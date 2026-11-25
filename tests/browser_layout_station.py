"""Acceptance of the three-card simulator layout, visible route geometry, and hover station tooltip.

Runs against the shipped HTML/CSS/JS over HTTP-like URLs. Synthetic values are
browser fixtures only: they are not used by the real simulator. No live API calls.
"""
import asyncio
import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "src" / "simco2" / "ui"
REPORTS = ROOT / "reports" / "layout-station"


def fixtures():
    entries = json.loads((UI / "vehicle-reference-catalog.json").read_text(encoding="utf-8"))["entries"]
    vehicles = []
    for index, e in enumerate(entries[:3]):
        vehicles.append({"id": f"vehicle-{index}", "vehicle_key": f"key-{index}",
                         "payload": {"label": e["label"], "manufacturer": e["manufacturer"],
                                     "model": e["model"], "seats": e["seats"],
                                     "energy_code": e["energy_code"], "unit": e["unit"],
                                     "consumption_per_km": str(e["consumption_per_km"]),
                                     "usable_capacity": str(e["usable_capacity"]),
                                     "reserve": str(e["reserve"]), "consumption_per_hour": "0",
                                     "source": "Fixture navigateur"}})
    energies = [{"id": "energy1", "payload": {"country_iso": "FR", "energy_code": "DIESEL",
                                                 "unit": "L", "price_per_unit": "1.7",
                                                 "source": "Fixture navigateur", "source_date": "2026-11-24",
                                                 "factors": {"direct": "2.7", "well_to_wheel": "3.4"}}},
                {"id": "energy2", "payload": {"country_iso": "FR", "energy_code": "BIOGNV",
                                                 "unit": "kg", "price_per_unit": "1.5",
                                                 "source": "Fixture navigateur", "source_date": "2026-11-24",
                                                 "factors": {"direct": "0.4", "well_to_wheel": "0.8"}}}]
    route = {"origin": "Caen", "destination": "Rouen", "distance_m": 132500,
             "duration_s": 6240, "provider": "browser_test", "source": "Fixture routage",
             "geometry": {"type": "LineString", "coordinates": [
                 [-0.36, 49.18], [-0.19, 49.16], [0.07, 49.24],
                 [0.49, 49.37], [0.86, 49.42], [1.1, 49.44]]},
             "origin_coordinates": [-0.36, 49.18], "destination_coordinates": [1.1, 49.44]}
    station = {"id": "fixture-h2", "name": "Station H2 de démonstration",
               "city": "Rouen", "address": "Rouen, Seine-Maritime",
               "longitude": 1.1, "latitude": 49.44, "category": "hydrogen",
               "energy_codes": ["H2"], "source": "Fixture navigateur"}
    responses = {
        "/public/session": {}, "/energies": energies, "/vehicles": vehicles,
        "/scenarios": [], "/runs": [], "/stations": [], "/comparisons": [],
        "/routing/resolve": {"quote_id": "browser-test-quote", "route": route},
        "/stations/discovery": {"hydrogen": [station],
                                "fuel": {"stations": [], "offset": 0, "limit": 100,
                                         "total": 0, "has_more": False, "unavailable": False}},
    }
    return responses


# This is deliberately a small Leaflet API double for testing application-side
# bindings. A real Leaflet visual regression is maintained separately.
LEAFLET_DOUBLE = """
window.L = {
 map(id){return {id, invalidateSize(){},fitBounds(){},setView(){},panTo(){},removeLayer(layer){layer?._node?.remove()}}},
 tileLayer(){return {addTo(){return this}}},
 latLngBounds(){return {pad(){return this}}},
 polyline(){return {addTo(){return this},getBounds(){return {isValid(){return true},pad(){return this}}}}},
 circleMarker(point,options){
   const node=document.createElement('button');node.className='mock-map-marker';node.type='button';
   node.setAttribute('aria-label','Marqueur de station');
   const marker={options, _node:node, _tooltip:null, _popup:null, _listeners:{},
     bindTooltip(t){this._tooltip=t;return this},getTooltip(){return this._tooltip},
     bindPopup(p){this._popup=p;return this},
     on(type,fn){node.addEventListener(type,fn);return this},
     addTo(map){const host=document.getElementById(map.id);if(host)host.appendChild(node);return this},
     setRadius(){},setStyle(){},bringToFront(){},getLatLng(){return point},
     openTooltip(){if(!this._tooltip)return;this.closeTooltip();const tip=document.createElement('div');
       tip.className='station-hover-tooltip';tip.innerHTML=this._tooltip;node.after(tip);this._tip=tip},
     closeTooltip(){this._tip?.remove();this._tip=null},
     openPopup(){if(!this._popup)return;const popup=document.createElement('div');
       popup.className='mock-full-popup';popup.innerHTML=this._popup;node.after(popup)}
   };return marker;
 }
};
"""


