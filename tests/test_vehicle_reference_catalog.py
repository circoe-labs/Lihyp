"""Nine user-provided coach references: prices and technical specs are not certified."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from simco2.api.app import create_app
from simco2.api.schemas import EnergyInput, VehicleInput

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/'src/simco2/ui/vehicle-reference-catalog.json'


def test_nine_reference_specs_and_cost_ranges_are_retained():
    data=json.loads(CATALOG.read_text(encoding='utf-8'))
    entries=data['entries']
    assert len(entries)==9 and len({e['id'] for e in entries})==9
    assert sorted({e['energy_code'] for e in entries})==['BIOGNV','DIESEL','ELECTRIC','H2']
    assert entries[0]['label']=='Autocar Diesel Standard (12m)'
    assert entries[0]['manufacturer']=='Iveco Bus'
    assert entries[0]['model']=='Crossway Line 12m'
    assert entries[0]['purchase_eur_ht']==[230000,250000]
    assert entries[0]['energy_cost_100km_eur_ht']==[39,48]
    assert entries[7]['purchase_scope']=='retrofit_kit_installation'
    assert entries[8]['purchase_eur_ht']==[650000,750000]
    expected=[(55,0.26,310,25),(63,0.28,350,30),(55,0.30,200,15),
              (63,0.32,250,20),(59,0.95,315,25),(55,1.0,375,30),
              (63,1.05,380,30),(55,0.07,38.2,3),(59,0.085,51.2,4)]
    assert [(e['seats'],e['consumption_per_km'],e['usable_capacity'],e['reserve']) for e in entries]==expected
    assert all(e['consumption_per_hour']==0 and e['technical_quality']=='user_supplied_unverified' for e in entries)
    assert all(e['technical_source'] and e['capacity_details'] for e in entries)
    assert entries[7]['model']=='Crossway H2 Rétrofit'


def test_nine_user_specifications_validate_as_vehicle_inputs():
    for e in json.loads(CATALOG.read_text(encoding='utf-8'))['entries']:
        vehicle=VehicleInput.model_validate({
            'label':e['label'],'manufacturer':e['manufacturer'],'model':e['model'],
            'seats':e['seats'],'energy_code':e['energy_code'],'unit':e['unit'],
            'consumption_per_km':str(e['consumption_per_km']),
            'consumption_per_hour':str(e['consumption_per_hour']),
            'usable_capacity':str(e['usable_capacity']),'reserve':str(e['reserve']),
            'source':e['technical_source']+' - données utilisateur non vérifiées',
        })
        assert vehicle.quality=='unverified'
        assert vehicle.seats==e['seats']


def test_biognv_unit_is_kg():
    energy=dict(country_iso='FR',energy_code='BIOGNV',unit='kg',price_per_unit='1.65',
                factors={'direct':'0'},source='Hypothèse de test non vérifiée',source_date='2026-11-24')
    assert EnergyInput.model_validate(energy).unit=='kg'
    with pytest.raises(ValidationError):
        EnergyInput.model_validate({**energy,'unit':'L'})


def test_reference_asset_visible_without_automatic_creation(tmp_path):
    app=create_app(tmp_path/'catalogue.sqlite')
    app.state.db.create_user('analyste','this-is-an-adequately-long-secret')
    client=TestClient(app)
    r=client.get('/assets/vehicle-reference-catalog.json')
    assert r.status_code==200 and len(r.json()['entries'])==9
    token=client.post('/auth/login',json={'username':'analyste','password':'this-is-an-adequately-long-secret'}).json()['access_token']
    client.headers.update({'Authorization':f'Bearer {token}'})
    assert client.get('/vehicles').json()==[]
    item=r.json()['entries'][0]
    payload={
        'label':item['label'],'manufacturer':item['manufacturer'],'model':item['model'],
        'seats':item['seats'],'energy_code':item['energy_code'],'unit':item['unit'],
        'consumption_per_km':str(item['consumption_per_km']),
        'consumption_per_hour':str(item['consumption_per_hour']),
        'usable_capacity':str(item['usable_capacity']),'reserve':str(item['reserve']),
        'source':'Données utilisateur non vérifiées [LIHYP-REF:diesel-12]',
    }
    result=client.post('/vehicles',json=payload)
    assert result.status_code==201,result.text
    assert client.get('/vehicles').json()[0]['payload']['seats']==55


def test_interface_allows_explicit_registration_and_review():
    js=(ROOT/'src/simco2/ui/app.js').read_text(encoding='utf-8')
    html=(ROOT/'src/simco2/ui/index.html').read_text(encoding='utf-8')
    assert 'id="reference-library"' in html
    assert 'data-add-reference' in js and 'data-prefill-reference' in js
    assert 'seats:String(e.seats),consumption_per_km:String(e.consumption_per_km)' in js
    assert 'usable_capacity:String(e.usable_capacity),reserve:String(e.reserve)' in js
    assert "quality:'unverified'" in js
    assert "purchase_scope==='vehicle'" in js
    assert 'referenceExists(e)' in js
    assert 'referenceMissingEnergy' in js
