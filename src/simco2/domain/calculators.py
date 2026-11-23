"""Calculs purs : energie, TCO et CO2e. Aucun chiffre national integre."""
from __future__ import annotations

from decimal import Decimal
from collections.abc import Mapping
from .errors import DomainError, MissingReference
from .units import dec


def energy_fixed(distance_m: int | Decimal, duration_s: int | Decimal,
                 per_km: str | Decimal, per_hour: str | Decimal) -> Decimal:
    """Une seule comptabilisation des auxiliaires temporels sur temps de roulage."""
    d, s = dec(distance_m), dec(duration_s)
    k, h = dec(per_km), dec(per_hour)
    if min(d, s, k, h) < 0:
        raise DomainError("negative_quantity", "Données négatives interdites")
    return d / Decimal(1000) * k + s / Decimal(3600) * h


def allocate_by_service_hours(total: Decimal, hours: Mapping[str, Decimal]) -> dict[str, Decimal]:
    """Cout reparti exactement une fois, solde affecte a la derniere ligne."""
    total = dec(total)
    if total < 0 or not hours or any(dec(v) < 0 for v in hours.values()):
        raise DomainError("invalid_allocation", "Montant ou heures non admissibles")
    all_hours = sum((dec(v) for v in hours.values()), Decimal(0))
    if all_hours == 0:
        raise DomainError("invalid_allocation", "Heures de service nulles")
    out = {}
    remaining = total
    keys = list(sorted(hours))
    for key in keys[:-1]:
        allocation = total * dec(hours[key]) / all_hours
        out[key] = allocation
        remaining -= allocation
    out[keys[-1]] = remaining
    return out


def cost_breakdown(*, energy_quantity: Decimal, price_per_unit: str,
                   distance_m: Decimal, duration_s: Decimal,
                   vehicle_count: int, days: int, vehicle: dict,
                   scope: str, infrastructure_daily_eur: str = "0") -> dict[str, Decimal]:
    """Variable / véhicule / complet ; immobilisations par véhicule utilisé."""
    if scope not in {"variable", "vehicle", "complete"}:
        raise DomainError("invalid_tco_scope", "Périmètre TCO non reconnu")
    if vehicle_count < 0 or days < 1:
        raise DomainError("invalid_tco_input", "Durée ou parc négatif")
    if any(dec(x) < 0 for x in (energy_quantity, distance_m, duration_s)):
        raise DomainError("negative_quantity", "Quantité négative")
    energy = energy_quantity * dec(price_per_unit)
    maintenance = distance_m / Decimal(1000) * dec(vehicle["maintenance_eur_per_km"])
    vehicle_fixed = Decimal(0)
    labor = Decimal(0)
    infrastructure = Decimal(0)
    if scope in {"vehicle", "complete"}:
        depreciation = ((dec(vehicle["purchase_eur"]) - dec(vehicle["residual_eur"])) /
                        dec(vehicle["life_years"]))
        insurance = dec(vehicle["insurance_eur_year"])
        vehicle_fixed = (depreciation + insurance) * Decimal(days) / Decimal(365) * vehicle_count
    if scope == "complete":
        labor = duration_s / Decimal(3600) * dec(vehicle["labor_eur_per_h"])
        infrastructure = dec(infrastructure_daily_eur) * days
    out = dict(energy_eur=energy, maintenance_eur=maintenance,
               vehicle_fixed_eur=vehicle_fixed, labor_eur=labor,
               infrastructure_eur=infrastructure)
    if min(out.values()) < 0:
        raise DomainError("negative_cost", "Coûts non négatifs attendus")
    out["total_eur"] = sum(out.values(), Decimal(0))
    return out


def emissions(*, energy_quantity: Decimal, factors: Mapping[str, str],
              perimeter: str) -> Decimal:
    if perimeter == "lifecycle":
        raise DomainError("unsupported_acv", "ACV non active : allocation fabrication/infrastructure non validée")
    if perimeter not in {"direct", "well_to_wheel"}:
        raise DomainError("invalid_co2e_scope", "Périmètre carbone inconnu")
    if perimeter not in factors or factors[perimeter] in (None, ""):
        raise MissingReference(f"Facteur CO2e absent pour {perimeter}")
    qty, factor = dec(energy_quantity), dec(factors[perimeter])
    if qty < 0 or factor < 0:
        raise DomainError("negative_quantity", "Facteur ou quantité négatif")
    # 'well_to_wheel' inclut deja le direct; aucune addition.
    return qty * factor


def safe_ratio(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    denominator = dec(denominator)
    return None if denominator == 0 else dec(numerator) / denominator
