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
