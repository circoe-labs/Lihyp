"""Arithmétique d'unités, argent et instants locaux sans nombres binaires."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .errors import DomainError


UNITS = {"m", "km", "s", "h", "L", "kWh", "kg", "Nm3", "kgCO2e", "EUR"}
CONVERSIONS = {("m", "km"): Decimal("0.001"), ("km", "m"): Decimal("1000"),
               ("s", "h"): Decimal(1) / Decimal(3600),
               ("h", "s"): Decimal(3600)}


def dec(value: str | int | Decimal) -> Decimal:
    if isinstance(value, float):
        raise DomainError("invalid_decimal", "Utiliser une chaîne décimale, pas float")
    try:
        x = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise DomainError("invalid_decimal", f"Valeur décimale invalide : {value}") from None
    if not x.is_finite():
        raise DomainError("invalid_decimal", "NaN et Inf interdits")
    return x


@dataclass(frozen=True)
class Quantity:
    value: Decimal
    unit: str

    def __post_init__(self):
        object.__setattr__(self, "value", dec(self.value))
        if self.unit not in UNITS:
            raise DomainError("unknown_unit", f"Unité non reconnue : {self.unit}")

    def __add__(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity) or self.unit != other.unit:
            raise DomainError("unit_mismatch", "Addition d'unités incompatibles")
        return Quantity(self.value + other.value, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity) or self.unit != other.unit:
            raise DomainError("unit_mismatch", "Soustraction d'unités incompatibles")
        return Quantity(self.value - other.value, self.unit)

    def convert(self, unit: str) -> "Quantity":
        if unit == self.unit:
            return self
        f = CONVERSIONS.get((self.unit, unit))
        if f is None:
            raise DomainError("conversion_required", f"Pas de conversion {self.unit} -> {unit}")
        return Quantity(self.value * f, unit)

    def to_json(self) -> dict:
        return {"value": str(self.value), "unit": self.unit}

    @classmethod
    def from_json(cls, data: dict) -> "Quantity":
        return cls(dec(data["value"]), data["unit"])


@dataclass(frozen=True)
class Money:
    value: Decimal
    currency: str = "EUR"

    def __post_init__(self):
        object.__setattr__(self, "value", dec(self.value))
        if self.currency != "EUR":
            raise DomainError("unsupported_currency", "Seul EUR est pris en charge")

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money) or other.currency != self.currency:
            raise DomainError("currency_mismatch", "Devises incompatibles")
        return Money(self.value + other.value, self.currency)

    def to_json(self) -> dict:
        return {"value": str(self.value), "currency": self.currency}


ENERGY_UNITS = {"L", "kWh", "kg", "Nm3"}


def local_to_utc(local_iso: str, tz_name: str, *, fold: int | None = None) -> datetime:
    """Rejette les heures inexistantes/ambiguës sauf choix explicite de fold."""
    try:
        d = datetime.fromisoformat(local_iso)
        zone = ZoneInfo(tz_name)
    except (ValueError, ZoneInfoNotFoundError) as e:
        raise DomainError("invalid_datetime", str(e)) from e
    if d.tzinfo is not None:
        raise DomainError("invalid_datetime", "Heure locale attendue sans décalage UTC")
    if fold not in (None, 0, 1):
        raise DomainError("invalid_fold", "fold attendu 0 ou 1")
    possibilities = []
    for choice in (0, 1):
        aware = d.replace(tzinfo=zone, fold=choice)
        utc = aware.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) == d:
            possibilities.append(utc)
    distinct = set(possibilities)
    if not distinct:
        raise DomainError("nonexistent_local_time", "Heure locale inexistante (transition DST)")
    if len(distinct) > 1 and fold is None:
        raise DomainError("ambiguous_local_time", "Heure locale ambiguë : préciser fold")
    chosen = 0 if fold is None else fold
    return d.replace(tzinfo=zone, fold=chosen).astimezone(timezone.utc)
