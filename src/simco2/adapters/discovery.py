"""Répertoire de stations en Normandie : H2 sourcé + flux officiel DGCCRF.

Ce répertoire est INFORMATIF. Il ne garantit ni accès aux autocars ni
fonctionnement temps réel et ne contribue pas au solveur de ravitaillement.
Aucun prix par station n'est exposé ou introduit dans les calculs (Q19).
"""
from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from time import monotonic

import httpx

H2_SOURCE = "https://www.h2-mobile.fr/stations-hydrogene/region-normandie/"
H2_GEO_SOURCE = "https://www.h2-mobile.fr/json/json-stations-h2.php"
FUEL_SOURCE = (
    "https://data.economie.gouv.fr/explore/dataset/"
    "prix-des-carburants-en-france-flux-instantane-v2/"
)
FUEL_API = (
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "prix-des-carburants-en-france-flux-instantane-v2/records"
)


def h2_station(city: str, address: str, lon: float, lat: float,
               pressure: str, detail: str) -> dict:
    return {
        "id": "h2-" + city.lower().replace(" ", "-"), "name": f"H₂ · {city}",
        "city": city, "address": address, "longitude": lon, "latitude": lat,
        "energy_codes": ["H2"], "category": "hydrogen", "pressure_bar": pressure,
        "access_reported": "public", "operational_status": "listed_open_unverified",
        "bus_compatibility": "not_confirmed", "vehicle_types_reported": ["light", "utility"],
        "source": f"https://www.h2-mobile.fr/stations-hydrogene/{detail}/",
        "coordinates_source": H2_GEO_SOURCE, "license": "Conditions de réutilisation à vérifier",
        "notice": "Station référencée, disponibilité et compatibilité autocars non confirmées",
    }


# Coordonnées reprises du GeoJSON public de h2-mobile, vérifiées pour la Normandie.
# Pressions et adresses issues des fiches de chaque station, non de mesures terrain.
NORMANDY_H2 = (
    h2_station("Rouen", "Place du Boulingrin, 76100 Rouen, France", 1.1062708,
               49.4469257, "350", "station-hydrogene-engie-76100-rouen"),
    h2_station("Bretteville-sur-Odon", "Rue Jules Védrine, 14760 Bretteville-sur-Odon, France",
               -0.432871, 49.175333, "350", "station-hydrogene-bretteville-sur-odon"),
    h2_station("Pont-l'Évêque", "Rue Georges Clemenceau, 14130 Pont-l'Évêque, France",
               0.197782, 49.287721, "350", "station-hydrogene-14130-pont-eveque"),
    h2_station("Val-de-Reuil", "Avenue des Métiers, 27100 Val-de-Reuil, France",
               1.175825, 49.25321, "350", "station-hydrogene-27100-val-de-reuil"),
    h2_station("Douains", "Avenue du Capitaine de Vandières, 27120 Douains, France",
               1.425762, 49.065525, "350", "station-hydrogene-douains-27120"),
    h2_station("Le Vieil-Évreux", "Rue Maryse Bastié, 27930 Le Vieil-Évreux, France",
               1.182344, 49.009496, "350 / 700", "station-hydrogene-vieil-evreux"),
    h2_station("Lillebonne", "Rue de Bossaye, 76170 Lillebonne, France",
               0.531731, 49.515098, "350", "station-hydrogene-76170-lillebonne"),
)


def _coordinate(value):
    """DGCCRF diffuse latitude / longitude en cent-millièmes de degré."""
    if isinstance(value, bool) or value is None:
        raise ValueError("missing coordinate")
    number = float(value)
    return number / 100000 if abs(number) > 180 else number


def normalize_fuel_station(record: dict) -> dict | None:
    """Ne pas laisser une station hors Normandie fuiter depuis une réponse externe."""
    if record.get("code_departement") not in {"14", "27", "50", "61", "76"}:
        return None
    try:
        lat = _coordinate(record["latitude"])
        lon = _coordinate(record["longitude"])
    except (KeyError, ValueError, TypeError):
        return None
    if not (48.1 <= lat <= 50.2 and -2.0 <= lon <= 2.1):
        return None
    fuels = record.get("carburants_disponibles")
    if not isinstance(fuels, list):
        fuels = []
    # Les prix par point de vente ne sont *jamais* retournés (Q19).
    fuels = [str(f) for f in fuels if str(f) in
             {"Gazole", "SP95", "SP98", "E10", "E85", "GPLc"}]
    address = ", ".join(str(x) for x in (
        record.get("adresse"), record.get("cp"), record.get("ville")) if x)
    name = str(record.get("ville") or "Station-service")
    return {
        "id": f"fuel-{record.get('id')}", "name": f"Station-service · {name}",
        "city": name, "address": address + ", France", "longitude": lon,
        "latitude": lat, "category": "fuel", "energy_codes": fuels,
        "access_reported": "published", "operational_status": "listed_unverified",
        "bus_compatibility": "not_confirmed",
        "heavy_vehicle_lane_reported": "Piste poids lourds" in (
            record.get("services_service") or []),
        "source": FUEL_SOURCE, "license": "Licence Ouverte v2.0 (Etalab)",
        "notice": "Référencé par la DGCCRF ; horaires et accès autocar à vérifier",
    }


class FuelStationDirectory:
    """Pagination serveur et cache court, sans tarifs individuels exposés."""
    def __init__(self, client: httpx.Client | None = None, cache_seconds: int = 900):
        self.client = client or httpx.Client(timeout=12, follow_redirects=False)
        self.cache_seconds = cache_seconds
        self._cache: dict[tuple[int, int], tuple[float, dict]] = {}
        self._lock = Lock()

    def page(self, offset: int = 0, limit: int = 100) -> dict:
        if offset < 0 or offset > 10000 or not 1 <= limit <= 100:
            raise ValueError("Invalid pagination")
        key = offset, limit
        with self._lock:
            cached = self._cache.get(key)
            if cached and cached[0] > monotonic():
                return cached[1]
        result = {
            "stations": [], "total": 0, "offset": offset, "limit": limit,
            "has_more": False, "source": FUEL_SOURCE,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "unavailable": False,
        }
        try:
            response = self.client.get(FUEL_API, params={
                "where": 'region="Normandie"', "limit": limit, "offset": offset,
                "order_by": "id",
            })
            response.raise_for_status()
            body = response.json()
            rows = body["results"]
            if not isinstance(rows, list):
                raise ValueError("Invalid station payload")
            result["stations"] = [item for row in rows
                                  if (item := normalize_fuel_station(row)) is not None]
            result["total"] = int(body.get("total_count", 0))
            result["has_more"] = offset + limit < result["total"]
        except (httpx.HTTPError, KeyError, ValueError, TypeError):
            # Une panne de source externe ne doit ni effacer le répertoire H2 ni
            # exposer le corps brut de réponse à un utilisateur.
            result["unavailable"] = True
        with self._lock:
            self._cache[key] = monotonic() + (60 if result["unavailable"] else self.cache_seconds), result
        return result
