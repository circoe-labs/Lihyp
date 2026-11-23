from copy import deepcopy
from simco2.domain.engine import BaselineEngine


def fixture():
    return {
        "scenario_revision_id": "REV-001",
        "scenario": {
            "name": "Fixture 80/50", "start_date": "2026-11-20", "end_date": "2026-11-20",
            "timezone": "Europe/Paris", "country_iso": "FR",
            "route": {"origin": "A", "destination": "B", "distance_m": 100000,
                      "duration_s": 7200, "provider": "manual", "source": "Test synthétique"},
            "passengers": 80, "window_start": "09:00", "window_end": "10:00",
            "max_vehicles": 2, "tco_scope": "variable", "emission_scope": "direct",
            "demand_mode": "global", "network_mode": "single", "fleet_mode": "single",
            "depot_mode": "none", "time_scope": "rapid", "consumption_scope": "fixed",
            "refuel_mode": "no_refuel", "charging_mode": "no_charge",
            "objective": "cost"},
        "vehicle_version": {"id": "VEH-001", "payload": {
            "energy_code": "DIESEL", "unit": "L", "seats": 50, "quality": "unverified",
            "consumption_per_km": "0.2", "consumption_per_hour": "0",
            "usable_capacity": "100", "reserve": "5",
            "maintenance_eur_per_km": "0", "labor_eur_per_h": "0", "purchase_eur": "0",
            "residual_eur": "0", "life_years": 10, "insurance_eur_year": "0"}},
        "energy_version": {"id": "ENG-001", "payload": {
            "country_iso": "FR", "energy_code": "DIESEL", "unit": "L",
            "price_per_unit": "2", "factors": {"direct": "2.7", "well_to_wheel": "3.3"},
            "source": "Test synthétique", "source_date": "2026-11-20",
            "quality": "unverified"}}
    }


def test_reference_two_trips_40_l_80_eur_108_kg():
    out = BaselineEngine().solve(fixture())
    assert out.status == "feasible_not_proven"
    t = out.result["totals"]
    assert (t["trips"], t["vehicles_used"], t["energy_consumed"],
            t["eur_total"], t["kgco2e_total"]) == (2, 2, "40.0", "80.0", "108.00")
    assert [t["passengers"] for t in out.result["trips"]] == [50, 30]
    assert out.result["objective_proven_optimal"] is False
    assert out.result["warnings"]


def test_too_few_vehicles_never_imagines_teleportation():
    x = fixture()
    x["scenario"]["max_vehicles"] = 1
    out = BaselineEngine().solve(x)
    assert out.status == "infeasible_proven"
    assert out.result["unserved_passengers"] == 30


def test_energy_reserve_and_missing_factors():
    x = fixture()
    x["vehicle_version"]["payload"]["usable_capacity"] = "22"
    assert BaselineEngine().solve(x).result["constraints"][0]["code"] == "insufficient_energy_no_refuel"
    x = fixture()
    x["energy_version"]["payload"]["factors"] = {}
    assert BaselineEngine().solve(x).status == "invalid_input"


def test_multi_day_and_acv_are_not_fake_successes():
    x = fixture()
    x["scenario"]["end_date"] = "2026-11-21"
    assert BaselineEngine().solve(x).status == "invalid_input"
    x = fixture()
    x["scenario"]["emission_scope"] = "lifecycle"
    assert BaselineEngine().solve(x).status == "invalid_input"


def test_unserved_zero_and_price_does_not_change_emissions():
    x = fixture()
    x["scenario"]["passengers"] = 0
    out = BaselineEngine().solve(x)
    assert out.result["totals"]["eur_per_passenger"] is None
    a = BaselineEngine().solve(fixture()).result["totals"]
    x = fixture()
    x["energy_version"]["payload"]["price_per_unit"] = "4"
    b = BaselineEngine().solve(x).result["totals"]
    assert a["kgco2e_total"] == b["kgco2e_total"]
    assert a["eur_total"] != b["eur_total"]


def test_dst_rejected_without_unreliable_departs():
    x = fixture()
    x['scenario']['start_date'] = '2026-03-29'
    x['scenario']['end_date'] = '2026-03-29'
    x['scenario']['window_start'] = '02:30'
    x['scenario']['window_end'] = '03:30'
    out = BaselineEngine().solve(x)
    assert out.status == 'invalid_input'
    assert out.result['constraints'][0]['code'] == 'nonexistent_local_time'
