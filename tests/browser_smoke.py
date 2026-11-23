"""Test visuel Chromium + API ASGI intégrée sans réseau :
python tests/browser_smoke.py

Nécessite Playwright/Chromium dans le poste QA. Aucun serveur externe n'est contacté.
"""
import asyncio
import base64
import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from playwright.async_api import async_playwright
from simco2.api.app import create_app


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        app=create_app(Path(tmp)/'web.db')
        app.state.db.create_user('smoke','smoke-long-passphrase-123')
        c=TestClient(app)
        ui=Path(__file__).parents[1]/'src'/'simco2'/'ui'
        html=(ui/'index.html').read_text()
        html=html.replace('<link rel="stylesheet" href="/assets/style.css" />','')
        html=html.replace('<script defer src="/assets/app.js"></script>','')
        async with async_playwright() as p:
            browser=await p.chromium.launch(executable_path='/usr/bin/chromium',
                                             headless=True,args=['--no-sandbox'])
            page=await browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
            errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            await page.set_content(html)
            await page.add_style_tag(content=(ui/'style.css').read_text())

            async def bridge(source,url,method,headers,body):
                response=c.request(method,url,headers=headers,content=body if body else None)
                return {'status':response.status_code,'type':response.headers.get('content-type','application/json'),
                        'body':base64.b64encode(response.content).decode('ascii')}

            await page.expose_binding('bridgeRequest',bridge)
            await page.evaluate('''() => {
              window.fetch = async (url, opt={}) => {
                const d=await window.bridgeRequest(url,opt.method||'GET',opt.headers||{},opt.body||null);
                const data=Uint8Array.from(atob(d.body),x=>x.charCodeAt(0));
                return new Response(d.status===204?null:data,
                    {status:d.status,headers:{'Content-Type':d.type}});
              };
            }''')
            await page.add_script_tag(content=(ui/'app.js').read_text())
            await page.locator('#login-form input[name=username]').fill('smoke')
            await page.locator('#login-form input[name=password]').fill('smoke-long-passphrase-123')
            await page.locator('#login-form button[type=submit]').click()
            await page.locator('#stat-energies').wait_for(state='visible')
            await page.screenshot(path='reports/browser_overview.png',full_page=True)
            await page.locator('[data-view=energy]').click()
            await page.locator('#energy-form input[name=price_per_unit]').fill('2')
            await page.locator('#energy-form input[name=direct]').fill('2.7')
            await page.locator('#energy-form input[name=well_to_wheel]').fill('3.3')
            await page.locator('#energy-form input[name=source]').fill('Fixture synthétique NON nationale')
            await page.locator('#energy-form button[type=submit]').click()
            await page.locator('#energy-table').get_by_text('2 EUR/L',exact=False).wait_for()
            await page.locator('[data-view=vehicles]').click()
            await page.locator('#vehicle-form input[name=label]').fill('Bus diesel fictif')
            await page.locator('#vehicle-form input[name=manufacturer]').fill('Atelier test')
            await page.locator('#vehicle-form input[name=model]').fill('Test 01')
            await page.locator('#vehicle-form button[type=submit]').click()
            await page.locator('#vehicle-table').get_by_text('Bus diesel fictif').wait_for()
            await page.locator('[data-view=scenarios]').click()
            await page.locator('#scenario-form input[name=origin]').fill('A')
            await page.locator('#scenario-form input[name=destination]').fill('B')
            await page.locator('#scenario-form input[name=distance_m]').fill('100000')
            await page.locator('#scenario-form input[name=duration_s]').fill('7200')
            await page.locator('#scenario-form button[type=submit]').click()
            await page.locator('#view-results').wait_for(state='visible')
            await page.locator('#result-detail').get_by_text('108.00 kg CO₂e').wait_for()
            await page.screenshot(path='reports/browser_results.png',full_page=True)
            if errors:raise AssertionError('Browser JS errors: '+repr(errors))
            print('Browser smoke OK, login, energy, vehicle, scenario, results checked.')
            await browser.close()


if __name__=='__main__':
    asyncio.run(main())
