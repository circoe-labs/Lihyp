"""Configuration locale du routage : secrets côté serveur, jamais renvoyés au navigateur.

La modification via HTTP est limitée à l'opérateur sur l'interface loopback.
En déploiement, fournir les clés via variables d'environnement ou un gestionnaire
externe de secrets; ne pas compter sur ce fichier local comme coffre-fort.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from threading import RLock

from simco2.adapters.routing import GeoapifyRoutingProvider, ORSRoutingProvider, OSRMRoutingProvider
from simco2.domain.errors import RoutingFailure

PROFILE_OPTIONS = {
    "geoapify": ("bus", "truck", "heavy_truck"),
    "ors": ("driving-hgv", "driving-car"),
    "osrm_demo": ("driving-car",),
    "osrm": ("driving-car",),
    "disabled": (),
}
ENDPOINTS = {
    "geoapify": GeoapifyRoutingProvider.API_URL,
    "ors": ORSRoutingProvider.API_URL,
    "osrm_demo": OSRMRoutingProvider.DEFAULT_URL,
    "osrm": "Endpoint OSRM défini par l'exploitant",
    "disabled": "—",
}


class RoutingSettings:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or os.getenv("SIMCO2_ROUTING_SETTINGS_PATH") or
                         (Path.home() / ".simco2" / "routing-settings.json"))
        self._lock = RLock()

    def _read(self) -> dict:
        if not self.path.is_file():
            return {}
        try:
            obj = json.loads(self.path.read_text(encoding="utf-8"))
            return obj if isinstance(obj, dict) else {}
        except (OSError, ValueError):
            raise RoutingFailure("settings_error", "Configuration de routage locale illisible") from None

    def _write(self, data: dict):
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Fichier temporaire dans le même répertoire pour remplacement atomique.
        fd, filename = tempfile.mkstemp(prefix="routing-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            os.chmod(filename, 0o600)
            os.replace(filename, self.path)
            os.chmod(self.path, 0o600)
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def key_for(self, provider: str) -> str:
        env = "SIMCO2_GEOAPIFY_API_KEY" if provider == "geoapify" else "ORS_API_KEY"
        return os.getenv(env, "") or str(self._read().get("keys", {}).get(provider, ""))

    def selected(self) -> tuple[str, str]:
        data = self._read()
        force = os.getenv("SIMCO2_ROUTING_MODE")
        provider = force or data.get("provider")
        if not provider:
            provider = "geoapify" if self.key_for("geoapify") else (
                "ors" if self.key_for("ors") else "osrm_demo")
        if provider == "demo":
            provider = "osrm_demo"
        if provider not in PROFILE_OPTIONS:
            provider = "disabled"
        profile = data.get("profile") if not force else None
        if profile not in PROFILE_OPTIONS[provider]:
            profile = PROFILE_OPTIONS[provider][0] if PROFILE_OPTIONS[provider] else ""
        return provider, profile

    def status(self, *, operator: bool = False) -> dict:
        with self._lock:
            provider, profile = self.selected()
            configured = {key: bool(self.key_for(key)) for key in ("geoapify", "ors")}
            available = provider in ("osrm", "osrm_demo") or (provider in configured and configured[provider])
            if provider == "osrm" and not os.getenv("SIMCO2_OSRM_URL"):
                available = False
            return {
                "provider": provider, "profile": profile,
                "endpoint": (os.getenv("SIMCO2_OSRM_URL") or ENDPOINTS[provider]) if provider == "osrm" else ENDPOINTS[provider],
                "available": bool(available), "configured": configured,
                "profiles": list(PROFILE_OPTIONS[provider]),
                "modifiable": bool(operator) and not bool(os.getenv("SIMCO2_ROUTING_MODE")),
                "operator": operator,
                "notes": "Routage estimatif : profil bus/camion ne vaut pas certification des restrictions réelles.",
            }

    def select(self, provider: str, profile: str):
        if provider not in PROFILE_OPTIONS or profile not in PROFILE_OPTIONS[provider]:
            raise RoutingFailure("unsupported_profile", "Profil de routage non disponible")
        with self._lock:
            data = self._read()
            data["provider"], data["profile"] = provider, profile
            self._write(data)

    def put_key(self, provider: str, secret: str):
        if provider not in ("geoapify", "ors") or not secret or len(secret) > 300:
            raise RoutingFailure("invalid_key", "Clé ou fournisseur invalide")
        with self._lock:
            data = self._read()
            data.setdefault("keys", {})[provider] = secret
            # On choisit le fournisseur lors de son premier ajout seulement.
            if "provider" not in data:
                data["provider"] = provider
                data["profile"] = PROFILE_OPTIONS[provider][0]
            self._write(data)

    def remove_key(self, provider: str):
        if provider not in ("geoapify", "ors"):
            raise RoutingFailure("unsupported_provider", "Fournisseur inconnu")
        with self._lock:
            data = self._read()
            data.setdefault("keys", {}).pop(provider, None)
            self._write(data)

    def provider(self):
        with self._lock:
            provider, profile = self.selected()
            if provider == "geoapify":
                key = self.key_for("geoapify")
                return GeoapifyRoutingProvider(key) if key else None
            if provider == "ors":
                key = self.key_for("ors")
                return ORSRoutingProvider(key) if key else None
            if provider == "osrm_demo":
                return OSRMRoutingProvider()
            if provider == "osrm" and os.getenv("SIMCO2_OSRM_URL"):
                return OSRMRoutingProvider(os.environ["SIMCO2_OSRM_URL"])
            return None
