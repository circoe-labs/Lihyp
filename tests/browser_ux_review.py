"""Actual Chromium acceptance for the reference-like SimCO2 layouts (fixtures only).

No actual price, emissions, station or timing data are invented as production facts.
Run: python tests/browser_ux_review.py  (optional Playwright + Chromium install)
"""
import asyncio
import base64
import re
import shutil
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from playwright.async_api import async_playwright
from simco2.api.app import create_app
from test_discovery_and_resolved_routing import FakeGeocoder, FakeFuelDirectory
from browser_smoke import BrowserDayRouter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'ux-review'

async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        app=create_app(Path(tmp)/'ux-review.sqlite',geocoder=FakeGeocoder(),routing_provider=BrowserDayRouter(),fuel_directory=FakeFuelDirectory())
        app.state.db.create_user('admin','long-password-smoke-123')
        client=TestClient(app)
        token=client.post('/auth/login',json={'username':'admin','password':'long-password-smoke-123'}).json()['access_token']
        auth={'Authorization':f'Bearer {token}'}
        # Fixtures, not national/reference prices. Four saved vehicles, one energy.
        enr={'country_iso':'FR','energy_code':'DIESEL','unit':'L','price_per_unit':'2',
             'factors':{'direct':'2.7','well_to_wheel':'3.4'},'source':'Fixture de test hors production','source_date':'2026-11-24'}
        assert client.post('/energies',json=enr,headers=auth).status_code==201
        # Other representative energy prices/factors are test fixtures, not live tariffs.
        for code,unit,price,co2 in [('BIOGNV','kg','1.65','0.5'),('ELECTRIC','kWh','0.2','0'),('H2','kg','12','0')]:
            payload={**enr,'energy_code':code,'unit':unit,'price_per_unit':price,
                     'factors':{'direct':co2,'well_to_wheel':'0.6'}}
            assert client.post('/energies',json=payload,headers=auth).status_code==201
        catalog=(ROOT/'src/simco2/ui/vehicle-reference-catalog.json').read_text(encoding='utf-8')
        import json
        entries=json.loads(catalog)['entries']
        for e in [entries[0],entries[1],entries[2],entries[4]]:
            v={
              'label':e['label'],'manufacturer':e['manufacturer'],'model':e['model'],'seats':e['seats'],
              'energy_code':e['energy_code'],'unit':e['unit'], 'consumption_per_km':str(e['consumption_per_km']),
              'consumption_per_hour':str(e['consumption_per_hour']),'usable_capacity':str(e['usable_capacity']),
              'reserve':str(e['reserve']),'source':'Fixture utilisateur non vérifiée',
            }
            assert client.post('/vehicles',json=v,headers=auth).status_code==201
        ui=ROOT/'src/simco2/ui'
        html=(ui/'index.html').read_text(encoding='utf-8')
        html=re.sub(r'<link rel="stylesheet" href="https://unpkg.com/leaflet[^>]+/>','',html,flags=re.S)
        html=re.sub(r'<script defer src="https://unpkg.com/leaflet[^>]+></script>','',html,flags=re.S)
        html=html.replace('<link rel="stylesheet" href="/assets/style.css" />','')
        html=html.replace('<script defer src="/assets/app.js"></script>','')
        async with async_playwright() as p:
            browser=await p.chromium.launch(**({'executable_path':shutil.which('chromium')} if shutil.which('chromium') else {}),headless=True,args=['--no-sandbox'])
            page=await browser.new_page(viewport={'width':1550,'height':1000},accept_downloads=True)
            page.set_default_timeout(8000)
            errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            await page.set_content(html)
            if (ui/'leaflet-layout.css').exists():
                await page.add_style_tag(content=(ui/'leaflet-layout.css').read_text(encoding='utf-8'))
            await page.add_style_tag(content=(ui/'style.css').read_text(encoding='utf-8'))
            async def bridge(source,url,method,headers,body):
                response=client.request(method,url,headers=headers,content=body if body else None)
                return {'status':response.status_code,'type':response.headers.get('content-type','application/json'),
                        'body':base64.b64encode(response.content).decode('ascii')}
            await page.expose_binding('bridgeRequest',bridge)
            await page.evaluate('''() => {window.fetch = async (url,opt={}) => {
              const d=await window.bridgeRequest(url,opt.method||'GET',opt.headers||{},opt.body||null);
              const bytes=Uint8Array.from(atob(d.body),x=>x.charCodeAt(0));
              return new Response(d.status===204?null:bytes,{status:d.status,headers:{'Content-Type':d.type}});
            };}''')
            await page.add_script_tag(content=(ui/'app.js').read_text(encoding='utf-8'))
            await page.locator('#scenario-form').wait_for(state='visible')
            assert await page.locator('#login').is_hidden()
            assert await page.locator('#ux-route-distance').inner_text()=='—'
            assert await page.locator('.ux-vehicle-input .compare-option').count()==4
            assert not await page.locator('#comparison-results').is_hidden()
            # 1. Simulation left inputs, right map & results, no overlaid tiles.
            left=await page.locator('.simulator-composer').bounding_box()
            right=await page.locator('.ux-map-overview').bounding_box()
            assert left['x']+left['width'] <= right['x']+3, (left,right)
            await page.locator('#calculate-route').click()
            await page.locator('#route-summary').wait_for(state='visible')
            assert '132' in await page.locator('#ux-route-distance').inner_text()
            assert await page.locator('#route-map-sketch').is_visible()
            await page.evaluate('window.scrollTo(0,0)')
            await page.screenshot(path=str(OUT/'simulation-before.png'),full_page=True)
            for checkbox in await page.locator('#vehicle-compare-options input:not(:disabled)').all():
                if not await checkbox.is_checked():
                    await checkbox.check()
            await page.locator('#scenario-submit').click()
            await page.wait_for_function("document.querySelectorAll('#comparison-results .ux-comparison-table tbody tr').length===4")
            assert await page.locator('#ux-timeline-content').is_visible()
            assert await page.locator('#comparison-results [data-compare-pdf]').count()==4
            assert await page.locator('#comparison-results .day-solution-card').count()==0
            assert await page.locator('#ux-route-trips').inner_text()!='—'
            await page.locator('#ux-timeline-vehicle').select_option(index=1)
            assert await page.locator('#ux-timeline-content .ux-timeline-step').count()>=1
            await page.evaluate('window.scrollTo(0,0)')
            await page.screenshot(path=str(OUT/'simulation-results.png'),full_page=True)
            # 2. One vehicle catalogue visible at a time, filtering and detail, no stacked duplicate library.
            await page.locator('[data-view=vehicles]').click()
            await page.wait_for_function("document.querySelectorAll('#reference-library .reference-card').length === 9")
            assert await page.locator('#vehicle-table').is_hidden()
            assert await page.locator('.ux-vehicle-browser').count()==1
            await page.locator('[data-view-reference=biognv-12]').click()
            assert '200' in await page.locator('#ux-vehicle-preview').inner_text()
            await page.locator('#ux-vehicle-search').fill('eIntouro')
            assert await page.locator('#reference-library .reference-card').count()==1
            await page.locator('#ux-reset-filters').click()
            await page.locator('.ux-energy-filter input[value=ELECTRIC]').uncheck()
            assert await page.locator('#reference-library .reference-card').count()==6
            await page.locator('#ux-reset-filters').click()
            await page.evaluate('window.scrollTo(0,0)')
            await page.screenshot(path=str(OUT/'vehicles-library.png'),full_page=True)
            await page.locator('#ux-tab-registered').click()
            assert await page.locator('#reference-library').is_hidden()
            assert await page.locator('#vehicle-table').is_visible()
            assert await page.locator('#vehicle-table .reference-card').count()==4
            await page.locator('#vehicle-table [data-view-vehicle]').first.click()
            assert 'Données utilisateur' in await page.locator('#ux-vehicle-preview').inner_text()
            await page.evaluate('window.scrollTo(0,0)')
            await page.screenshot(path=str(OUT/'vehicles-registered.png'),full_page=True)
            # 3. Real admin login is still protected and available (not a cosmetic overlay).
            await page.locator('[data-view=routing]').click()
            await page.locator('#login-form input[name=username]').fill('admin')
            await page.locator('#login-form input[name=password]').fill('long-password-smoke-123')
            await page.locator('#login-form button[type=submit]').click()
            await page.wait_for_function("document.querySelector('#vehicle-editor-panel') && !document.querySelector('#vehicle-editor-panel').classList.contains('hidden')")
            await page.locator('[data-view=vehicles]').click()
            await page.locator('#ux-tab-library').click()
            await page.locator('[data-view-reference="electric-12-yutong"]').click()
            assert await page.locator('#vehicle-form input[name=seats]').input_value()=='59'
            await page.evaluate('window.scrollTo(0,0)')
            await page.screenshot(path=str(OUT/'vehicles-admin.png'),full_page=True)
            # 4. Responsive: no document-wide overflow, no opaque overlapping panes.
            for view in [{'width':1920,'height':1080},{'width':1280,'height':900},{'width':820,'height':900},{'width':390,'height':844}]:
                await page.set_viewport_size(view)
                await page.wait_for_timeout(80)
                bounds=await page.evaluate('''() => ({screen:innerWidth, scroll:document.documentElement.scrollWidth,
                   left:document.querySelector('.ux-vehicle-browser').getBoundingClientRect().toJSON(),
                   right:document.querySelector('.ux-vehicle-details').getBoundingClientRect().toJSON()})''')
                assert bounds['scroll'] <= bounds['screen']+2,bounds
                left,right=bounds['left'],bounds['right']
                intersects=left['x']<right['right']-2 and left['right']>right['x']+2 and left['y']<right['bottom']-2 and left['bottom']>right['y']+2
                assert not intersects,(view,bounds)
                await page.evaluate('window.scrollTo(0,0)')
                await page.screenshot(path=str(OUT/f'vehicles-{view["width"]}.png'),full_page=True)
            await page.locator('[data-view=scenarios]').click()
            for view in [{'width':1280,'height':900},{'width':820,'height':900},{'width':390,'height':844}]:
                await page.set_viewport_size(view)
                await page.wait_for_timeout(80)
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth+2')
                await page.evaluate('window.scrollTo(0,0)')
                await page.screenshot(path=str(OUT/f'simulation-{view["width"]}.png'),full_page=True)
            assert not errors,errors
            print('UX Chromium PASS: public data, compare, timetable, tabs, filters, admin, 4 viewports')
            await browser.close()

if __name__=='__main__':
    asyncio.run(main())
