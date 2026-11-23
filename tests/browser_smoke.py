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


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        app = create_app(Path(tmp)/'web.db', geocoder=FakeGeocoder(),
                         routing_provider=FakeRouter(), fuel_directory=FakeFuelDirectory())
        app.state.db.create_user('smoke', 'smoke-long-passphrase-123')
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
            await page.locator('#login-form input[name=username]').fill('smoke')
            await page.locator('#login-form input[name=password]').fill('smoke-long-passphrase-123')
            await page.locator('#login-form button[type=submit]').click()
            await page.locator('#scenario-form').wait_for(state='visible')
            assert await page.locator('#view-stations').is_hidden()
            assert await page.locator('#page-title').inner_text() == 'Simulations'
            assert not await page.locator('#view-overview').count()
            assert not await page.locator('#view-results').count()
            assert await page.locator('[data-i18n=scenarioIntro]').inner_text() == (
                'Enter the places and passenger demand. The software calculates road distance and time, and displays the route on a map.')

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
            assert await check_clipping('route-map','scenario-vehicle')
            await page.locator('#language-toggle').click()
            assert (await page.locator('[data-i18n=scenarioIntro]').inner_text()).startswith('Renseignez les lieux')
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
            await page.locator('#energy-form input[name=price_per_unit]').fill('2')
            await page.locator('#energy-form input[name=direct]').fill('2.7')
            await page.locator('#energy-form input[name=well_to_wheel]').fill('3.3')
            await page.locator('#energy-form input[name=source]').fill('Fixture de recette, non nationale')
            await page.locator('#energy-form button[type=submit]').click()
            await page.locator('#energy-table').get_by_text('2 EUR/L',exact=False).wait_for()

            await page.locator('[data-view=vehicles]').click()
            await page.locator('#vehicle-form input[name=label]').fill('Bus diesel fictif')
            await page.locator('#vehicle-form input[name=manufacturer]').fill('Atelier test')
            await page.locator('#vehicle-form input[name=model]').fill('Test 01')
            await page.locator('#vehicle-form button[type=submit]').click()
            await page.locator('#vehicle-table').get_by_text('Bus diesel fictif').wait_for()

            await page.locator('[data-view=scenarios]').click()
            await page.locator('#scenario-submit').click()
            await page.locator('#result-detail').wait_for(state='visible')
            assert 'kg CO₂e' in await page.locator('#result-detail').inner_text()
            assert await page.locator('#pdf-current').is_visible()
            await page.screenshot(path='reports/new_results_inline.png',full_page=True)

            await page.locator('[data-view=stations]').click()
            await page.locator('#station-list').get_by_text('H₂ · Rouen').wait_for()
            assert await page.locator('.station-card').count() == 8
            assert await page.locator('#station-map-fallback').is_visible()
            assert await check_clipping('station-map','station-filter')
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
