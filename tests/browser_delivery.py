"""Chromium regression for deployed HTML and external resource URLs.

Run: PYTHONPATH=src:tests python tests/browser_delivery.py
Browser loads CSS and JS through HTTP-like URLs served by FastAPI TestClient,
not with inline app.js/style.css as the old smoke suite did. The sandbox blocks
real loopback navigation; Playwright routes provide the exact API bytes instead.
"""
import asyncio
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient
from playwright.async_api import async_playwright
from simco2.api.app import create_app
from test_discovery_and_resolved_routing import FakeGeocoder, FakeFuelDirectory
from browser_smoke import BrowserDayRouter

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "src/simco2/ui"
OUT = ROOT / "reports/ux-release"


def seed(client):
    client.app.state.db.create_user("admin", "a-long-password-for-ui-acceptance")
    login = client.post("/auth/login", json={
        "username": "admin", "password": "a-long-password-for-ui-acceptance"})
    assert login.status_code == 200
    headers = {"Authorization": "Bearer " + login.json()["access_token"]}
    for code, unit, price in (("DIESEL", "L", "2.0"), ("BIOGNV", "kg", "1.65")):
        energy = {"country_iso": "FR", "energy_code": code, "unit": unit,
                  "price_per_unit": price,
                  "factors": {"direct": "2.7", "well_to_wheel": "3.4"},
                  "source": "Test navigateur non vérifié", "source_date": "2026-11-24"}
        assert client.post("/energies", json=energy, headers=headers).status_code == 201
    entries = json.loads((UI / "vehicle-reference-catalog.json").read_text(encoding="utf-8"))["entries"]
    for e in entries[:3]:
        vehicle = {"label": e["label"], "manufacturer": e["manufacturer"], "model": e["model"],
                   "seats": e["seats"], "energy_code": e["energy_code"], "unit": e["unit"],
                   "consumption_per_km": str(e["consumption_per_km"]),
                   "consumption_per_hour": str(e["consumption_per_hour"]),
                   "usable_capacity": str(e["usable_capacity"]), "reserve": str(e["reserve"]),
                   "source": "Hypothèse de test utilisateur non vérifiée"}
        assert client.post("/vehicles", json=vehicle, headers=headers).status_code == 201


async def check():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="lihyp-release-") as tmp:
        app = create_app(Path(tmp)/"test.sqlite", geocoder=FakeGeocoder(),
                         routing_provider=BrowserDayRouter(), fuel_directory=FakeFuelDirectory())
        with TestClient(app) as http:
            seed(http)
            home = http.get("/")
            assert home.status_code == 200
            assert home.headers["cache-control"] == "no-store, max-age=0"
            async with async_playwright() as playwright:
                chromium = shutil.which("chromium")
                options = {"headless": True, "args": ["--no-sandbox"]}
                if chromium:
                    options["executable_path"] = chromium
                browser = await playwright.chromium.launch(**options)
                page = await browser.new_page(viewport={"width":1550,"height":920})
                page.set_default_timeout(12000)
                errors, resources, stale_hits = [], {}, []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("response", lambda response: resources.update({urlsplit(response.url).path:response.url})
                        if urlsplit(response.url).path.endswith(("/app.js","/style.css")) else None)

                async def serve(route):
                    parts = urlsplit(route.request.url)
                    if parts.hostname != "lihyp.test":
                        await route.abort()
                        return
                    # Model an old browser cache containing the pre-PR#10 bundles.
                    # If a bundle URL lacks its version, intentionally return stale bytes.
                    if parts.path.endswith(("/app.js","/style.css")) and not parse_qs(parts.query).get("v"):
                        stale_hits.append(parts.path)
                        await route.fulfill(
                            body=("window.__old_bundle=true" if parts.path.endswith(".js")
                                  else ".ux-vehicle-workspace{display:block!important}"),
                            content_type=("application/javascript" if parts.path.endswith(".js") else "text/css"))
                        return
                    path = parts.path + (("?"+parts.query) if parts.query else "")
                    response = http.request(route.request.method, path,
                                            content=route.request.post_data or None,
                                            headers={k:v for k,v in route.request.headers.items()
                                                     if k.lower() not in ("host", "content-length")})
                    await route.fulfill(status=response.status_code,body=response.content,
                                        headers={"Content-Type":response.headers.get("content-type","application/json"),
                                                 "Cache-Control":response.headers.get("cache-control","")})

                await page.route("**/*", serve)
                # The generated index is loaded unchanged, apart from a base URL
                # required for browser requests under page.set_content().
                html = home.text.replace("<head>", '<head><base href="http://lihyp.test/">', 1)
                await page.set_content(html, wait_until="load")
                await page.locator("#scenario-form").wait_for(state="visible")
                await page.wait_for_function("document.querySelector('#vehicle-compare-options')?.children.length >= 2")
                assert not stale_hits, stale_hits
                assert not await page.evaluate("Boolean(window.__old_bundle)")
                for filename in ("app.js", "style.css"):
                    version = hashlib.sha256((UI/filename).read_bytes()).hexdigest()[:16]
                    assert parse_qs(urlsplit(resources[f"/assets/{filename}"]).query)["v"] == [version]
                assert await page.locator('[data-i18n="uxDistance"]').inner_text() == "Distance"
                assert await page.locator('[data-i18n="uxComparisonTitle"]').inner_text() == "Comparaison des véhicules"

                await page.locator('[data-view="vehicles"]').click()
                await page.wait_for_function("document.querySelectorAll('#reference-library .reference-card').length===9")
                for key, name in (("uxFilters","Filtres"),("uxLibraryTab","Bibliothèque"),
                                  ("uxVehicleDetail","Fiche véhicule"),
                                  ("uxResetFilters","Réinitialiser les filtres")):
                    assert await page.locator(f'[data-i18n="{key}"]').inner_text() == name
                assert await page.locator('.ux-vehicle-workspace').evaluate(
                    'el => getComputedStyle(el).display') == 'grid'
                # The old long cost table is opt-in, not another permanent stack.
                assert not await page.locator('#ux-benchmarks').evaluate('el => el.open')
                await page.locator('#ux-benchmarks summary').click()
                assert await page.locator('#ux-cost-benchmarks').is_visible()
                await page.locator('#ux-benchmarks summary').click()
                assert not await page.locator('#ux-benchmarks').evaluate('el => el.open')
                await page.screenshot(path=str(OUT/'vehicles-desktop.png'), full_page=True)
                for width,height in ((1920,1080),(1280,900),(820,900),(390,844)):
                    await page.set_viewport_size({'width':width,'height':height})
                    await page.wait_for_timeout(100)
                    assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'), width
                    if width in (1920,390):
                        await page.screenshot(path=str(OUT/f'vehicles-{width}.png'),full_page=True)
                await page.set_viewport_size({'width':1550,'height':920})
                await page.locator('[data-view="scenarios"]').click()
                await page.locator('#calculate-route').click()
                await page.locator('#route-summary').wait_for(state='visible')
                await page.locator('#scenario-submit').click()
                await page.wait_for_function(
                    "document.querySelectorAll('#comparison-results .ux-comparison-table tbody tr').length >= 2")
                await page.screenshot(path=str(OUT/'simulation-results.png'), full_page=True)
                assert not errors, errors
                print('PASS: versioned CSS/JS URLs, no stale bundle, FR labels, grids, route and comparison, 4 widths')
                await browser.close()


if __name__ == '__main__':
    asyncio.run(check())
