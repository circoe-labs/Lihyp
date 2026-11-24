"""Conservative planning, no queues, auditable return and station detours."""
from datetime import datetime
from decimal import Decimal

from simco2.domain.service_day import schedule_day


def fixture(*, station=True, fleet=1, capacity='50', end='18:00'):
    route={"origin":"Caen","destination":"Rouen", "distance_m":100000,
           "duration_s":7200,"provider":"fixture_test_only", "source":"Test"}
    vehicle={"label":"Diesel fictif", "energy_code":"DIESEL", "unit":"L",
             "seats":50,"consumption_per_km":"0.2","consumption_per_hour":"0",
             "usable_capacity":capacity,"reserve":"5", "maintenance_eur_per_km":"0",
             "labor_eur_per_h":"0","purchase_eur":"0","residual_eur":"0",
             "life_years":10,"insurance_eur_year":"0", "source":"synthetic"}
    return {
        "scenario_revision_id":"s1","vehicle_version":{"id":"v1","payload":vehicle},
        "energy_version":{"id":"e1","payload":{"country_iso":"FR", "energy_code":"DIESEL",
            "unit":"L","price_per_unit":"2","factors":{"direct":"2.7"},"source":"fixture", "source_date":"2026-01-01"}},
        "scenario":{"name":"Fixture", "country_iso":"FR", "start_date":"2026-11-23",
            "end_date":"2026-11-23","timezone":"Europe/Paris", "route":route,
            "window_start":"08:00","window_end":end,"passengers":80,
            "max_vehicles":fleet,"network_mode":"single","depot_mode":"none",
            "tco_scope":"variable", "emission_scope":"direct"},
        "day_legs":{"reverse":{"distance_m":"100000","duration_s":"7500","provider":"fixture_test_only"},
           "via_station":{"to_station":{"distance_m":"10000","duration_s":"600"},
                          "from_station":{"distance_m":"90000","duration_s":"6500"}}},
        "day_station":{"id":"fuel-demo","name":"Test","energy_codes":["DIESEL"],
            "longitude":1.1,"latitude":49.3,"source":"Fixture, not live"} if station else None,
        "day_refuel_rates_per_min":{"DIESEL":"30"},"day_handling_minutes":"2",
    }


def test_refuel_with_no_wait_and_separate_return_leg():
    x=schedule_day(fixture()).result
    assert x['status']=='feasible_not_proven'
    assert x['totals']['vehicles_used']==1
    assert x['totals']['refuel_count']==1
    assert x['totals']['duration_wait_s']=='0'
    assert Decimal(x['totals']['duration_refuel_s']) == Decimal(44)
    assert x['totals']['duration_handling_s']=='120'
    assert x['totals']['distance_passenger_m']=='200000'
    assert x['totals']['distance_empty_m']=='100000'
    assert Decimal(x['totals']['energy_consumed'])==Decimal('60')
    assert Decimal(x['totals']['eur_total'])==Decimal('120')
    assert len(x['trips'])==2
    events=x['vehicles'][0]['events']
    assert [e['kind'] for e in events]==[
        'service','station_detour','refuel','handling','deadhead_return','service']
    assert Decimal(x['totals']['duration_elapsed_s'])==Decimal('21664')
    assert Decimal(x['totals']['duration_vehicle_s'])==Decimal('21664')
    assert all(e['end_utc']<=events[i+1]['start_utc'] for i,e in enumerate(events[:-1]))
    assert len({row['vehicle_instance'] for row in x['trips']}) == 1


def test_without_station_two_coaches_work_in_parallel_and_no_refuel():
    x=schedule_day(fixture(station=False,fleet=2)).result
    assert x['totals']['vehicles_used']==2
    assert x['totals']['refuel_count']==0
    assert x['totals']['duration_elapsed_s']=='7200.0'
    assert x['totals']['duration_vehicle_s']=='14400'
    assert x['totals']['duration_wait_s']=='0'
    assert x['totals']['distance_empty_m']=='0'
    assert len(x['vehicles'])==2


def test_not_proven_infeasible_when_greedy_cannot_schedule():
    x=schedule_day(fixture(station=False,fleet=1)).result
    assert x['status']=='no_solution_found'
    assert x['totals'] is None
    assert 'prouve' in x['constraints'][0]['message']


def test_do_not_invent_station_flow_or_ignore_energy_capacity():
    data=fixture()
    data['day_refuel_rates_per_min']={'DIESEL':'0'}
    assert schedule_day(data).result['status']=='no_solution_found'
    data=fixture(capacity='20')
    assert schedule_day(data).result['status']=='infeasible_proven'


def test_window_is_end_of_service_and_no_crossing_midnight():
    data=fixture(end='10:00')
    assert schedule_day(data).result['status']=='no_solution_found'
    data=fixture(end='07:00')
    assert schedule_day(data).result['status']=='invalid_input'


def test_route_details_have_to_be_sourced_not_mirrored():
    data=fixture()
    data['day_legs'].pop('reverse')
    assert schedule_day(data).result['status']=='invalid_input'


def test_automatic_station_choice_uses_routed_duration_and_no_wait():
    data=fixture(station=False)
    data['day_station_policy']='automatic'
    data['day_legs'].pop('via_station')
    data['day_station_options']={'DIESEL':[
        {'station':{'id':'slow','name':'Slow valid fuel station', 'energy_codes':['DIESEL']},
         'to_station':{'distance_m':'10000','duration_s':'1100'},
         'from_station':{'distance_m':'90000','duration_s':'7200'}},
        {'station':{'id':'fast','name':'Fast valid fuel station', 'energy_codes':['DIESEL']},
         'to_station':{'distance_m':'10000','duration_s':'600'},
         'from_station':{'distance_m':'90000','duration_s':'6500'}}]}
    result=schedule_day(data).result
    assert result['status']=='feasible_not_proven'
    assert result['totals']['refuel_count']==1
    assert result['totals']['duration_wait_s']=='0'
    events=result['vehicles'][0]['events']
    fuel=[e for e in events if e['kind']=='refuel']
    assert len(fuel)==1
    assert fuel[0]['station_id']=='fast'
    assert fuel[0]['station_name']=='Fast valid fuel station'
    assert result['totals']['rotations_per_vehicle']=={'V001':2}
