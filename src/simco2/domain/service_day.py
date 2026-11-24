"""Conservative, deterministic single-line day schedule for homogeneous fleets.

Only sourced routing legs are accepted. No invented reverse journey, station access,
waiting, queueing, legal break or recharging. This is a bounded heuristic, not an optimizer.
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from math import ceil

from .calculators import energy_fixed, cost_breakdown, emissions, safe_ratio
from .contracts import SolveResult, SolveStatus
from .engine import stringify
from .errors import DomainError
from .units import dec, local_to_utc

ZERO = Decimal(0)


def _not_solved(reason: str, code: str = "day_plan_unresolved", unserved: int = 0):
    return SolveResult(SolveStatus.NO_SOLUTION_FOUND, {
        "status": SolveStatus.NO_SOLUTION_FOUND.value,
        "constraints": [{"code": code, "message": reason}],
        "unserved_passengers": unserved, "trips": [], "vehicles": [], "totals": None,
        "warnings": ["Aucune preuve d'impossibilite : planificateur heuristique mono-ligne."],
    })


def _leg(data: dict | None, label: str) -> dict:
    if not data or dec(data.get("distance_m", 0)) <= 0 or dec(data.get("duration_s", 0)) <= 0:
        raise DomainError("missing_routing_leg", f"Trajet routier manquant : {label}")
    return data


def schedule_day(snapshot: dict) -> SolveResult:
    """One-way passenger runs with explicit road return / refuel legs when reusing a bus.

    All buses start full at the line origin, but remain at their final destination.
    The departure window is interpreted as a full service interval for this mode.
    """
    try:
        return _schedule_day(snapshot)
    except (DomainError, ValueError, TypeError, KeyError, ArithmeticError, OverflowError) as err:
        return SolveResult(SolveStatus.INVALID_INPUT, {
            "status": SolveStatus.INVALID_INPUT.value,
            "constraints": [{"code": getattr(err, "code", "invalid_input"),
                             "message": getattr(err, "message", "Parametres de planning invalides")}],
            "unserved_passengers": snapshot.get("scenario", {}).get("passengers", 0),
            "trips": [], "vehicles": [], "totals": None,
        })


def _schedule_day(snapshot: dict) -> SolveResult:
    scenario = snapshot["scenario"]
    vehicle = snapshot["vehicle_version"]["payload"]
    energy = snapshot["energy_version"]["payload"]
    if scenario["start_date"] != scenario["end_date"]:
        raise DomainError("unsupported_day", "Seule une journee est disponible")
    if scenario.get("network_mode") != "single" or scenario.get("depot_mode") != "none":
        raise DomainError("unsupported_day", "Mode journee reserve a une ligne sans depot")
    if vehicle["energy_code"] != energy["energy_code"] or vehicle["unit"] != energy["unit"]:
        raise DomainError("energy_mismatch", "Energie et unite incompatibles")
    if energy.get("country_iso") != scenario.get("country_iso"):
        raise DomainError("country_mismatch", "Pays du tarif incompatible")
    route = _leg(scenario["route"], "aller")
    start = local_to_utc(f"{scenario['start_date']}T{scenario['window_start']}:00", scenario["timezone"])
    stop = local_to_utc(f"{scenario['end_date']}T{scenario['window_end']}:00", scenario["timezone"])
    if stop <= start:
        raise DomainError("invalid_window", "Fin du service posterieure au debut requise")
    capacity, reserve = dec(vehicle["usable_capacity"]), dec(vehicle["reserve"])
    if capacity <= reserve or dec(vehicle["consumption_per_km"]) < 0:
        raise DomainError("invalid_energy", "Capacite utile et reserve incoherentes")
    seats, passengers, fleet_limit = int(vehicle["seats"]), int(scenario["passengers"]), int(scenario["max_vehicles"])
    if seats <= 0 or passengers < 0 or fleet_limit < 0:
        raise DomainError("invalid_capacity", "Places, demande ou parc invalides")
    trips_needed = ceil(passengers / seats)
    if trips_needed > 500:
        return _not_solved("Etude trop grande pour le planificateur indicatif (500 courses maximum)",
                           code="prototype_trip_limit", unserved=passengers)
    if capacity > Decimal("1000000"):
        raise DomainError("out_of_range", "Capacite energetique hors limites du prototype")
    route_energy = energy_fixed(dec(route["distance_m"]), dec(route["duration_s"]),
                                vehicle["consumption_per_km"], vehicle["consumption_per_hour"])
    if route_energy > capacity - reserve:
        return SolveResult(SolveStatus.INFEASIBLE_PROVEN, {
            "status": SolveStatus.INFEASIBLE_PROVEN.value,
            "constraints": [{"code": "trip_exceeds_usable_range",
                             "message": "Une course depasse l'autonomie et aucune recharge en route n'est prevue"}],
            "unserved_passengers": passengers, "trips": [], "vehicles": [], "totals": None,
        })
    reverse = snapshot.get("day_legs", {}).get("reverse")
    station = snapshot.get("day_station")
    detour = snapshot.get("day_legs", {}).get("via_station")
    policy = snapshot.get("day_station_policy", "imposed" if station else "none")
    options = list((snapshot.get("day_station_options") or {}).get(vehicle["energy_code"], []))
    # Compatibility with snapshots created before station auto-selection.
    if station and detour and policy == "imposed":
        options = [{"station": station, "to_station": detour.get("to_station"),
                    "from_station": detour.get("from_station")}]
    if policy == "none":
        options = []
    flow_rates = snapshot.get("day_refuel_rates_per_min") or {}
    rate = dec(flow_rates.get(vehicle["energy_code"], "0"))
    handling_minutes = dec(snapshot.get("day_handling_minutes", "0"))
    if handling_minutes < 0 or rate < 0:
        raise DomainError("invalid_station_rate", "Debit ou manipulation negatif")
    if vehicle["energy_code"] == "ELECTRIC":
        # Charging is not a constant-flow fuel operation.
        rate = ZERO
    if trips_needed > 1:
        _leg(reverse, "retour a vide")
    buses: list[dict] = []
    trips: list[dict] = []
    service_dist = deadhead_dist = drive_s = stop_s = total_energy = ZERO
    service_energy = deadhead_energy = ZERO
    refuel_count = 0
    remaining = passengers

    def power(leg):
        return energy_fixed(dec(leg["distance_m"]), dec(leg["duration_s"]),
                            vehicle["consumption_per_km"], vehicle["consumption_per_hour"])

    def event(bus, kind, begin, leg=None, duration=None, amount=ZERO, notes=""):
        nonlocal service_dist, deadhead_dist, drive_s, stop_s, total_energy, service_energy, deadhead_energy
        dur = dec(leg["duration_s"]) if leg else dec(duration)
        distance = dec(leg["distance_m"]) if leg else ZERO
        used = power(leg) if leg else ZERO
        finish = begin + timedelta(seconds=float(dur))
        bus["energy"] -= used
        if bus["energy"] < reserve:
            raise DomainError("energy_below_reserve", "Reserve energetique du vehicule non respectee")
        if kind == "service":
            service_dist += distance
            service_energy += used
        elif leg:
            deadhead_dist += distance
            deadhead_energy += used
        if leg:
            drive_s += dur
        else:
            stop_s += dur
        total_energy += used
        row = {"kind": kind, "start_utc": begin.isoformat(), "end_utc": finish.isoformat(),
               "duration_s": str(dur), "distance_m": str(distance),
               "energy_used": str(used), "energy_added": str(amount),
               "note": notes}
        bus["events"].append(row)
        bus["available_at"] = finish
        return finish

    for trip_num in range(trips_needed):
        pax = min(remaining, seats)
        # Reuse existing coaches when feasible. Search a bounded shortlist of
        # routed, energy-compatible stations when the direct return cannot work.
        candidates = []
        for bus in buses:
            before, fuel = bus["available_at"], bus["energy"]
            ret_energy = power(reverse)
            if fuel >= ret_energy + route_energy + reserve:
                arrival = before + timedelta(seconds=float(dec(reverse["duration_s"]) + dec(route["duration_s"])))
                if arrival <= stop:
                    candidates.append((arrival, bus["id"], bus, [("deadhead_return", reverse)], None))
            if fuel < ret_energy + route_energy + reserve and rate > 0:
                for option in options:
                    selected = option.get("station") or {}
                    if vehicle["energy_code"] not in selected.get("energy_codes", []):
                        continue
                    to_station = _leg(option.get("to_station"), "vers station")
                    from_station = _leg(option.get("from_station"), "retour depuis station")
                    e_to, e_back = power(to_station), power(from_station)
                    if fuel < e_to + reserve or capacity < e_back + route_energy + reserve:
                        continue
                    quantity = capacity - (fuel - e_to)
                    if quantity < 0:
                        continue
                    extra = (dec(to_station["duration_s"]) + dec(from_station["duration_s"])
                             + quantity / rate * Decimal(60) + handling_minutes * Decimal(60))
                    arrival = before + timedelta(seconds=float(extra + dec(route["duration_s"])))
                    if arrival <= stop:
                        candidates.append((arrival, bus["id"], bus,
                            [("station_detour", to_station), ("deadhead_return", from_station)],
                            selected))
        # Earliest completed next passenger run. This is a bounded greedy
        # decision, never a claim of a mathematically proven optimum.
        chosen = min(candidates, key=lambda t: (t[0], t[1])) if candidates else None
        if chosen is not None:
            _, _, bus, chain, station_chosen = chosen
            for kind, leg in chain:
                if kind == "deadhead_return" and station_chosen:
                    quantity = capacity - bus["energy"]
                    seconds = quantity / rate * Decimal(60)
                    event(bus, "refuel", bus["available_at"], duration=seconds, amount=quantity,
                          notes=station_chosen["name"] + " · sans attente / no queue")
                    bus["events"][-1]["station_id"] = station_chosen["id"]
                    bus["events"][-1]["station_name"] = station_chosen["name"]
                    bus["energy"] = capacity
                    refuel_count += 1
                    if handling_minutes:
                        event(bus, "handling", bus["available_at"],
                              duration=handling_minutes * Decimal(60))
                event(bus, kind, bus["available_at"], leg=leg)
        else:
            if len(buses) >= fleet_limit:
                reason = ("Aucune rotation supplémentaire trouvée avec le parc et les horaires. "
                          "Vérifier le trajet retour, l'autonomie, les stations compatibles "
                          "et les débits de plein (0 interdit le plein). "
                          "Le modèle ne prouve pas l'impossibilité.")
                return _not_solved(reason, unserved=remaining)
            if start + timedelta(seconds=float(dec(route["duration_s"]))) > stop:
                return _not_solved("La course ne tient pas dans la plage de service", unserved=remaining)
            bus = {"id": f"V{len(buses)+1:03d}", "energy": capacity,
                   "available_at": start, "events": []}
            buses.append(bus)
        depart = bus["available_at"]
        event(bus, "service", depart, leg=route)
        trips.append({"trip_id": f"T{trip_num+1:03d}", "vehicle_instance": bus["id"],
                      "passengers": pax, "origin": route["origin"], "destination": route["destination"],
                      "depart_utc": depart.isoformat(), "arrive_utc": bus["available_at"].isoformat(),
                      "distance_m": str(route["distance_m"]), "empty_distance_m": "0",
                      "energy_used": str(route_energy)})
        remaining -= pax

    elapsed_s = (max((b["available_at"] for b in buses), default=start) - start).total_seconds()
    active_seconds = sum((sum((dec(e["duration_s"]) for e in b["events"]), ZERO)
                          for b in buses), ZERO)
    passenger_km = dec(route["distance_m"]) * dec(passengers) / Decimal(1000)
    costs = cost_breakdown(energy_quantity=total_energy, price_per_unit=energy["price_per_unit"],
                           distance_m=service_dist + deadhead_dist, duration_s=drive_s + stop_s,
                           vehicle_count=len(buses), days=1, vehicle=vehicle,
                           scope=scenario["tco_scope"],
                           infrastructure_daily_eur=scenario.get("infrastructure_daily_eur", "0"))
    kg = emissions(energy_quantity=total_energy, factors=energy.get("factors", {}),
                   perimeter=scenario["emission_scope"])
    rows = []
    for b in buses:
        rows.append({"vehicle_instance": b["id"], "events": b["events"],
                     "active_duration_s": str(sum((dec(e["duration_s"]) for e in b["events"]), ZERO)),
                     "remaining_energy": str(b["energy"])})
    warnings = [
        "Planning heuristique, ni optimalite ni minimum de vehicules prouves.",
        "Trajets retour et station issus d'un fournisseur, compatibilite autocar non garantie.",
        "Temps d'attente a la station = 0 par decision metier.",
        "Aucune pause chauffeur/reglementation, depot, congestion ni recharge electrique modele.",
        "Stations indicatives : disponibilite et acces a confirmer avant exploitation.",
    ]
    if policy == "automatic":
        warnings.append("Sélection automatique sur un échantillon de stations : optimum global non prouvé.")
        warnings.extend(snapshot.get("day_station_search_warnings") or [])
        if not rate and trips_needed > 1:
            warnings.append("Débit de remplissage nul : aucun plein possible; seuls les véhicules autonomes ou supplémentaires sont utilisés.")
    result = {
        "status": SolveStatus.FEASIBLE_NOT_PROVEN.value, "engine": "single-line-day-v0.1",
        "objective": scenario.get("objective", "cost"), "objective_proven_optimal": False,
        "optimality_gap": None,
        "scope": {"tco": scenario["tco_scope"], "emissions": scenario["emission_scope"],
                  "consumption": "fixed", "schedule": "single_line_day_greedy"},
        "totals": {
            "passengers_requested": passengers, "passengers_served": passengers,
            "passengers_unserved": 0, "vehicles_used": len(buses), "trips": trips_needed,
            "passenger_km": passenger_km, "distance_passenger_m": service_dist,
            "distance_empty_m": deadhead_dist, "duration_driving_s": drive_s,
            "duration_wait_s": ZERO, "duration_refuel_s": sum(
                (dec(e["duration_s"]) for b in buses for e in b["events"] if e["kind"] == "refuel"), ZERO),
            "duration_handling_s": sum(
                (dec(e["duration_s"]) for b in buses for e in b["events"] if e["kind"] == "handling"), ZERO),
            "duration_elapsed_s": dec(str(elapsed_s)), "duration_vehicle_s": active_seconds,
            "refuel_count": refuel_count, "energy_consumed": total_energy,
            "rotations_per_vehicle": {b["id"]: sum(e["kind"] == "service" for e in b["events"])
                                      for b in buses},
            "energy_unit": vehicle["unit"], "eur_total": costs["total_eur"],
            "eur_per_vehicle": safe_ratio(costs["total_eur"], dec(len(buses))),
            "eur_per_km": safe_ratio(costs["total_eur"], (service_dist + deadhead_dist)/Decimal(1000)),
            "eur_per_passenger": safe_ratio(costs["total_eur"], dec(passengers)),
            "kgco2e_total": kg, "kgco2e_per_passenger": safe_ratio(kg, dec(passengers)),
            "gco2e_per_passenger_km": safe_ratio(kg*Decimal(1000), passenger_km),
        },
        "cost_breakdown": costs,
        "co2e_breakdown": {"selected_perimeter": scenario["emission_scope"],
                            "energy_kgco2e": kg, "vehicle_kgco2e": None,
                            "infrastructure_kgco2e": None},
        "trips": trips, "vehicles": rows, "constraints": [], "unserved_demand": [],
        "warnings": warnings,
        "provenance": {"route": {"provider": route.get("provider"), "source": route.get("source")},
                       "day_legs": snapshot.get("day_legs"), "station": station,
                       "station_policy": policy,
                       "station_options": snapshot.get("day_station_options"),
                       "vehicle_version_id": snapshot["vehicle_version"]["id"],
                       "energy_version_id": snapshot["energy_version"]["id"],
                       "energy_source": energy["source"],
                       "energy_source_date": energy["source_date"],
                       "scenario_revision_id": snapshot["scenario_revision_id"]},
    }
    return SolveResult(SolveStatus.FEASIBLE_NOT_PROVEN, stringify(result), warnings=tuple(warnings))
