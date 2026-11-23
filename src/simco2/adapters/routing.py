"""Routage contrôlé : offline strict, ORS optionnel, jamais de distance de secours inventée."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Mapping

import httpx
from simco2.domain.contracts import RouteResult
from simco2.domain.errors import RoutingFailure


class FixtureRoutingProvider:
    def __init__(self, routes: Mapping[tuple, tuple[int, int]]):
        self.routes = dict(routes)

    def route(self, origin, destination, profile, departure_time=None):
        key = (tuple(origin), tuple(destination), profile)
        if key not in self.routes:
            raise RoutingFailure("route_not_found", "Aucune route de fixture déclarée")
        length, duration = self.routes[key]
        return RouteResult(Decimal(length), Decimal(duration), profile, "fixture_test_only",
                           "1", "2026-01-01T00:00:00+00:00")


class ORSRoutingProvider:
    API_URL = "https://api.openrouteservice.org/v2/directions"

    def __init__(self, api_key: str, *, client: httpx.Client | None = None):
        if not api_key:
            raise RoutingFailure("provider_unconfigured", "Clé ORS absente sur serveur")
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=12)

    def route(self, origin, destination, profile, departure_time=None):
        if profile not in ("driving-car", "driving-hgv"):
            raise RoutingFailure("unsupported_profile", "Profil routage non supporté")
        for lon, lat in (origin, destination):
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise RoutingFailure("invalid_coordinates", "Coordonnées hors bornes")
        try:
            response = self.client.post(
                f"{self.API_URL}/{profile}/geojson",
                headers={"Authorization": self.api_key, "Content-Type": "application/json"},
                json={"coordinates": [list(origin), list(destination)]},
            )
            response.raise_for_status()
            body = response.json()
            feature = body["features"][0]
            summary = feature["properties"]["summary"]
            distance, duration = Decimal(str(summary["distance"])), Decimal(str(summary["duration"]))
            if distance <= 0 or duration <= 0:
                raise ValueError("empty route")
            return RouteResult(distance, duration, profile, "openrouteservice",
                               str(body.get("metadata", {}).get("engine", {}).get("version", "unknown")),
                               datetime.now(timezone.utc).isoformat(),
                               geometry=feature.get("geometry"),
                               restrictions=("Profils ORS ne certifient pas tous les accès autocar.",))
        except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError) as err:
            # Ne pas logguer response ou URL contenant secret ; diagnostics typés.
            raise RoutingFailure("provider_error", "Route ORS indisponible ou réponse invalide") from None


class GeoplatformGeocoder:
    """Géocodage des lieux français via la Géoplateforme (IGN / BAN)."""
    API_URL = "https://data.geopf.fr/geocodage/search"

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(timeout=12, follow_redirects=False)

    def locate(self, place: str) -> tuple[tuple[float, float], str]:
        if not isinstance(place, str) or not 2 <= len(place.strip()) <= 150:
            raise RoutingFailure("invalid_place", "Saisir un lieu de 2 à 150 caractères")
        try:
            response = self.client.get(self.API_URL, params={"q": place.strip(), "limit": 5})
            response.raise_for_status()
            features = response.json().get("features", [])
            if not features:
                raise RoutingFailure("place_not_found", "Lieu introuvable dans le géocodeur IGN")
            # Pour la saisie « Caen », préférer la commune à une rue homonyme.
            query = place.strip().casefold()
            preferred = next((f for f in features if
                             str(f.get("properties", {}).get("city", "")).casefold() == query
                             or str(f.get("properties", {}).get("name", "")).casefold() == query),
                             features[0])
            lon, lat = preferred["geometry"]["coordinates"][:2]
            lon, lat = float(lon), float(lat)
            if not (-5.5 <= lon <= 10 and 41 <= lat <= 52):
                raise ValueError("Place outside France")
            label = str(preferred.get("properties", {}).get("label") or place)
            return (lon, lat), label[:180]
        except RoutingFailure:
            raise
        except (httpx.HTTPError, KeyError, ValueError, IndexError, TypeError):
            raise RoutingFailure("geocoding_unavailable", "Géocodage IGN indisponible ou réponse invalide") from None


class OSRMRoutingProvider:
    """Calcul routier OSRM ; endpoint de démonstration jamais garanti en production."""
    DEFAULT_URL = "https://router.project-osrm.org/route/v1/driving"

    def __init__(self, base_url: str | None = None, *, client: httpx.Client | None = None):
        self.base_url = (base_url or self.DEFAULT_URL).rstrip("/")
        self.is_demo = self.base_url == self.DEFAULT_URL
        self.client = client or httpx.Client(timeout=15, follow_redirects=False)

    def route(self, origin, destination, profile="driving-car", departure_time=None):
        if profile not in ("driving-car", "driving-hgv"):
            raise RoutingFailure("unsupported_profile", "Profil routage non supporté")
        if profile == "driving-hgv" and self.is_demo:
            # Le profil du serveur de démonstration OSRM est générique (voiture).
            # On ne doit pas promettre que les contraintes de gabarit sont appliquées.
            pass
        for lon, lat in (origin, destination):
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise RoutingFailure("invalid_coordinates", "Coordonnées hors bornes")
        coords = ";".join(f"{lon:.7f},{lat:.7f}" for lon, lat in (origin, destination))
        try:
            response = self.client.get(
                f"{self.base_url}/{coords}",
                params={"overview": "full", "geometries": "geojson", "steps": "false"},
            )
            response.raise_for_status()
            route = response.json()["routes"][0]
            distance, duration = Decimal(str(route["distance"])), Decimal(str(route["duration"]))
            geometry = route["geometry"]
            if distance <= 0 or duration <= 0 or geometry.get("type") != "LineString":
                raise ValueError("invalid route")
            provider = "osrm_demo" if self.is_demo else "osrm"
            restrictions = (
                "Tracé de démonstration OSRM : profil voiture, sans garantie de gabarit autocar ni disponibilité.",
            ) if self.is_demo else (
                "Routage OSRM : vérifier les restrictions et la compatibilité autocar.",
            )
            return RouteResult(distance, duration, profile, provider, "osrm-v1",
                               datetime.now(timezone.utc).isoformat(),
                               geometry=geometry, restrictions=restrictions)
        except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError, AttributeError):
            raise RoutingFailure("provider_error", "Itinéraire indisponible : vérifier le service de routage") from None


class GeoapifyRoutingProvider:
    """Routage Geoapify bus/camion. Réponse GeoJSON normalisée en LineString."""
    API_URL = "https://api.geoapify.com/v1/routing"
    SUPPORTED = ("bus", "truck", "heavy_truck")

    def __init__(self, api_key: str, *, client: httpx.Client | None = None):
        if not api_key:
            raise RoutingFailure("provider_unconfigured", "Clé Geoapify absente côté serveur")
        self.api_key = api_key
        self.client = client or httpx.Client(timeout=15, follow_redirects=False)

    def route(self, origin, destination, profile="bus", departure_time=None):
        if profile not in self.SUPPORTED:
            raise RoutingFailure("unsupported_profile", "Profil Geoapify non pris en charge")
        for lon, lat in (origin, destination):
            if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                raise RoutingFailure("invalid_coordinates", "Coordonnées hors bornes")
        try:
            response = self.client.get(self.API_URL, params={
                "waypoints": "|".join(f"{lat:.7f},{lon:.7f}" for lon, lat in (origin, destination)),
                "mode": profile, "format": "geojson", "apiKey": self.api_key,
            })
            response.raise_for_status()
            feature = response.json()["features"][0]
            props = feature["properties"]
            distance, duration = Decimal(str(props["distance"])), Decimal(str(props["time"]))
            geometry = feature["geometry"]
            if geometry["type"] == "MultiLineString":
                segments = geometry["coordinates"]
                coords = []
                for line in segments:
                    coords.extend(line if not coords or coords[-1] != line[0] else line[1:])
                geometry = {"type": "LineString", "coordinates": coords}
            if (distance <= 0 or duration <= 0 or geometry["type"] != "LineString"
                    or len(geometry["coordinates"]) < 2
                    or len(geometry["coordinates"]) > 15000):
                raise ValueError("invalid route")
            return RouteResult(distance, duration, profile, "geoapify", "routing-v1",
                               datetime.now(timezone.utc).isoformat(), geometry=geometry,
                               restrictions=(
                                   "Profil Geoapify indicatif : restrictions bus/camion non garanties partout.",
                               ))
        except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError, AttributeError):
            # Ne jamais inclure l'URL avec apiKey dans les erreurs renvoyées.
            raise RoutingFailure("provider_error", "Routage Geoapify indisponible ou réponse invalide") from None
