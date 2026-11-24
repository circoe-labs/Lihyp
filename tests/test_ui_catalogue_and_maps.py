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
    client = TestClient(app)
    assert client.post("/public/session").status_code == 200
    vehicles = client.get("/vehicles").json()
    assert vehicles == []  # one-click opt-in creates it; logging in does not mutate data
    js = (UI / "app.js").read_text(encoding="utf-8")
    assert 'solutionCard(demoCoach())' in js
    assert 'add-demo-vehicle' in js
    assert 'synthetic' in js.lower()


def test_stations_and_energy_catalogue_layout_matches_reviewed_mockups():
    html = (UI / 'index.html').read_text(encoding='utf-8')
    js = (UI / 'app.js').read_text(encoding='utf-8')
    css = (UI / 'style.css').read_text(encoding='utf-8')
    for control in ('station-filter-h2', 'station-filter-petrol',
                    'station-filter-diesel', 'station-list', 'station-details'):
        assert f'id="{control}"' in html
    assert 'station-explorer-grid' in css
    assert "bindPopup(stationPopupHtml(s))" in js
    assert ".on('mouseover',()=>emphasizeMarker(s.id,true))" in js
    assert "marker.setRadius(baseMarkerRadius(marker)*1.7)" in js
    assert 'id="station-area"' in html
    assert 'selectStation(b.dataset.stationId)' in js
    assert 'data-i18n="addEnergy"' in html
    assert 'id="energy-editor"' in html
    assert 'data-energy-edit=' in js and 'data-energy-remove=' in js
    assert 'archiveEnergyConfirm' in js
