"""Regression: an upgraded HTML document must never reuse prior JS/CSS assets.

Previously, browser tests injected scripts/styles inline; they could not detect
mixed cached versions after an update. These tests exercise the HTTP boundary.
"""
import hashlib
import re
from pathlib import Path

from fastapi.testclient import TestClient
from simco2.api.app import create_app

UI = Path(__file__).resolve().parents[1] / "src/simco2/ui"


def test_index_references_content_addressed_assets_and_disallows_cache(tmp_path):
    client = TestClient(create_app(tmp_path / "asset-headers.sqlite"))
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, max-age=0"
    assert response.headers["pragma"] == "no-cache"
    html = response.text
    for name in ("app.js", "style.css"):
        digest = hashlib.sha256((UI / name).read_bytes()).hexdigest()[:16]
        target = f"/assets/{name}?v={digest}"
        assert target in html
        assert f'/assets/{name}"' not in html, "Unversioned links could reuse stale assets"
        asset = client.get(target)
        assert asset.status_code == 200
        assert asset.content == (UI / name).read_bytes()
        assert asset.headers["cache-control"] == "no-store, max-age=0"
        assert asset.headers["pragma"] == "no-cache"
    # The price/source reference library must also stay synchronized on upgrades.
    ref = client.get("/assets/vehicle-reference-catalog.json")
    assert ref.status_code == 200
    assert ref.headers["cache-control"] == "no-store, max-age=0"
    assert len(ref.json()["entries"]) == 9


def test_all_new_ux_translations_have_fr_and_en_keys():
    markup = (UI / "index.html").read_text(encoding="utf-8")
    javascript = (UI / "app.js").read_text(encoding="utf-8")
    keys = sorted(set(re.findall(r'data-i18n(?:-placeholder)?="(ux[A-Za-z0-9]+)"', markup)))
    assert keys and "uxFilters" in keys and "uxDistance" in keys
    for key in keys:
        # New UX terms must be defined in *both* dictionaries, not left to raw keys.
        assert len(re.findall(r"\b" + re.escape(key) + r"\s*:", javascript)) >= 2, key


def test_approved_layout_styles_are_in_served_stylesheet(tmp_path):
    client = TestClient(create_app(tmp_path / "styles.sqlite"))
    css = client.get("/assets/style.css").text
    assert ".ux-vehicle-workspace{display:grid" in css
    assert ".ux-route-indicators{display:flex" in css
    assert ".ux-vehicle-browser .reference-grid" in css
    assert ".ux-vehicle-filters{display:flex" in css
