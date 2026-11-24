"""Regression checks: user-supplied nine-vehicle reference catalogue."""
import json
from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from simco2.api.app import create_app
from simco2.api.schemas import EnergyInput, VehicleInput

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "src/simco2/ui/vehicle-reference-catalog.json"


def test_all_nine_user_ranges_are_retained_without_inventing_specs():
    entries = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    assert len(entries) == 9
    assert len({entry["id"] for entry in entries}) == 9
    assert sorted({entry["energy_code"] for entry in entries}) == [
        "BIOGNV", "DIESEL", "ELECTRIC", "H2"]
    assert entries[0]["model"] == "Iveco Bus Crossway Line 12m"
    assert entries[0]["purchase_eur_ht"] == [230000, 250000]
    assert entries[0]["energy_cost_100km_eur_ht"] == [39, 48]
    assert entries[0]["maintenance_eur_per_km_ht"] == [0.25, 0.28]
    assert entries[4]["model"] == "Yutong ICe 12 (350 kWh)"
    assert entries[7]["purchase_scope"] == "retrofit_kit_installation"
    assert entries[8]["purchase_eur_ht"] == [650000, 750000]
    assert all("seats" not in e and "usable_capacity" not in e
               and "consumption_per_km" not in e for e in entries)


def test_biognv_requires_kg_unit():
    energy = dict(country_iso="FR", energy_code="BIOGNV", unit="kg",
                  price_per_unit="1.65", factors={"direct": "0"},
                  source="Hypothèse de comparaison non vérifiée",
                  source_date="2026-11-24")
    assert EnergyInput.model_validate(energy).unit == "kg"
    with pytest.raises(ValidationError):
        EnergyInput.model_validate({**energy, "unit": "L"})
    vehicle = dict(label="Autocar BioGNV test", manufacturer="Iveco Bus",
                   model="Crossway NP", seats=50, energy_code="BIOGNV",
                   unit="kg", consumption_per_km="0.4", usable_capacity="100",
                   reserve="10", source="Hypothèse de comparaison non vérifiée")
    assert VehicleInput.model_validate(vehicle).unit == "kg"
    with pytest.raises(ValidationError):
        VehicleInput.model_validate({**vehicle, "unit": "L"})


def test_reference_asset_visible_without_auto_creating_vehicles(tmp_path):
    app = create_app(tmp_path / "catalogue.sqlite")
    app.state.db.create_user("analyste", "this-is-an-adequately-long-secret")
    client = TestClient(app)
    response = client.get("/assets/vehicle-reference-catalog.json")
    assert response.status_code == 200
    assert len(response.json()["entries"]) == 9
    token = client.post("/auth/login", json={
        "username": "analyste", "password": "this-is-an-adequately-long-secret"
    }).json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    assert client.get("/vehicles").json() == []
    assert "BIOGNV" in {e["code"] for e in client.get("/energies/catalog").json()["energy_types"]}
    created = client.post("/energies", json={
        "country_iso":"FR", "energy_code":"BIOGNV", "unit":"kg",
        "price_per_unit":"1.65", "factors":{"direct":"0"},
        "source":"Hypothèse de test non vérifiée", "source_date":"2026-11-24"})
    assert created.status_code == 201, created.text
    vehicle = client.post("/vehicles", json={
        "label":"Autocar BioGNV test", "manufacturer":"Iveco Bus", "model":"Crossway NP",
        "seats":50, "energy_code":"BIOGNV", "unit":"kg",
        "consumption_per_km":"0.42", "usable_capacity":"120",
        "reserve":"10", "source":"Hypothèse de test non vérifiée"})
    assert vehicle.status_code == 201, vehicle.text
    assert len(client.get("/vehicles").json()) == 1


def test_frontend_requires_completion_before_reference_is_savable():
    html = (ROOT/"src/simco2/ui/index.html").read_text(encoding="utf-8")
    js = (ROOT/"src/simco2/ui/app.js").read_text(encoding="utf-8")
    assert 'id="reference-library"' in html
    assert 'id="reference-form-note"' in html
    assert "seats:'',consumption_per_km:''" in js
    assert "usable_capacity:''" in js
    assert "purchase_scope==='vehicle'" in js
    assert "referenceCompareTitle" in js and "referencePartialWarning" in js
