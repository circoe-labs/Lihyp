"""Comparaisons homogènes, isolation et secrets de routage côté serveur."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from simco2.adapters.routing import GeoapifyRoutingProvider
from simco2.adapters.routing_settings import RoutingSettings
from simco2.api.app import create_app
from simco2.domain.errors import RoutingFailure
from test_api import energy, vehicle
from test_discovery_and_resolved_routing import FakeGeocoder, FakeRouter


def client_with_route(tmp_path):
    settings = RoutingSettings(tmp_path / 'private-routing-settings.json')
    app = create_app(tmp_path / 'cmp.sqlite', geocoder=FakeGeocoder(),
                     routing_provider=FakeRouter(), routing_settings=settings)
    app.state.db.create_user('admin', 'test-operator-password-123')
    app.state.db.create_user('bob', 'test-bob-password-12345')
    client = TestClient(app)

    def login(name, password):
        return client.post('/auth/login', json={'username': name, 'password': password}).json()['access_token']

    client.headers['Authorization'] = 'Bearer ' + login('admin', 'test-operator-password-123')
    return client, login, settings


def test_comparison_same_inputs_two_versions_and_immutability(tmp_path):
    client, login, _ = client_with_route(tmp_path)
    diesel = client.post('/energies', json=energy()).json()
    v1 = client.post('/vehicles', json=vehicle()).json()
    v2 = client.post('/vehicles', json={**vehicle(), 'label': 'Bus plus sobre',
                                       'consumption_per_km': '0.12'}).json()
    quote = client.post('/routing/resolve', json={'origin': 'Caen', 'destination': 'Rouen'}).json()
    fields = dict(name='Comparer deux autocars', route_quote_id=quote['quote_id'],
                  vehicle_version_ids=[v1['id'], v2['id']], start_date='2026-11-23',
                  passengers=80, max_vehicles=2, emission_scope='direct')
    response = client.post('/comparisons', json=fields)
    assert response.status_code == 201, response.text
    comparison = response.json()
    assert len(comparison['entries']) == 2
    assert comparison['shared']['comparison_kind'] == 'independent_homogeneous_cases'
    assert comparison['shared']['optimality_proven'] is False
    ids = [entry['run_id'] for entry in comparison['entries']]
    runs = [client.get(f'/runs/{ident}').json() for ident in ids]
    assert {run['snapshot']['scenario']['route']['distance_m'] for run in runs} == {132543}
    assert {run['snapshot']['scenario']['passengers'] for run in runs} == {80}
    assert {run['snapshot']['scenario']['emission_scope'] for run in runs} == {'direct'}
    assert {run['snapshot']['energy_version']['id'] for run in runs} == {diesel['id']}
    assert runs[0]['result']['totals']['eur_total'] != runs[1]['result']['totals']['eur_total']
    assert all(run['result']['status'] == 'feasible_not_proven' for run in runs)
    assert all(not run['result']['objective_proven_optimal'] for run in runs)
    assert len(client.get('/comparisons').json()) == 1
    assert client.get(f'/comparisons/{comparison["id"]}').json()['shared_sha256'] == comparison['shared_sha256']
    assert client.get(f'/runs/{ids[0]}/report.pdf?lang=en').content.startswith(b'%PDF')

    client.post('/energies', json={**energy(), 'price_per_unit': '42'})
    assert client.get(f'/comparisons/{comparison["id"]}').json()['entries'] == comparison['entries']
    client.headers.pop('Authorization')
    assert client.post('/public/session').status_code == 200
    assert client.get(f'/comparisons/{comparison["id"]}').status_code == 404
    assert client.get('/comparisons').json() == []
    assert client.post('/comparisons', json=fields).status_code == 404


def test_comparison_rejects_partial_invalid_selection(tmp_path):
    client, _, _ = client_with_route(tmp_path)
    v = client.post('/vehicles', json=vehicle()).json()
    quote = client.post('/routing/resolve', json={'origin': 'Caen', 'destination': 'Rouen'}).json()
    fields = dict(name='Essai multi',route_quote_id=quote['quote_id'],
                  vehicle_version_ids=[v['id'],v['id']],start_date='2026-11-23',passengers=20)
    assert client.post('/comparisons',json=fields).status_code == 422
    fields['vehicle_version_ids'] = [v['id'],'inconnu']
    assert client.post('/comparisons',json=fields).status_code == 422  # prix absent
    client.post('/energies',json=energy())
    assert client.post('/comparisons',json=fields).status_code == 404  # reference absente
    v2 = client.post('/vehicles',json={**vehicle(),'label':'Second bus','energy_code':'H2',
                                     'unit':'kg','usable_capacity':'50','reserve':'5'}).json()
    fields['vehicle_version_ids'] = [v['id'],v2['id']]
    assert client.post('/comparisons',json=fields).status_code == 422  # energie H2 absente
    assert client.get('/comparisons').json() == []
    assert client.get('/scenarios').json() == []


def test_infeasible_vehicle_still_displayed_in_comparison(tmp_path):
    client,_,_=client_with_route(tmp_path)
    client.post('/energies',json=energy())
    fit=client.post('/vehicles',json={**vehicle(),'usable_capacity':'100'}).json()
    not_fit=client.post('/vehicles',json={**vehicle(),'label':'Réservoir trop court',
                                          'usable_capacity':'20','reserve':'5'}).json()
    quote=client.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'}).json()
    response=client.post('/comparisons',json={
        'name':'Deux capacités','route_quote_id':quote['quote_id'],
        'vehicle_version_ids':[fit['id'],not_fit['id']],
        'start_date':'2026-11-23','passengers':50,'max_vehicles':2})
    assert response.status_code==201,response.text
    rows=response.json()['entries']
    assert rows[0]['result']['totals'] is not None
    assert rows[1]['status']=='infeasible_proven'
    assert rows[1]['result']['totals'] is None


def test_geoapify_route_modes_geometry_and_secret_never_logged(tmp_path):
    seen=[]
    def answer(request: httpx.Request):
        seen.append(request)
        return httpx.Response(200,json={'features':[{'type':'Feature',
           'properties':{'distance':128500.2,'time':6050.5},
           'geometry':{'type':'MultiLineString','coordinates':[
               [[-0.36,49.18],[0.15,49.26]],[[0.15,49.26],[1.1,49.44]]
           ]}}]})
    client=httpx.Client(transport=httpx.MockTransport(answer))
    provider=GeoapifyRoutingProvider('local-test-secret',client=client)
    route=provider.route((-0.36,49.18),(1.1,49.44),'bus')
    assert route.provider=='geoapify' and route.profile=='bus'
    assert route.distance_m==Decimal('128500.2')
    assert route.geometry['type']=='LineString'
    assert len(route.geometry['coordinates'])==3
    assert 'mode=bus' in str(seen[0].url)
    assert '49.1800000%2C-0.3600000' in str(seen[0].url)
    assert 'apiKey=local-test-secret' in str(seen[0].url)
    with pytest.raises(RoutingFailure):
        provider.route((-0.36,49.18),(1.1,49.44),'driving-car')
    bad=GeoapifyRoutingProvider('secret',client=httpx.Client(transport=httpx.MockTransport(
        lambda _:httpx.Response(403,text='apikey was invalid: SECRET'))))
    with pytest.raises(RoutingFailure) as info:
        bad.route((-0.36,49.18),(1.1,49.44),'truck')
    assert 'SECRET' not in str(info.value)


def test_local_operator_can_configure_api_but_other_users_cannot(tmp_path,monkeypatch):
    monkeypatch.delenv('SIMCO2_ROUTING_MODE',raising=False)
    monkeypatch.delenv('SIMCO2_GEOAPIFY_API_KEY',raising=False)
    monkeypatch.delenv('ORS_API_KEY',raising=False)
    client,login,settings=client_with_route(tmp_path)
    status=client.get('/routing/config')
    assert status.status_code==200
    assert status.json()['operator'] is True
    assert status.json()['configured']['geoapify'] is False
    saved=client.post('/routing/keys',json={'provider':'geoapify','key':'local-geoapify-secret-key'})
    assert saved.status_code==200,saved.text
    assert saved.json()['configured']['geoapify'] is True
    assert 'local-geoapify-secret-key' not in saved.text
    assert settings.path.exists() and 'local-geoapify-secret-key' in settings.path.read_text()
    changed=client.post('/routing/config',json={'provider':'geoapify','profile':'bus'})
    assert changed.status_code==200
    assert changed.json()['provider']=='geoapify'
    assert changed.json()['profile']=='bus'
    assert client.get('/routing/status').json()['provider']=='fixture' # injected router for tests
    client.headers.pop('Authorization')
    assert client.post('/public/session').status_code == 200
    assert client.get('/routing/config').status_code == 403
    assert client.post('/routing/keys',json={'provider':'ors','key':'bob-malicious-key'}).status_code==403
    assert client.delete('/routing/keys/geoapify').status_code==403
    assert 'local-geoapify-secret-key' not in client.get('/routing/config').text
    assert client.get('/routing/test').status_code==405
    client.headers['Authorization'] = 'Bearer ' + login('admin','test-operator-password-123')
    assert client.post('/routing/keys',json={'provider':'geoapify',
        'key':'another-example-key'},headers={'Host':'remote.example'}).status_code == 403


def test_selected_geoapify_bus_is_used_without_exposing_key(tmp_path, monkeypatch):
    from simco2.domain.contracts import RouteResult
    monkeypatch.delenv('SIMCO2_ROUTING_MODE', raising=False)
    monkeypatch.delenv('SIMCO2_GEOAPIFY_API_KEY', raising=False)
    settings = RoutingSettings(tmp_path / 'private-settings.json')
    settings.put_key('geoapify', 'a-test-key-not-for-publication')
    settings.select('geoapify', 'bus')
    invoked = []
    def fake_geoapify(self, origin, destination, profile, departure_time=None):
        invoked.append((origin,destination,profile))
        return RouteResult(Decimal('128500'),Decimal('7200'),'bus',
                           'geoapify','mock','2026-11-23T00:00:00Z',
                           geometry={'type':'LineString','coordinates':[list(origin),list(destination)]},
                           restrictions=('Not coach certified',))
    monkeypatch.setattr(GeoapifyRoutingProvider,'route',fake_geoapify)
    app=create_app(tmp_path/'dynamic.sqlite',geocoder=FakeGeocoder(),routing_settings=settings)
    app.state.db.create_user('admin','long-enough-test-password')
    c=TestClient(app)
    token=c.post('/auth/login',json={'username':'admin','password':'long-enough-test-password'}).json()['access_token']
    c.headers['Authorization']='Bearer '+token
    r=c.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'})
    assert r.status_code==200,r.text
    assert invoked[0][2]=='bus'
    assert r.json()['route']['profile']=='bus'
    assert r.json()['route']['provider']=='geoapify'
    assert 'a-test-key-not-for-publication' not in r.text
    assert 'a-test-key-not-for-publication' not in c.get('/routing/config').text
