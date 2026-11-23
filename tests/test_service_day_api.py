"""Compare two coaches on one server-routed day; persist defensible time journals."""
from decimal import Decimal

from fastapi.testclient import TestClient

from simco2.api.app import create_app
from simco2.domain.contracts import RouteResult
from simco2.domain.errors import RoutingFailure
from test_api import energy, vehicle
from test_discovery_and_resolved_routing import FakeGeocoder


CAEN = (-0.362, 49.183)
ROUEN = (1.099, 49.443)
STATION = (0.5, 49.30)


class DayRouter:
    def route(self, origin, destination, profile):
        routes = {
            (CAEN, ROUEN): (100000, 7200),
            (ROUEN, CAEN): (100000, 7500),
            (ROUEN, STATION): (10000, 600),
            (STATION, CAEN): (90000, 6500),
        }
        if (tuple(origin), tuple(destination)) not in routes:
            raise RoutingFailure('no_leg','Itineraire inexistant dans la fixture')
        assert profile == 'driving-car'
        length, seconds = routes[(tuple(origin), tuple(destination))]
        return RouteResult(Decimal(length), Decimal(seconds), profile, 'osrm_demo',
                           'fixture-v1', '2026-11-23T08:00:00Z',
                           geometry={'type':'LineString', 'coordinates':[list(origin), list(destination)]},
                           restrictions=('Synthetic for tests only',))


def login_client(tmp_path):
    app = create_app(tmp_path/'day.sqlite', geocoder=FakeGeocoder(), routing_provider=DayRouter())
    app.state.db.create_user('alice', 'secure-passphrase-for-tests')
    app.state.db.create_user('bob', 'another-secure-passphrase')
    c=TestClient(app)
    def token(username,password):
        return c.post('/auth/login',json={'username':username,'password':password}).json()['access_token']
    c.headers['Authorization']='Bearer '+token('alice','secure-passphrase-for-tests')
    return c, token


def test_real_day_schedule_and_snapshot_are_saved(tmp_path):
    c, token=login_client(tmp_path)
    c.post('/energies',json=energy())
    v1=c.post('/vehicles',json={**vehicle(),'label':'Autocar 50 L',
        'usable_capacity':'50'}).json()
    v2=c.post('/vehicles',json={**vehicle(),'label':'Autocar plus sobre',
        'usable_capacity':'50','consumption_per_km':'0.1'}).json()
    quote=c.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'}).json()
    fields={
        'name':'Journée test', 'route_quote_id':quote['quote_id'],
        'vehicle_version_ids':[v1['id'],v2['id']],
        'start_date':'2026-11-23', 'passengers':80,
        'window_start':'08:00','window_end':'18:00','max_vehicles':1,
        'day_plan':True, 'diesel_flow_l_per_min':'30','handling_minutes':'2',
        'refuel_station':{'id':'station-test','name':'Station test',
            'longitude':STATION[0],'latitude':STATION[1],
            'energy_codes':['Gazole','SP95'], 'source':'Test DGCCRF fictif'},
    }
    response=c.post('/comparisons',json=fields)
    assert response.status_code==201, response.text
    group=response.json()
    assert group['shared']['day_plan'] is True
    assert group['shared']['day_legs']['reverse']['duration_s']=='7500'
    assert group['shared']['day_station']['energy_codes']==['DIESEL','SP95']
    entries=group['entries']
    assert len(entries)==2
    assert entries[0]['result']['totals']['refuel_count']==1
    assert entries[0]['result']['totals']['duration_wait_s']=='0'
    assert entries[0]['result']['totals']['vehicles_used']==1
    assert entries[1]['result']['totals']['refuel_count']==0
    run=c.get('/runs/'+entries[0]['run_id']).json()
    assert run['snapshot']['day_legs']['via_station']['to_station']['distance_m']=='10000'
    assert run['snapshot']['day_station']['name']=='Station test'
    assert run['result']['vehicles'][0]['events'][2]['kind']=='refuel'
    # Changing a national price does not alter saved comparison snapshots.
    c.post('/energies',json={**energy(),'price_per_unit':'45'})
    assert c.get('/comparisons/'+group['id']).json()['entries']==entries
    c.headers['Authorization']='Bearer '+token('bob','another-secure-passphrase')
    assert c.get('/comparisons/'+group['id']).status_code==404


def test_return_route_is_required_and_no_unverified_fallback(tmp_path):
    c,_=login_client(tmp_path)
    c.post('/energies',json=energy())
    v1=c.post('/vehicles',json=vehicle()).json()
    v2=c.post('/vehicles',json={**vehicle(),'label':'Autre'}).json()
    quote=c.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'}).json()
    # Non-existent station coordinates: no fabricated reverse/station legs.
    r=c.post('/comparisons',json={'name':'Station hors route',
        'route_quote_id':quote['quote_id'],'vehicle_version_ids':[v1['id'],v2['id']],
        'start_date':'2026-11-23','passengers':80,'day_plan':True,
        'refuel_station':{'id':'s1','name':'Imaginaire','longitude':2.1,
            'latitude':48.0,'energy_codes':['Gazole'],'source':'Source fictive'}})
    assert r.status_code in (422,503)
    assert c.get('/comparisons').json()==[]


def test_station_rates_must_be_nonnegative_and_snapshot_is_not_modified(tmp_path):
    c,_=login_client(tmp_path)
    c.post('/energies',json=energy())
    v1=c.post('/vehicles',json=vehicle()).json()
    v2=c.post('/vehicles',json={**vehicle(),'label':'Autre'}).json()
    quote=c.post('/routing/resolve',json={'origin':'Caen','destination':'Rouen'}).json()
    r=c.post('/comparisons',json={'name':'Debit negatif',
        'route_quote_id':quote['quote_id'],'vehicle_version_ids':[v1['id'],v2['id']],
        'start_date':'2026-11-23','passengers':80,'day_plan':True,
        'diesel_flow_l_per_min':'-1'})
    assert r.status_code==422
    assert c.get('/comparisons').json()==[]
