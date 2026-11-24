"""Bounded, auditable station candidate routing for single-line day studies.

This is a *candidate search*, not a globally optimal station selector. Results
can be incomplete when an upstream directory or route provider is unavailable.
Coordinates are never substituted for routed detour distance/duration.
"""
from __future__ import annotations

from math import cos, hypot, radians

from simco2.domain.errors import RoutingFailure


def _coords(station):
    try:
        lon, lat = float(station["longitude"]), float(station["latitude"])
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            return (lon, lat)
    except (KeyError, TypeError, ValueError):
        pass
    return None


def _proximity(station, start, end):
    """Cheap candidate pruning only; never used as a routed travel time."""
    lon, lat = _coords(station)
    mid_lat = (start[1] + end[1]) / 2
    dx = cos(radians(mid_lat))
    return min(hypot((lon - start[0]) * dx, lat - start[1]),
               hypot((lon - end[0]) * dx, lat - end[1]))


def _valid_codes(station):
    return {"DIESEL" if x == "Gazole" else x for x in station.get("energy_codes", [])}


def route_candidates(provider, route_quote: dict, stations: list[dict],
                     energy_codes: set[str], *, max_per_energy: int = 4):
    """Return a bounded, provider-verified station shortlist and search warnings.

    No implicit fallback to straight-line distance. Duplicate coordinates or
    station identifiers are removed; an unusable station is never a solution.
    """
    start = route_quote.get("origin_coordinates")
    end = route_quote.get("destination_coordinates")
    profile = route_quote.get("profile")
    if not start or not end:
        return {}, ["Recherche de stations impossible : coordonnées du trajet absentes."]
    start, end = tuple(start), tuple(end)
    options: dict[str, list[dict]] = {}
    warnings = []
    for energy in sorted(energy_codes.intersection({"DIESEL", "H2"})):
        pool = [s for s in stations if _coords(s) is not None and energy in _valid_codes(s)]
        pool.sort(key=lambda s: (_proximity(s, start, end), str(s.get("id", ""))))
        seen = set()
        candidates = []
        for station in pool:
            key = str(station.get("id") or "")
            if not key or key in seen:
                continue
            seen.add(key)
            candidates.append(station)
            if len(candidates) >= max_per_energy:
                break
        if len(pool) > len(candidates):
            warnings.append(f"{energy}: présélection géographique limitée à {max_per_energy} stations; optimum global non prouvé.")
        routed = []
        for station in candidates:
            point = _coords(station)
            try:
                def leg(a, b, description):
                    r = provider.route(a, b, profile)
                    if (r.provider != route_quote.get("provider") or r.profile != profile or
                            r.distance_m <= 0 or r.duration_s <= 0):
                        raise RoutingFailure("station_route_mismatch", "Routage station incompatible")
                    return {"label": description, "distance_m": str(r.distance_m),
                            "duration_s": str(r.duration_s), "provider": r.provider,
                            "profile": r.profile, "valid_at": r.valid_at,
                            "restrictions": list(r.restrictions)}
                to = leg(end, point, "vers la station")
                back = leg(point, start, "retour à la ligne")
            except (RoutingFailure, ValueError, TypeError, KeyError):
                warnings.append(f"Station {station.get('id', 'inconnue')}: détour routier indisponible, station écartée.")
                continue
            routed.append({"station": {"id": str(station["id"]),
                        "name": str(station.get("name") or station["id"]),
                        "source": str(station.get("source", "")),
                        "longitude": point[0], "latitude": point[1],
                        "energy_codes": sorted(_valid_codes(station)),
                        "bus_compatibility": "not_confirmed"},
                        "to_station": to, "from_station": back})
        options[energy] = routed
        if not routed:
            warnings.append(f"{energy}: aucune station compatible avec détour routé disponible dans l'échantillon.")
    return options, warnings
