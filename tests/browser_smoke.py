"""Vérification locale Chromium de la nouvelle UX bilingue, sans réseau extérieur.

Usage: python tests/browser_smoke.py
Nécessite Playwright et Chromium (facultatifs en environnement de développement).
Les données de route et stations-service sont des fixtures, jamais des données nationales.
"""
import asyncio
import base64
import re
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient
from playwright.async_api import async_playwright
from simco2.api.app import create_app

from test_discovery_and_resolved_routing import FakeGeocoder, FakeRouter, FakeFuelDirectory
from decimal import Decimal
from simco2.domain.contracts import RouteResult


class BrowserDayRouter(FakeRouter):
    """Route fixtures for the day-planner browser flow (no external requests)."""
    def route(self, origin, destination, profile):
        legs={
            ((1.099,49.443),(-0.362,49.183)):(120000,6300),
            ((1.099,49.443),(0.1,49.1)):(15000,900),
            ((0.1,49.1),(-0.362,49.183)):(50000,3600),
        }
        key=tuple(origin),tuple(destination)
        if key not in legs:
            return super().route(origin,destination,profile)
        m,s=legs[key]
        return RouteResult(Decimal(m),Decimal(s),profile,'osrm_demo','fake-day',
            '2026-11-23T09:00:00Z',
            geometry={'type':'LineString','coordinates':[list(origin),list(destination)]})


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        app = create_app(Path(tmp)/'web.db', geocoder=FakeGeocoder(),
                         routing_provider=BrowserDayRouter(), fuel_directory=FakeFuelDirectory())
        app.state.db.create_user('admin', 'smoke-long-passphrase-123')
        client = TestClient(app)
        ui = Path(__file__).parents[1]/'src'/'simco2'/'ui'
        html = (ui/'index.html').read_text(encoding='utf-8')
        # Les cartes utilisent Leaflet en production. Test hors ligne des affichages de secours.
        html = re.sub(r'<link rel="stylesheet" href="https://unpkg.com/leaflet[^>]+/>', '', html, flags=re.S)
        html = re.sub(r'<script defer src="https://unpkg.com/leaflet[^>]+></script>', '', html, flags=re.S)
        html = html.replace('<link rel="stylesheet" href="/assets/style.css" />', '')
        html = html.replace('<script defer src="/assets/app.js"></script>', '')

        async with async_playwright() as p:
            browser = await p.chromium.launch(executable_path='/usr/bin/chromium',
                                              headless=True, args=['--no-sandbox'])
            page = await browser.new_page(viewport={'width':1440,'height':1000}, accept_downloads=True)
            page.set_default_timeout(5000)
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            await page.set_content(html)
            await page.add_style_tag(content=(ui/'leaflet-layout.css').read_text(encoding='utf-8'))
            await page.add_style_tag(content=(ui/'style.css').read_text(encoding='utf-8'))

            async def bridge(source, url, method, headers, body):
                response = client.request(method,url, headers=headers,
                                          content=body if body else None)
                return {'status':response.status_code,
                        'type':response.headers.get('content-type','application/json'),
                        'body':base64.b64encode(response.content).decode('ascii')}

            await page.expose_binding('bridgeRequest', bridge)
            await page.evaluate('''() => {
              window.fetch = async (url,opt={}) => {
                const d = await window.bridgeRequest(url,opt.method||'GET',opt.headers||{},opt.body||null);
                const bytes = Uint8Array.from(atob(d.body),x=>x.charCodeAt(0));
                return new Response(d.status===204?null:bytes,
                    {status:d.status,headers:{'Content-Type':d.type}});
              };
            }''')
            await page.add_script_tag(content=(ui/'app.js').read_text(encoding='utf-8'))

            assert await page.locator('#login').is_visible()
            await page.locator('#language-toggle').click()
            assert await page.locator('[data-i18n=signIn]').inner_text() == 'Sign in'
            await page.locator('#login-form input[name=username]').fill('admin')
            await page.locator('#login-form input[name=password]').fill('smoke-long-passphrase-123')
            await page.locator('#login-form button[type=submit]').click()
            await page.locator('#scenario-form').wait_for(state='visible')
            assert await page.locator('#view-stations').is_hidden()
            assert await page.locator('#page-title').inner_text() == 'Simulations'
            assert not await page.locator('#view-overview').count()
            assert not await page.locator('#view-results').count()
            assert 'Compare costs, emissions' in await page.locator('[data-i18n=scenarioIntro]').inner_text()

            await page.locator('#calculate-route').click()
            await page.locator('#route-summary').wait_for(state='visible')
            assert '132.5 km' in await page.locator('#route-summary').inner_text()
            assert await page.locator('#route-map-fallback').is_visible()
            # Reproduce the reported failure: Leaflet DOM present but its CDN CSS blocked.
            # A deliberately oversized tile must not cover the vehicle form below the map.
            async def check_clipping(map_id, outside_id):
                return await page.evaluate('''([mapId, outsideId]) => {
                  const el = document.getElementById(mapId);
                  el.classList.remove('hidden'); el.classList.add('leaflet-container');
                  el.innerHTML = '<div class="leaflet-pane leaflet-tile-pane">' +
                    '<img class="leaflet-tile leaflet-tile-loaded" alt="" ' +
                    'src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" ' +
                    'style="width:3000px;height:3000px" /></div>';
                  const tile=el.querySelector('.leaflet-tile');
                  const target=document.getElementById(outsideId);
                  const b=target.getBoundingClientRect();
                  const node=document.elementFromPoint(b.left+10,b.top+10);
                  const valid = getComputedStyle(el).overflow==='hidden' &&
                    getComputedStyle(tile).position==='absolute' &&
                    !node?.closest('.leaflet-container');
                  el.replaceChildren();el.classList.remove('leaflet-container');
                  el.classList.add('hidden');
                  return valid;
                }''', [map_id, outside_id])
            await page.locator('#scenario-submit').scroll_into_view_if_needed()
            assert await check_clipping('route-map','scenario-submit')
            await page.locator('#language-toggle').click()
            assert (await page.locator('[data-i18n=scenarioIntro]').inner_text()).startswith('Un même trajet')
            assert await page.locator('#calculate-route').inner_text() == "Calculer l'itinéraire"
            (Path('reports')).mkdir(exist_ok=True)
            await page.screenshot(path='reports/new_simulations_fr.png',full_page=True)

            await page.locator('[data-view=vehicles]').click()
            assert await page.locator('#vehicle-table .solution-demo').is_visible()
            assert 'EXEMPLE FICTIF' in await page.locator('#vehicle-table').inner_text()
            assert '50' in await page.locator('#vehicle-table .solution-specs').inner_text()
            await page.screenshot(path='reports/demo_catalogue_fr.png',full_page=True)
            await page.locator('#add-demo-vehicle').click()
            await page.locator('#vehicle-table .solution-demo').wait_for(state='detached')
            assert 'Autocar diesel de démonstration' in await page.locator('#vehicle-table').inner_text()
            assert await page.locator('#vehicle-table [data-vehicle-simulate]').count() == 1

            await page.locator('[data-view=energy]').click()
            assert (await page.locator('#energy-form button[type=submit]').inner_text()) == 'Enregistrer'
            await page.screenshot(path='reports/energy_save_fr.png',full_page=True)
            assert await page.locator('#energy-editor').is_hidden()
            await page.locator('#add-energy').click()
            assert await page.locator('#energy-editor').is_visible()
            await page.locator('#energy-form input[name=price_per_unit]').fill('2')
            await page.locator('#energy-form input[name=direct]').fill('2.7')
            await page.locator('#energy-form input[name=well_to_wheel]').fill('3.3')
            await page.locator('#energy-form input[name=source]').fill('Fixture de recette, non nationale')
            await page.locator('#energy-form button[type=submit]').click()
            await page.locator('#energy-table').get_by_text('2 EUR/L',exact=False).wait_for()
            assert await page.locator('#energy-editor').is_hidden()
            await page.locator('[data-energy-edit="DIESEL"]').click()
            assert await page.locator('#energy-editor').is_visible()
            assert await page.locator('#energy-code').is_disabled()
            assert await page.locator('#energy-form input[name=price_per_unit]').input_value() == '2'
            await page.locator('#energy-form input[name=price_per_unit]').fill('2.25')
            await page.locator('#energy-form button[type=submit]').click()
            await page.locator('#energy-table').get_by_text('2,25',exact=False).wait_for()
            await page.locator('[data-energy-history="DIESEL"]').click()
            await page.locator('#energy-history').get_by_text('v1',exact=False).wait_for()
            await page.screenshot(path='reports/energy_table_fr.png',full_page=True)


            await page.locator('[data-view=vehicles]').click()
            await page.locator('#vehicle-form input[name=label]').fill('Bus diesel fictif')
            await page.locator('#vehicle-form input[name=manufacturer]').fill('Atelier test')
            await page.locator('#vehicle-form input[name=model]').fill('Test 01')
            await page.locator('#vehicle-form input[name=consumption_per_km]').fill('0.14')
            await page.locator('#vehicle-form button[type=submit]').click()
            await page.locator('#vehicle-table').get_by_text('Bus diesel fictif').wait_for()

            await page.locator('[data-view=scenarios]').click()
            assert await page.locator('#vehicle-compare-options .compare-option').count() == 2
            assert await page.locator('#vehicle-compare-options .compare-vehicle-checkbox:checked').count() == 2
            await page.locator('#scenario-submit').click()
            await page.locator('#comparison-results').wait_for(state='visible')
            assert 'kg' in await page.locator('#comparison-results').inner_text()
            assert await page.locator('#comparison-results tbody tr').count() == 2
            assert len(set(await page.locator('#comparison-results tbody tr td:nth-child(5)').all_inner_texts())) == 2
            assert await page.locator('#comparison-results .comparison-table [data-compare-pdf]').count() == 2
            assert await page.locator('#comparison-results .day-solution-card').count() == 2
            assert await page.locator('#comparison-results .day-bus').count() == 4
            assert 'Course avec voyageurs' in await page.locator('#comparison-results').inner_text()
            await page.screenshot(path='reports/new_results_inline.png',full_page=True)
            await page.locator('[data-view=routing]').click()
            await page.locator('#routing-config-form').wait_for(state='visible')
            assert await page.locator('#routing-provider-label').inner_text() != ''
            await page.locator('#routing-provider').select_option('geoapify')
            await page.locator('#routing-profile').select_option('bus')
            await page.locator('#routing-config-form button[type=submit]').click()
            await page.wait_for_function("document.getElementById('routing-profile-label').textContent === 'bus'")
            await page.locator('#geoapify-key-form input[name=key]').fill('illustrative-test-only-key')
            await page.locator('#geoapify-key-form button[type=submit]').click()
            await page.wait_for_function("document.querySelector('#routing-geo-status').textContent.includes('serveur')")
            assert await page.locator('#geoapify-key-form input[name=key]').input_value() == ''
            assert 'illustrative-test-only-key' not in await page.locator('#view-routing').inner_text()
            await page.screenshot(path='reports/new_routing_settings_fr.png',full_page=True)

            await page.locator('[data-view=stations]').click()
            await page.locator('#station-list').get_by_text('H₂ · Rouen').wait_for()
            assert await page.locator('#station-area').input_value() == 'upper_normandy'
            assert await page.locator('.station-card').count() == 6  # 5 H2 + one fictional fuel fixture
            assert await page.locator('#station-map-fallback').is_visible()
            assert await check_clipping('station-map','station-filter-h2')
            assert await page.locator('#station-filter-h2').is_checked()
            await page.locator('#station-filter-h2').uncheck()
            assert await page.locator('.station-card').count() == 1
            await page.locator('#station-filter-h2').check()
            assert await page.locator('.station-card').count() == 6
            await page.locator('#station-area').select_option('normandy')
            await page.wait_for_function("document.querySelectorAll('#station-list .station-card').length === 8")
            await page.locator('#station-area').select_option('upper_normandy')
            await page.wait_for_function("document.querySelectorAll('#station-list .station-card').length === 6")
            await page.locator('#station-list .station-card').first.click()
            assert await page.locator('#station-details').is_visible()
            assert 'H₂' in await page.locator('#station-details').inner_text()
            await page.locator('#use-station-day-plan').click()
            assert await page.locator('#day-plan-enabled').is_checked()
            assert await page.locator('#day-plan-details').is_visible()
            assert 'Rouen' in await page.locator('#day-station-name').inner_text()
            await page.locator('[data-view=stations]').click()
            # Use the test fuel station to exercise real day events, not the H2 listing.
            await page.locator('#station-list .station-card').last.click()
            assert 'Station test' in await page.locator('#station-details').inner_text()
            await page.locator('#use-station-day-plan').click()
            await page.locator('#scenario-form input[name=passengers]').fill('140')
            await page.locator('#day-plan-details input[name=diesel_flow_l_per_min]').fill('30')
            await page.locator('#scenario-form .advanced-settings summary').click()
            await page.locator('#scenario-form input[name=window_end]').fill('20:00')
            await page.locator('#scenario-form input[name=max_vehicles]').fill('1')
            await page.locator('#scenario-submit').click()
            await page.wait_for_function("document.querySelectorAll('#comparison-results .day-solution-card').length === 2")
            assert 'Ravitaillement' in await page.locator('#comparison-results').inner_text()
            assert 'Attente en station: 0 min' in await page.locator('#comparison-results').inner_text() or \
                   'Attente en station : 0 min' in await page.locator('#comparison-results').inner_text()
            await page.screenshot(path='reports/day_plan_timeline_fr.png',full_page=True)
            await page.locator('[data-view=stations]').click()

            await page.screenshot(path='reports/stations_list_fr.png',full_page=True)
            await page.locator('#language-toggle').click()
            assert await page.locator('[data-i18n=stationTitle]').inner_text() == 'Stations in Normandy'
            assert 'Coach access' in await page.locator('.station-card').first.inner_text() or \
                   'not confirmed' in (await page.locator('.station-card').first.inner_text()).lower()
            await page.screenshot(path='reports/new_stations_en.png',full_page=True)
            assert not errors, 'Browser JS errors: '+repr(errors)
            print('Browser smoke OK: FR/EN login/navigation, automatic route, inline results, H2/fuel stations.')
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
