"""Deterministic automatic refuel search: fixture data only, no live providers."""
from test_service_day_api import login_client, DayRouter, CAEN, ROUEN, STATION
from test_api import energy, vehicle
from simco2.adapters.station_optimization import route_candidates


class FakeFuelStations:
    def __init__(self, available=True):
        self.calls = []
        self.available = available

    def page(self, offset, limit, area="normandy"):
        self.calls.append((offset, limit, area))
        stations = ([{"id": "gazole-test", "name": "Station gazole d'essai", "longitude": STATION[0],
                     "latitude": STATION[1], "energy_codes": ["Gazole", "SP95"],
                     "source": "Fixture DGCCRF", "bus_compatibility": "not_confirmed"}]
                    if self.available else [])
        return {"stations": stations, "has_more": False, "unavailable": not self.available}


def _comparison(c, v1, v2, *, flow="30", fleet=1, policy="automatic"):
    q = c.post('/routing/resolve', json={'origin': 'Caen', 'destination': 'Rouen'}).json()
    r = c.post('/comparisons', json={
        'name': 'Comparatif stations auto', 'route_quote_id': q['quote_id'],
        'vehicle_version_ids': [v1, v2], 'start_date': '2026-11-23',
        'passengers': 80, 'max_vehicles': fleet, 'window_start': '08:00',
        'window_end': '18:00', 'day_plan': True, 'station_policy': policy,
        'diesel_flow_l_per_min': flow, 'handling_minutes': '2',
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_automatic_station_is_routed_and_selected_per_diesel_solution(tmp_path):
    c, _ = login_client(tmp_path)
    directory = FakeFuelStations()
    c.app.state.fuel_directory = directory
    c.post('/energies', json=energy())
    v1 = c.post('/vehicles', json={**vehicle(), 'label': 'Diesel 50 L',
                                   'usable_capacity': '50'}).json()
    v2 = c.post('/vehicles', json={**vehicle(), 'label': 'Diesel sobre',
                                   'usable_capacity': '50',
                                   'consumption_per_km': '0.1'}).json()
    result = _comparison(c, v1['id'], v2['id'])
    assert directory.calls == [(0, 100, 'normandy')]
    assert result['shared']['day_station_policy'] == 'automatic'
    assert result['shared']['day_station'] is None
    options = result['shared']['day_station_options']['DIESEL']
    assert len(options) == 1
    assert options[0]['station']['id'] == 'gazole-test'
    assert options[0]['to_station']['distance_m'] == '10000'
    first, second = (e['result'] for e in result['entries'])
    assert first['totals']['refuel_count'] == 1
    assert first['totals']['vehicles_used'] == 1
    assert first['totals']['rotations_per_vehicle'] == {'V001': 2}
    events = first['vehicles'][0]['events']
    assert [x['kind'] for x in events] == ['service', 'station_detour', 'refuel',
                                         'handling', 'deadhead_return', 'service']
    assert events[2]['station_id'] == 'gazole-test'
    assert events[2]['station_name'] == "Station gazole d'essai"
    assert first['totals']['duration_wait_s'] == '0'
    assert second['totals']['refuel_count'] == 0
    # A later price change must not rewrite old schedules.
    old = c.get('/comparisons/'+result['id']).json()
    c.post('/energies', json={**energy(), 'price_per_unit':'9'})
    assert c.get('/comparisons/'+result['id']).json()['entries'] == old['entries']


def test_no_station_or_zero_flow_never_invents_a_refuel(tmp_path):
    c, _ = login_client(tmp_path)
    directory = FakeFuelStations(False)
    c.app.state.fuel_directory = directory
    c.post('/energies', json=energy())
    v1 = c.post('/vehicles', json={**vehicle(), 'label': 'Diesel A',
                                   'usable_capacity': '50'}).json()
    v2 = c.post('/vehicles', json={**vehicle(), 'label': 'Diesel B',
                                   'usable_capacity': '50'}).json()
    group = _comparison(c, v1['id'], v2['id'], fleet=2)
    assert group['shared']['day_station_options']['DIESEL'] == []
    assert all(e['result']['totals']['vehicles_used'] == 2 for e in group['entries'])
    assert all(e['result']['totals']['refuel_count'] == 0 for e in group['entries'])
    assert group['entries'][0]['result']['totals']['duration_wait_s'] == '0'
    # No flow rate => don't even query stations, and don't silently assume one.
    directory.calls.clear()
    no_flow = _comparison(c, v1['id'], v2['id'], flow='0', fleet=2)
    assert directory.calls == []
    assert all(e['result']['totals']['refuel_count'] == 0 for e in no_flow['entries'])


def test_candidate_search_excludes_incompatible_energy_and_forged_routes():
    quote = {'origin_coordinates': CAEN, 'destination_coordinates': ROUEN,
             'profile': 'driving-car', 'provider': 'osrm_demo'}
    candidates = [
        {'id':'hydrogen-only','name':'H2 test','longitude':STATION[0],
         'latitude':STATION[1], 'energy_codes':['H2']},
        {'id':'diesel','name':'Diesel test','longitude':STATION[0],
         'latitude':STATION[1], 'energy_codes':['Gazole']},
    ]
    opts,warnings = route_candidates(DayRouter(),quote,candidates,{'DIESEL'})
    assert [s['station']['id'] for s in opts['DIESEL']] == ['diesel']
    assert opts['DIESEL'][0]['station']['energy_codes'] == ['DIESEL']
    assert all(s['station']['id'] != 'hydrogen-only' for s in opts['DIESEL'])


def test_imposed_h2_station_cannot_be_used_for_diesel_models(tmp_path):
    c, _ = login_client(tmp_path)
    c.post('/energies', json=energy())
    v1 = c.post('/vehicles', json={**vehicle(), 'label': 'Diesel 1'}).json()
    v2 = c.post('/vehicles', json={**vehicle(), 'label': 'Diesel 2'}).json()
    q = c.post('/routing/resolve', json={'origin':'Caen','destination':'Rouen'}).json()
    payload = {'name':'Incompatibilite', 'route_quote_id':q['quote_id'],
               'vehicle_version_ids':[v1['id'],v2['id']],
               'start_date':'2026-11-23','passengers':80,'day_plan':True,
               'station_policy':'imposed',
               'refuel_station':{'id':'h2-only','name':'H2 incompatible',
                                 'longitude':STATION[0],'latitude':STATION[1],
                                 'energy_codes':['H2'],'source':'Fixture H2 only'}}
    r = c.post('/comparisons', json=payload)
    assert r.status_code == 422, r.text
    assert r.json()['error']['code'] == 'station_energy_incompatible'
    assert c.get('/comparisons').json()==[]
    # An explicitly automatic request ignores an obsolete manual station field.
    payload['station_policy']='automatic'
    payload['max_vehicles']=2
    payload['diesel_flow_l_per_min']='0'
    accepted = c.post('/comparisons', json=payload)
    assert accepted.status_code==201, accepted.text
    assert accepted.json()['shared']['day_station'] is None
    assert accepted.json()['shared']['day_station_policy']=='automatic'
