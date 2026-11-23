"""Vérification de la découverte, du routage, du périmètre et des devis immuables."""
from decimal import Decimal

import httpx
from fastapi.testclient import TestClient

from simco2.adapters.discovery import NORMANDY_H2, FuelStationDirectory, normalize_fuel_station
from simco2.api.app import create_app
from simco2.domain.contracts import RouteResult
from test_api import energy, vehicle, scenario


class FakeGeocoder:
    def locate(self, value):
        assert value in ("Caen", "Rouen")
        return ((-0.362, 49.183), "Caen") if value == "Caen" else ((1.099, 49.443), "Rouen")


class FakeRouter:
    def route(self, origin, destination, profile):
        assert origin == (-0.362, 49.183)
        assert destination == (1.099, 49.443)
        assert profile == "driving-car"
        return RouteResult(Decimal('132542.7'), Decimal('6184.1'), profile,
                           "osrm_demo", "test", "2026-11-23T10:00:00Z",
                           geometry={"type":"LineString", "coordinates":[list(origin),list(destination)]},
                           restrictions=("Demo route for testing only",))


class FakeFuelDirectory:
    def page(self, offset, limit, area="normandy"):
        return {"stations": [{"id":"fuel-test", "name":"Station test",
                              "category":"fuel", "longitude":0.1,"latitude":49.1,
                              "energy_codes":["Gazole", "SP95"], "department_code":"76",
                              "address":"Rue Exemple, 76000 Rouen, France"}],
                "offset": offset, "limit":limit, "total":1, "has_more":False,
                "unavailable":False,"source":"DGCCRF fixture"}


def auth_client(tmp_path):
    app = create_app(tmp_path / 'routing.db', geocoder=FakeGeocoder(),
                     routing_provider=FakeRouter(), fuel_directory=FakeFuelDirectory())
    app.state.db.create_user('alice', 'test-passphrase-at-least-12')
    app.state.db.create_user('bob', 'test-passphrase-at-least-13')
    client=TestClient(app)
    def login(name, password):
        return client.post('/auth/login',json={'username':name,'password':password}).json()['access_token']
    client.headers.update({'Authorization':'Bearer '+login('alice','test-passphrase-at-least-12')})
    return client, login


def test_route_quote_reproducibility_and_cross_user_isolation(tmp_path):
    client, login = auth_client(tmp_path)
    e = client.post('/energies',json=energy()).json()
    v = client.post('/vehicles',json=vehicle()).json()
    quote = client.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'} )
    assert quote.status_code == 200, quote.text
    assert quote.json()['route']['distance_m'] == 132543
    assert quote.json()['route']['duration_s'] == 6184
    assert quote.json()['route']['geometry']['type'] == 'LineString'
    fields = scenario(e['id'],v['id'])
    fields.pop('route')
    fields['route_quote_id'] = quote.json()['quote_id']
    response=client.post('/scenarios',json=fields)
    assert response.status_code == 201, response.text
    frozen=response.json()['latest_revision']['payload']['route']
    assert frozen['provider']=='osrm_demo'
    assert frozen['distance_m']==132543
    assert frozen['source'].startswith('Routage automatique')
    run=client.post('/runs',json={'scenario_revision_id':response.json()['latest_revision']['id']})
    assert run.status_code==201,run.text
    assert run.json()['snapshot']['scenario']['route']==frozen
    english_pdf=client.get(f"/runs/{run.json()['id']}/report.pdf?lang=en")
    assert english_pdf.status_code==200 and english_pdf.content.startswith(b'%PDF')
    assert client.get(f"/runs/{run.json()['id']}/report.pdf?lang=de").status_code==422

    # Un client ne peut pas revendiquer une route venant d'un provider non vérifiée.
    forged = dict(fields,route_quote_id=None,route={
        'origin':'Caen','destination':'Rouen','distance_m':1,'duration_s':1,
        'provider':'openrouteservice','source':'fake external route'})
    assert client.post('/scenarios',json=forged).status_code==422
    assert client.post('/scenarios',json=dict(fields,route_quote_id='made-up')).status_code==404
    bob_token = login('bob','test-passphrase-at-least-13')
    client.headers.update({'Authorization':'Bearer '+bob_token})
    assert client.post('/scenarios',json=fields).status_code==404
    client.headers.pop('Authorization')
    assert client.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'}).status_code==401


def test_normandy_station_sources_and_station_price_is_never_exposed(tmp_path):
    c,_=auth_client(tmp_path)
    result=c.get('/stations/discovery')
    assert result.status_code==200
    items=result.json()['hydrogen']
    assert len(items)==7 and all(48 < s['latitude'] < 50 for s in items)
    assert all(s['bus_compatibility']=='not_confirmed' for s in items)
    assert all(s['source'].startswith('https://www.h2-mobile.fr/') for s in items)
    assert result.json()['fuel']['stations'][0]['category']=='fuel'
    assert c.get('/stations/discovery?offset=-1').status_code==422
    assert c.get('/stations/discovery?limit=101').status_code==422
    assert 'price' not in str(result.json()['fuel']['stations'])


