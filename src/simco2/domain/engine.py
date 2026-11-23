"""Planning minimal exact dans le sous-modèle mono-ligne sans repositionnement.

Chaque course orientée dispose de son propre véhicule initialement à l'origine.
Le résultat ne prétend pas optimiser ni prendre en charge le réseau complet.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from math import ceil

from .calculators import energy_fixed, cost_breakdown, emissions, safe_ratio
from .contracts import SolveResult, SolveStatus
from .errors import DomainError
from .units import dec, local_to_utc


def stringify(x):
    if isinstance(x, Decimal):
        return str(x)
    if isinstance(x, dict):
        return {k: stringify(v) for k, v in x.items()}
    if isinstance(x, list):
        return [stringify(v) for v in x]
    if isinstance(x, tuple):
        return [stringify(v) for v in x]
    return x


def _failure(status: SolveStatus, code: str, message: str, *, unserved=0) -> SolveResult:
    return SolveResult(status=status,
                       result={"status": status.value, "constraints": [{"code": code, "message": message}],
                               "unserved_passengers": unserved, "trips": [], "totals": None},
                       violations=(message,))


class BaselineEngine:
    ENGINE_VERSION = "baseline-orientee-v0.1"

    def solve(self, snapshot: dict) -> SolveResult:
        try:
            return self._solve(snapshot)
        except (DomainError, ValueError, KeyError, TypeError) as err:
            if isinstance(err, DomainError):
                code, message = err.code, err.message
            else:
                code, message = "invalid_input", "Snapshot incomplet ou invalide"
            return _failure(SolveStatus.INVALID_INPUT, code, message)

    def _solve(self, snapshot: dict) -> SolveResult:
        scenario = snapshot["scenario"]
        vehicle = snapshot["vehicle_version"]["payload"]
        energy = snapshot["energy_version"]["payload"]
        unsupported = []
        for name, expected in (("network_mode", "single"), ("fleet_mode", "single"),
                               ("depot_mode", "none"), ("demand_mode", "global"),
                               ("time_scope", "rapid"), ("consumption_scope", "fixed")):
            if scenario.get(name) != expected:
                unsupported.append(f"{name}={scenario.get(name)} (attendu {expected})")
        if scenario.get("start_date") != scenario.get("end_date"):
            unsupported.append("période > 1 jour")
        if scenario.get("refuel_mode") != "no_refuel":
            unsupported.append("ravitaillement (moteur de stations non encore disponible)")
        if scenario.get("charging_mode") != "no_charge":
            unsupported.append("recharge (moteur de bornes non encore disponible)")
        if unsupported:
            raise DomainError("unsupported_modes", "Modes non implémentés : " + "; ".join(unsupported))
        if vehicle["energy_code"] != energy["energy_code"] or vehicle["unit"] != energy["unit"]:
            raise DomainError("energy_mismatch", "Energie / unite du vehicule et du pays incompatibles")
        if scenario["country_iso"] != energy["country_iso"]:
            raise DomainError("country_mismatch", "Version tarif d'un autre pays")
        if energy.get("price_per_unit") is None:
            raise DomainError("missing_price", "Tarif national absent")
        route = scenario["route"]
        distance_m = dec(route["distance_m"])
        duration_s = dec(route["duration_s"])
        if distance_m <= 0 or duration_s <= 0:
            raise DomainError("invalid_route", "Distance et durée de route strictement positives")
        start = local_to_utc(f"{scenario['start_date']}T{scenario['window_start']}:00",
                             scenario["timezone"])
        end = local_to_utc(f"{scenario['end_date']}T{scenario['window_end']}:00",
                           scenario["timezone"])
        if end <= start:
            raise DomainError("invalid_window", "Amplitude de départ non positive")
        seats = int(vehicle["seats"])
        total_passengers = int(scenario["passengers"])
        max_vehicles = int(scenario["max_vehicles"])
        if seats <= 0 or total_passengers < 0 or max_vehicles < 0:
            raise DomainError("invalid_capacity", "Places, demande ou flotte incohérentes")
        trip_count = ceil(total_passengers / seats)
        if trip_count > max_vehicles:
            unserved = max(0, total_passengers - seats * max_vehicles)
            return _failure(SolveStatus.INFEASIBLE_PROVEN, "insufficient_fleet",
                            f"{trip_count} véhicules requis pour {total_passengers} passagers, parc limité à {max_vehicles}",
                            unserved=unserved)
        per_trip_energy = energy_fixed(distance_m, duration_s,
                                       vehicle["consumption_per_km"],
                                       vehicle["consumption_per_hour"])
        capacity = dec(vehicle["usable_capacity"])
        reserve = dec(vehicle["reserve"])
        if per_trip_energy > capacity - reserve:
            return _failure(SolveStatus.INFEASIBLE_PROVEN, "insufficient_energy_no_refuel",
                            "Energie disponible insuffisante sans ravitaillement/recharge",
                            unserved=total_passengers)
        total_energy = per_trip_energy * trip_count
        total_distance = distance_m * trip_count
        total_duration = duration_s * trip_count
        cost = cost_breakdown(energy_quantity=total_energy,
                              price_per_unit=energy["price_per_unit"],
                              distance_m=total_distance, duration_s=total_duration,
                              vehicle_count=trip_count, days=1, vehicle=vehicle,
                              scope=scenario["tco_scope"],
                              infrastructure_daily_eur=scenario.get("infrastructure_daily_eur", "0"))
        total_co2e = emissions(energy_quantity=total_energy,
                               factors=energy.get("factors", {}),
                               perimeter=scenario["emission_scope"])
        trip_rows = []
        remaining = total_passengers
        for i in range(trip_count):
            pax = min(seats, remaining)
            remaining -= pax
            # L'heure de depart est declarative et appartient a l'amplitude.
            # Aucun trajet retour n'est suppose. Bus differents si courses multiples.
            dep = start
            arr = start + timedelta(seconds=float(duration_s))
            trip_rows.append(dict(trip_id=f"T{i+1:03d}", vehicle_instance=f"V{i+1:03d}",
                                  passengers=pax, origin=route["origin"],
                                  destination=route["destination"],
                                  depart_utc=dep.isoformat(), arrive_utc=arr.isoformat(),
                                  distance_m=str(distance_m), empty_distance_m="0",
                                  energy_used=str(per_trip_energy)))
        passenger_km = distance_m / Decimal(1000) * total_passengers
        warnings = ["PROTOTYPE : monoligne, 1 jour, aucune réutilisation de véhicule.",
                    "Aucun détour, retour dépôt, temps de pause ou recharge pris en charge."]
        if route.get("provider") == "manual":
            warnings.append("Distance/durée déclarées par l'utilisateur, non vérifiées par routage.")
        if scenario.get("objective") not in (None, "cost"):
            warnings.append("Objectif choisi enregistré, aucun calcul d'optimalité ni classement n'est réalisé.")
        else:
            warnings.append("Aucune minimisation du coût n'est prouvée : affectation baseline seulement.")
        if scenario.get("tco_scope") == "complete":
            warnings.append("TCO complet limité aux postes saisis, sans coût d'exploitation non paramétré.")
        if energy.get("quality") != "verified":
            warnings.append("Tarifs et facteurs sont des hypothèses non vérifiées ; pas des données nationales officielles.")
        if vehicle.get("quality") != "verified":
            warnings.append("Données de véhicule non vérifiées.")
        out = {
            "status": SolveStatus.FEASIBLE_NOT_PROVEN.value,
            "engine": self.ENGINE_VERSION,
            "objective": scenario.get("objective", "cost"),
            "objective_proven_optimal": False,
            "optimality_gap": None,
            "scope": {"tco": scenario["tco_scope"], "emissions": scenario["emission_scope"],
                      "consumption": "fixed", "schedule": "one_way_no_reuse"},
            "totals": {
                "passengers_requested": total_passengers,
                "passengers_served": total_passengers,
                "passengers_unserved": 0,
                "vehicles_used": trip_count,
                "trips": trip_count,
                "passenger_km": passenger_km,
                "distance_passenger_m": total_distance,
                "distance_empty_m": Decimal(0),
                "duration_driving_s": total_duration,
                "duration_wait_s": Decimal(0),
                "energy_consumed": total_energy,
                "energy_unit": vehicle["unit"],
                "eur_total": cost["total_eur"],
                "eur_per_vehicle": safe_ratio(cost["total_eur"], Decimal(trip_count)),
                "eur_per_km": safe_ratio(cost["total_eur"], total_distance / Decimal(1000)),
                "eur_per_passenger": safe_ratio(cost["total_eur"], Decimal(total_passengers)),
                "kgco2e_total": total_co2e,
                "kgco2e_per_passenger": safe_ratio(total_co2e, Decimal(total_passengers)),
                "gco2e_per_passenger_km": safe_ratio(total_co2e * 1000, passenger_km),
            },
            "cost_breakdown": cost,
            "co2e_breakdown": {"selected_perimeter": scenario["emission_scope"],
                                "energy_kgco2e": total_co2e, "vehicle_kgco2e": None,
                                "infrastructure_kgco2e": None},
            "trips": trip_rows,
            "constraints": [], "unserved_demand": [],
            "warnings": warnings,
            "provenance": {
                "route": {"provider": route.get("provider"), "source": route.get("source")},
                "vehicle_version_id": snapshot["vehicle_version"]["id"],
                "energy_version_id": snapshot["energy_version"]["id"],
                "energy_source": energy["source"],
                "energy_source_date": energy["source_date"],
                "scenario_revision_id": snapshot["scenario_revision_id"],
            },
        }
        return SolveResult(status=SolveStatus.FEASIBLE_NOT_PROVEN,
                           result=stringify(out), warnings=tuple(warnings))