async def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    responses = fixtures()
    async with async_playwright() as p:
        options = {"headless": True, "args": ["--no-sandbox"]}
        chromium = shutil.which("chromium")
        if chromium:
            options["executable_path"] = chromium
        browser = await p.chromium.launch(**options)
        for viewport in (1920, 1280, 820, 390):
            page = await browser.new_page(viewport={"width": viewport, "height": 960})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            async def serve(route):
                parts = urlsplit(route.request.url)
                if parts.hostname != "lihyp.test":
                    await route.abort()
                    return
                if parts.path == "/":
                    await route.fulfill(body=(UI / "index.html").read_bytes(), content_type="text/html")
                elif parts.path.startswith("/assets/"):
                    asset = UI / Path(parts.path).name
                    if asset.is_file():
                        mime = "application/javascript" if asset.suffix == ".js" else (
                            "application/json" if asset.suffix == ".json" else "text/css")
                        await route.fulfill(body=asset.read_bytes(), content_type=mime)
                    else:
                        await route.fulfill(status=404)
                else:
                    data = responses.get(parts.path, [] if route.request.method == "GET" else {})
                    await route.fulfill(status=200, body=json.dumps(data), content_type="application/json")

            await page.route("**/*", serve)
            await page.set_content((UI / "index.html").read_text(encoding="utf-8").replace("<head>", '<head><base href="http://lihyp.test/">', 1), wait_until="load")
            await page.locator("#scenario-form").wait_for(state="visible")
            await page.wait_for_function(
                "document.querySelectorAll('#vehicle-compare-options .compare-option').length >= 3")
            cards = [await page.locator(f".ux-{kind}-input").bounding_box()
                     for kind in ("route", "vehicle", "plan")]
            assert all(cards), cards
            if viewport >= 1180:
                assert abs(cards[0]["y"] - cards[1]["y"]) < 5, cards
                assert abs(cards[1]["y"] - cards[2]["y"]) < 5, cards
                assert cards[0]["x"] < cards[1]["x"] < cards[2]["x"], cards
            if viewport <= 760:
                assert cards[0]["y"] < cards[1]["y"] < cards[2]["y"], cards
            map_box = await page.locator("#route-map-container").bounding_box()
            assert map_box and map_box["y"] >= max(c["y"] + c["height"] for c in cards) - 2
            assert map_box["width"] >= cards[0]["width"] * (2 if viewport >= 1180 else 0.9)
            assert not await page.evaluate("document.documentElement.scrollWidth > innerWidth+2")
            assert await page.locator(".notice-banner").count() == 0
            assert await page.locator(".sidebar-label.compact").count() == 0
            await page.locator("#calculate-route").click()
            await page.locator("#route-map-sketch svg.route-sketch-svg").wait_for(state="visible")
            assert await page.locator('#route-map-sketch path[stroke="#087e8b"]').count() == 1
            assert await page.locator("#ux-route-distance").inner_text() != "—"
            assert not errors, errors
            if viewport in (1920, 390):
                await page.screenshot(path=str(REPORTS / f"simulation-{viewport}.png"), full_page=True)
            await page.close()

        # The Leaflet integration is isolated: hovering a marker opens a compact
        # tooltip, while clicking it still opens full station details.
        page = await browser.new_page(viewport={"width": 1440, "height": 960})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        await page.evaluate(LEAFLET_DOUBLE)

        async def serve_leaflet(route):
            parts = urlsplit(route.request.url)
            if parts.hostname != "lihyp.test":
                await route.abort()
                return
            if parts.path == "/":
                await route.fulfill(body=(UI / "index.html").read_bytes(), content_type="text/html")
            elif parts.path.startswith("/assets/"):
                asset = UI / Path(parts.path).name
                mime = "application/javascript" if asset.suffix == ".js" else (
                    "application/json" if asset.suffix == ".json" else "text/css")
                if asset.exists():
                    await route.fulfill(body=asset.read_bytes(), content_type=mime)
                else:
                    await route.fulfill(status=404)
            else:
                await route.fulfill(body=json.dumps(responses.get(parts.path, [])),content_type="application/json")

        await page.route("**/*", serve_leaflet)
        await page.set_content((UI / "index.html").read_text(encoding="utf-8").replace("<head>", '<head><base href="http://lihyp.test/">', 1), wait_until="load")
        await page.locator('[data-view="stations"]').click()
        await page.locator(".mock-map-marker").wait_for(state="visible")
        await page.locator(".mock-map-marker").hover()
        tip = page.locator(".station-hover-tooltip")
        await tip.wait_for(state="visible")
        assert "Station H2 de démonstration" in await tip.inner_text()
        assert "Rouen" in await tip.inner_text()
        assert await page.locator(".mock-full-popup").count() == 0
        await page.locator(".mock-map-marker").click()
        assert await page.locator(".mock-full-popup").count() == 1
        assert not errors, errors
        await page.screenshot(path=str(REPORTS / "stations-hover.png"), full_page=True)
        await browser.close()
    print("Browser layout/station regression OK at 1920/1280/820/390 widths")


if __name__ == "__main__":
    asyncio.run(main())