def test_fuel_directory_normalization_pagination_unavailable_cache():
    records=[{'id':1234,'adresse':'Rue Exemple','cp':'14000','ville':'Caen',
              'code_departement':'14','region':'Normandie','latitude':4918300,'longitude':-36200,
              'gazole_prix':99.99,'sp95_prix':99.99,'carburants_disponibles':['Gazole','SP95'],
              'services_service':['Piste poids lourds']}]
    calls=[]
    def mock(request):
        calls.append(str(request.url))
        assert request.url.host=='data.economie.gouv.fr'
        assert 'Normandie' in str(request.url)
        return httpx.Response(200,json={'results':records,'total_count':101})
    with httpx.Client(transport=httpx.MockTransport(mock)) as client:
        provider=FuelStationDirectory(client)
        data=provider.page(0,100)
        assert data['has_more'] and data['stations'][0]['latitude']==49.183
        assert data['stations'][0]['longitude']==-0.362
        assert data['stations'][0]['heavy_vehicle_lane_reported']
        assert '99.99' not in str(data)
        assert provider.page(0,100)==data
        assert len(calls)==1
    assert normalize_fuel_station({**records[0],'code_departement':'75'}) is None
    assert normalize_fuel_station({**records[0],'latitude':123456789}) is None
    with httpx.Client(transport=httpx.MockTransport(lambda _:httpx.Response(503))) as client:
        out=FuelStationDirectory(client).page()
        assert out['unavailable'] and out['stations']==[]


def test_ign_geocoder_and_osrm_provider_mocked_without_network():
    from simco2.adapters.routing import GeoplatformGeocoder, OSRMRoutingProvider
    def mock(request):
        if request.url.host=='data.geopf.fr':
            return httpx.Response(200,json={'features':[
                {'properties':{'label':'Caen (Calvados)','city':'Caen'},'geometry':{'coordinates':[-0.362,49.183]}},
            ]})
        assert request.url.host=='router.project-osrm.org'
        return httpx.Response(200,json={'routes':[{'distance':100000,'duration':7000,
            'geometry':{'type':'LineString','coordinates':[[-0.362,49.183],[1.099,49.443]]}}]})
    with httpx.Client(transport=httpx.MockTransport(mock)) as client:
        geo=GeoplatformGeocoder(client)
        coord, name=geo.locate('Caen')
        assert coord==(-0.362,49.183) and 'Caen' in name
        route=OSRMRoutingProvider(client=client).route(coord,(1.099,49.443),'driving-car')
        assert route.distance_m==100000 and route.provider=='osrm_demo'
        assert route.geometry['coordinates'][0]==[-0.362,49.183]


def test_upper_normandy_station_area_is_server_filtered_and_cached(tmp_path):
    """Eure/Seine-Maritime only, without making local station prices accessible."""
    c, _ = auth_client(tmp_path)
    payload = c.get('/stations/discovery?area=upper_normandy')
    assert payload.status_code == 200
    assert payload.json()['coverage'] == 'Eure et Seine-Maritime'
    assert len(payload.json()['hydrogen']) == 5
    assert {station['department_code'] for station in payload.json()['hydrogen']} == {'27', '76'}
    assert c.get('/stations/discovery?area=upper_normanndy').status_code == 422
    assert c.get('/stations/discovery?area=normandy').status_code == 200

    rows = [
        {'id': 27001001, 'adresse': 'Avenue de la Gare', 'cp': '27000',
         'ville': 'Évreux', 'code_departement': '27', 'latitude': 4902400,
         'longitude': 115000, 'carburants_disponibles': ['Gazole', 'E10'],
         'gazole_maj': '2026-11-23T08:00:00Z', 'gazole_prix': 1.99,
         'horaires_automate_24_24': 'Oui',
         'services_service': ['Piste poids lourds', 'Automate CB 24/24']},
        {'id': 76001001, 'adresse': 'Quai du Port', 'cp': '76000',
         'ville': 'Rouen', 'code_departement': '76', 'latitude': 4944000,
         'longitude': 110000, 'carburants_disponibles': ['SP98'],
         'sp98_prix': 2.22},
        {'id': 14001001, 'adresse': 'Rue de Caen', 'cp': '14000',
         'ville': 'Caen', 'code_departement': '14', 'latitude': 4918000,
         'longitude': -36000, 'carburants_disponibles': ['Gazole']},
    ]
    calls = []
    def request_mock(request):
        query = request.url.params['where']
        calls.append(query)
        assert 'code_departement' in query or 'Normandie' in query
        return httpx.Response(200, json={'results': rows, 'total_count': 3})
    with httpx.Client(transport=httpx.MockTransport(request_mock)) as client:
        directory = FuelStationDirectory(client)
        result = directory.page(0, 100, area='upper_normandy')
        assert [station['department_code'] for station in result['stations']] == ['27','76']
        assert all(not any(key.endswith('_prix') or key == 'price' for key in station)
                   for station in result['stations'])
        first=result['stations'][0]
        assert first['heavy_vehicle_lane_reported'] and first['automatic_24h_reported']
        assert first['source_updated_at'].startswith('2026-11-23')
        assert directory.page(0, 100, area='upper_normandy') is result
        assert len(calls)==1
        result2=directory.page(0, 100, area='normandy')
        assert len(result2['stations'])==3
        assert len(calls)==2
