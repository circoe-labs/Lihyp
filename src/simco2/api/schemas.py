"""Schémas d'entrée stricts. Décimaux obligatoirement transportés en textes."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from simco2.domain.units import ENERGY_UNITS, dec


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def require_decimal(value: str, *, positive: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError("Décimal attendu au format chaîne de caractères")
    d = dec(value)
    if (d <= 0 if positive else d < 0):
        raise ValueError("Montant négatif ou nul interdit")
    return str(d)


class EnergyInput(StrictInput):
    country_iso: Literal["FR"] = "FR"
    energy_code: Literal["DIESEL", "ELECTRIC", "H2"]
    unit: Literal["L", "kWh", "kg"]
    price_per_unit: str
    factors: dict[str, str] = Field(default_factory=dict)
    source: str = Field(min_length=5, max_length=500)
    source_date: date
    license: str = Field(default="À vérifier", min_length=3, max_length=150)
    quality: Literal["unverified"] = "unverified"  # pas de certif. self-service

    @field_validator("price_per_unit")
    @classmethod
    def parse_price(cls, value):
        return require_decimal(value)

    @field_validator("factors")
    @classmethod
    def parse_factors(cls, factors):
        if any(k not in {"direct", "well_to_wheel", "lifecycle"} for k in factors):
            raise ValueError("Périmètre carbone inconnu")
        return {key: require_decimal(value) for key, value in factors.items()}

    @model_validator(mode="after")
    def check_unit(self):
        target = {"DIESEL": "L", "ELECTRIC": "kWh", "H2": "kg"}
        if self.unit != target[self.energy_code]:
            raise ValueError("Unité incorrecte pour le type d'énergie")
        return self


class VehicleInput(StrictInput):
    label: str = Field(min_length=2, max_length=150)
    manufacturer: str = Field(min_length=1, max_length=150)
    model: str = Field(min_length=1, max_length=150)
    kind: Literal["bus", "van", "car"] = "bus"
    seats: int = Field(ge=1, le=150)
    energy_code: Literal["DIESEL", "ELECTRIC", "H2"]
    unit: Literal["L", "kWh", "kg"]
    consumption_per_km: str
    consumption_per_hour: str = "0"
    usable_capacity: str
    reserve: str = "0"
    maintenance_eur_per_km: str = "0"
    labor_eur_per_h: str = "0"
    purchase_eur: str = "0"
    residual_eur: str = "0"
    life_years: int = Field(default=10, ge=1, le=80)
    insurance_eur_year: str = "0"
    connectors: list[str] = Field(default_factory=list)
    height_m: str | None = None
    length_m: str | None = None
    width_m: str | None = None
    max_mass_t: str | None = None
    source: str = Field(min_length=5, max_length=500)
    quality: Literal["unverified"] = "unverified"

    @field_validator("consumption_per_km", "consumption_per_hour", "usable_capacity", "reserve",
                     "maintenance_eur_per_km", "labor_eur_per_h", "purchase_eur", "residual_eur",
                     "insurance_eur_year")
    @classmethod
    def parse_nonneg(cls, value):
        return require_decimal(value)

    @field_validator("height_m", "length_m", "width_m", "max_mass_t")
    @classmethod
    def parse_optional(cls, value):
        return None if value is None else require_decimal(value, positive=True)

    @model_validator(mode="after")
    def rules(self):
        units = {"DIESEL": "L", "ELECTRIC": "kWh", "H2": "kg"}
        if units[self.energy_code] != self.unit:
            raise ValueError("Unité énergie incompatible")
        if dec(self.reserve) > dec(self.usable_capacity):
            raise ValueError("Réserve supérieure au réservoir utilisable")
        if dec(self.residual_eur) > dec(self.purchase_eur):
            raise ValueError("Valeur résiduelle supérieure au prix d'achat")
        return self


class EquipmentInput(StrictInput):
    energy_code: Literal["DIESEL", "ELECTRIC", "H2"]
    connector: str = Field(min_length=1, max_length=100)
    ports: int = Field(ge=1, le=100)
    max_power_kw: str | None = None
    flow_per_min: str | None = None
    pressure_bar: str | None = None

    @field_validator("max_power_kw", "flow_per_min", "pressure_bar")
    @classmethod
    def parse_optional(cls, value):
        return None if value is None else require_decimal(value, positive=True)


class StationInput(StrictInput):
    name: str = Field(min_length=2, max_length=150)
    longitude: float = Field(ge=-2.1, le=2.6)
    latitude: float = Field(ge=48.0, le=50.5)
    access: Literal["public", "private", "restricted"]
    operational_status: Literal["unverified", "unavailable"] = "unverified"
    equipments: list[EquipmentInput] = Field(min_length=1)
    opening_hours: str = Field(default="unknown", max_length=250)
    source: str = Field(min_length=5)
    observed_at: date
    license: str = Field(default="À vérifier", min_length=3)
    confidence: Literal["unverified"] = "unverified"


class RouteInput(StrictInput):
    origin: str = Field(min_length=1, max_length=150)
    destination: str = Field(min_length=1, max_length=150)
    distance_m: int = Field(gt=0, le=10_000_000)
    duration_s: int = Field(gt=0, le=1_000_000)
    provider: Literal["manual", "openrouteservice", "osrm_demo", "osrm", "geoapify"] = "manual"
    source: str = Field(min_length=5, max_length=500)
    origin_coordinates: tuple[float, float] | None = None
    destination_coordinates: tuple[float, float] | None = None
    geometry: dict | None = None
    valid_at: str | None = None
    profile: str | None = None
    restrictions: list[str] = Field(default_factory=list)


class ScenarioInput(StrictInput):
    name: str = Field(min_length=2, max_length=200)
    country_iso: Literal["FR"] = "FR"
    start_date: date
    end_date: date
    timezone: str = "Europe/Paris"
    route: RouteInput | None = None
    route_quote_id: str | None = Field(default=None, max_length=60)
    passengers: int = Field(ge=0, le=1_000_000)
    window_start: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    window_end: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    max_vehicles: int = Field(ge=0, le=1000)
    vehicle_version_id: str
    energy_version_id: str
    tco_scope: Literal["variable", "vehicle", "complete"] = "variable"
    emission_scope: Literal["direct", "well_to_wheel", "lifecycle"] = "direct"
    infrastructure_daily_eur: str = "0"
    objective: Literal["cost", "co2e", "vehicles", "weighted"] = "cost"
    demand_mode: Literal["global", "calendar", "exact"] = "global"
    network_mode: Literal["single", "independent", "shared"] = "single"
    fleet_mode: Literal["single", "catalogue", "mixed"] = "single"
    depot_mode: Literal["none", "one", "multiple"] = "none"
    time_scope: Literal["rapid", "detailed", "regulatory"] = "rapid"
    consumption_scope: Literal["fixed", "contextual", "measured"] = "fixed"
    refuel_mode: Literal["no_refuel", "necessary", "imposed", "optimized"] = "no_refuel"
    charging_mode: Literal["no_charge", "simple", "technical", "shared"] = "no_charge"

    @field_validator("infrastructure_daily_eur")
    @classmethod
    def validate_cost(cls, value):
        return require_decimal(value)

    @model_validator(mode="after")
    def rules(self):
        if self.start_date > self.end_date:
            raise ValueError("Date de fin antérieure à la date de début")
        if (self.route is None) == (self.route_quote_id is None):
            raise ValueError("Fournir soit une route manuelle, soit un calcul routier, pas les deux")
        if self.route is not None and self.route.provider != "manual":
            raise ValueError("Les distances calculées exigent un devis serveur")
        if not self.vehicle_version_id or not self.energy_version_id:
            raise ValueError("Versions de référence requises")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Fuseau IANA inconnu") from exc
        return self


class LoginInput(StrictInput):
    username: str
    password: str


class RunInput(StrictInput):
    scenario_revision_id: str


class RoutePreviewInput(StrictInput):
    origin: tuple[float, float]
    destination: tuple[float, float]
    profile: Literal["driving-car", "driving-hgv"] = "driving-hgv"


class RouteResolveInput(StrictInput):
    origin: str = Field(min_length=2, max_length=150)
    destination: str = Field(min_length=2, max_length=150)
    profile: Literal["driving-car", "driving-hgv", "bus", "truck", "heavy_truck"] | None = None


class DayStationInput(StrictInput):
    """Indicative point selected by the user; not an access/availability certificate."""
    id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    longitude: float = Field(ge=-2.1, le=2.6)
    latitude: float = Field(ge=48.0, le=50.5)
    energy_codes: list[str] = Field(min_length=1, max_length=12)
    source: str = Field(min_length=5, max_length=500)

    @field_validator("energy_codes")
    @classmethod
    def known_codes(cls, values):
        if any(code not in {"DIESEL", "H2", "ELECTRIC", "SP95", "SP98", "E10", "Gazole"}
               for code in values):
            raise ValueError("Code de station inconnu")
        return ["DIESEL" if x == "Gazole" else x for x in values]


class ComparisonInput(StrictInput):
    """Même demande et même route pour plusieurs modèles séparés (pas flotte mixte)."""
    name: str = Field(min_length=2, max_length=200)
    route_quote_id: str = Field(min_length=1, max_length=60)
    vehicle_version_ids: list[str] = Field(min_length=2, max_length=8)
    country_iso: Literal["FR"] = "FR"
    start_date: date
    passengers: int = Field(ge=0, le=1_000_000)
    window_start: str = Field(default="08:00", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    window_end: str = Field(default="18:00", pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    max_vehicles: int = Field(default=10, ge=0, le=1000)
    tco_scope: Literal["variable", "vehicle", "complete"] = "variable"
    emission_scope: Literal["direct", "well_to_wheel"] = "direct"
    infrastructure_daily_eur: str = "0"
    day_plan: bool = False
    station_policy: Literal["automatic", "imposed", "none"] = "automatic"
    refuel_station: DayStationInput | None = None
    diesel_flow_l_per_min: str = "0"
    hydrogen_flow_kg_per_min: str = "0"
    handling_minutes: str = "0"

    @field_validator("diesel_flow_l_per_min", "hydrogen_flow_kg_per_min", "handling_minutes")
    @classmethod
    def rate(cls, value):
        parsed = require_decimal(value)
        if len(parsed) > 24 or dec(parsed) > Decimal("100000"):
            raise ValueError("Debit ou duree hors du perimetre du prototype")
        return parsed

    @field_validator("vehicle_version_ids")
    @classmethod
    def unique_vehicles(cls, items):
        if len(items) != len(set(items)) or any(not item for item in items):
            raise ValueError("Sélectionner des véhicules distincts")
        return items

    @field_validator("infrastructure_daily_eur")
    @classmethod
    def cost(cls, value):
        return require_decimal(value)


class RoutingConfigInput(StrictInput):
    provider: Literal["geoapify", "ors", "osrm_demo"]
    profile: Literal["bus", "truck", "heavy_truck", "driving-hgv", "driving-car"]


class RoutingKeyInput(StrictInput):
    provider: Literal["geoapify", "ors"]
    key: str = Field(min_length=8, max_length=300)
