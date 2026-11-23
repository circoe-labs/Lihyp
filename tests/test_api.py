from fastapi.testclient import TestClient
from simco2.api.app import create_app
from simco2.domain.engine import BaselineEngine


def setup_client(tmp_path):
    app = create_app(tmp_path / "api.sqlite")
    db = app.state.db
    db.create_user("alice", "very-long-passphrase-01")
    db.create_user("bob", "very-long-passphrase-02")
    client = TestClient(app)
    token = client.post("/auth/login", json={"username": "alice", "password": "very-long-passphrase-01"}).json()["access_token"]
    client.headers.update({"Authorization": "Bearer " + token})
    return client, db


def energy():
    return dict(country_iso="FR", energy_code="DIESEL", unit="L",
                price_per_unit="2", factors={"direct": "2.7", "well_to_wheel": "3.3"},
                source="Fixture hypothétique; non officielle", source_date="2026-01-01")


def vehicle():
    return dict(label="Autocar hypothétique", manufacturer="Demo", model="bus", seats=50,
                energy_code="DIESEL", unit="L", consumption_per_km="0.2",
                consumption_per_hour="0", usable_capacity="100", reserve="5",
                maintenance_eur_per_km="0", labor_eur_per_h="0", purchase_eur="0",
                residual_eur="0", life_years=10, insurance_eur_year="0",
                source="Fixture hypothétique; non officielle")


def scenario(eid, vid):
    return dict(name="80 passagers", country_iso="FR",
                start_date="2026-11-20", end_date="2026-11-20", timezone="Europe/Paris",
                route=dict(origin="A", destination="B", distance_m=100000,
                           duration_s=7200, provider="manual", source="Fixture synthétique"),
                passengers=80, window_start="09:00", window_end="11:00",
                max_vehicles=2, vehicle_version_id=vid, energy_version_id=eid)


def test_api_end_to_end_snapshot_immutability_audit_and_auth(tmp_path):
    c, db = setup_client(tmp_path)
    assert c.get("/auth/me").status_code == 200
    e = c.post("/energies", json=energy())
    v = c.post("/vehicles", json=vehicle())
    assert e.status_code == v.status_code == 201, (e.text, v.text)
    data = scenario(e.json()["id"], v.json()["id"])
    s = c.post("/scenarios", json=data)
    assert s.status_code == 201, s.text
    r = c.post("/runs", json={"scenario_revision_id": s.json()["latest_revision"]["id"]})
    assert r.status_code == 201, r.text
    old_result = r.json()["result"]
    assert old_result["totals"]["eur_total"] == "80.0"
    assert old_result["totals"]["kgco2e_total"] == "108.00"
    assert len(r.json()["snapshot_sha256"]) == 64
    pdf = c.get(f'/runs/{r.json()["id"]}/report.pdf')
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"
    new_energy = c.post("/energies", json={**energy(), "price_per_unit": "4"})
    assert new_energy.status_code == 201
    same = c.get(f'/runs/{r.json()["id"]}')
    assert same.json()["result"] == old_result
    assert same.json()["snapshot_sha256"] == r.json()["snapshot_sha256"]
    assert c.get("/audit").json()
    c.headers.pop("Authorization")
    assert c.get("/vehicles").status_code == 401
    c.headers.update({"Authorization": "Bearer " + c.post("/auth/login", json={
        "username": "bob", "password": "very-long-passphrase-02"}).json()["access_token"]})
    assert c.get("/vehicles").status_code == 200  # catalogues partages
    assert c.get(f'/scenarios/{s.json()["id"]}').status_code == 404  # Q24 provisoire
    assert c.get(f'/runs/{r.json()["id"]}').status_code == 404


def test_api_rejects_bad_units_sources_modes_and_untrusted_station_status(tmp_path):
    c, _ = setup_client(tmp_path)
    assert c.post("/energies", json={**energy(), "unit": "kWh"}).status_code == 422
    assert c.post("/energies", json={**energy(), "price_per_unit": 3.14}).status_code == 422
    assert c.post("/vehicles", json={**vehicle(), "reserve": "1000"}).status_code == 422
    bad_station = {"name": "Station test", "longitude": 0.1, "latitude": 49.1,
                   "access": "public", "equipments": [{"energy_code": "DIESEL", "connector": "pompe", "ports": 1}],
                   "source": "Fichier non vérifié", "observed_at": "2026-01-01",
                   "operational_status": "confirmed"}
    assert c.post("/stations", json=bad_station).status_code == 422
    good = {**bad_station, "operational_status": "unverified"}
    assert c.post("/stations", json=good).status_code == 201
    assert "price" not in c.get("/stations").json()[0]["payload"]
    assert c.post("/stations", json={**good, "price_per_unit": "2"}).status_code == 422
    assert c.get("/routing/status").json()["configured"] is False
    assert c.post("/routing/preview", json={"origin": [0,0], "destination": [1,1]}).status_code == 503
