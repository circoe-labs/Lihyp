"""Regression checks for the visible UI changes requested by the pilot user."""
from pathlib import Path

from fastapi.testclient import TestClient

from simco2.api.app import create_app

UI = Path(__file__).resolve().parents[1] / "src" / "simco2" / "ui"


def test_map_fallback_css_is_locally_served_and_referenced(tmp_path):
    app = create_app(tmp_path / "test-ui-map.sqlite")
    client = TestClient(app)
    html = client.get("/")
    css = client.get("/assets/leaflet-layout.css")
    assert html.status_code == 200
    assert css.status_code == 200
    assert 'href="/assets/leaflet-layout.css"' in html.text
    assert 'position: absolute' in css.text
    assert 'overflow: hidden' in css.text
    assert '.leaflet-tile-pane' in css.text
    layout = (UI / "style.css").read_text(encoding="utf-8")
    assert 'contain: layout paint' in layout
    assert 'overflow: hidden !important' in layout


def test_save_labels_are_plain_language_but_db_keeps_revision_history():
    html = (UI / "index.html").read_text(encoding="utf-8")
    js = (UI / "app.js").read_text(encoding="utf-8")
    assert 'data-i18n="saveEnergy">Enregistrer</button>' in html
    assert "saveEnergy:'Enregistrer'" in js
    assert "saveEnergy:'Save'" in js
    assert 'data-energy-history' in js
    assert 'loadEnergyHistory' in js


def test_bus_demo_is_not_silently_created_on_login(tmp_path):
    app = create_app(tmp_path / "test-ui-demo.sqlite")
    db = app.state.db
    db.create_user("reader", "an-adequately-long-passphrase")
    client = TestClient(app)
    token = client.post("/auth/login", json={
        "username": "reader", "password": "an-adequately-long-passphrase"}).json()["access_token"]
    vehicles = client.get("/vehicles", headers={"Authorization": f"Bearer {token}"}).json()
    assert vehicles == []  # one-click opt-in creates it; logging in does not mutate data
    js = (UI / "app.js").read_text(encoding="utf-8")
    assert 'solutionCard(demoCoach())' in js
    assert 'add-demo-vehicle' in js
    assert 'synthetic' in js.lower()
