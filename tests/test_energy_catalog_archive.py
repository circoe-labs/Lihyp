"""Energy catalogue administration must never delete historical prices/factors."""
from fastapi.testclient import TestClient
from simco2.api.app import create_app


def test_energy_archive_is_reversible_and_keeps_versions(tmp_path):
    app=create_app(tmp_path/'archival.sqlite')
    db=app.state.db
    user=db.create_user('catalogue-admin','sufficiently-long-password-123')
    payload={'country_iso':'FR','energy_code':'DIESEL','unit':'L',
             'price_per_unit':'2','factors':{'direct':'2.7'},
             'source':'Synthetic testing fixture','source_date':'2026-11-23'}
    original=db.append_energy(payload,user)
    assert len(db.list_energies('FR'))==1
    db.archive_energy('FR','DIESEL',user)
    assert db.list_energies('FR')==[]
    assert db.get_energy(original['id'])['payload']['price_per_unit']=='2'
    assert db.energy_history('FR','DIESEL')[0]['id']==original['id']
    db.append_energy({**payload,'price_per_unit':'2.5'},user)
    assert db.list_energies('FR')[0]['revision']==2
    assert db.energy_history('FR','DIESEL')[1]['id']==original['id']
    assert 'archive_from_catalogue' in [x['action'] for x in db.audit_for(user)]


def test_archival_api_authenticated_and_does_not_delete_versions(tmp_path):
    app=create_app(tmp_path/'api.sqlite')
    db=app.state.db
    db.create_user('admin','a-long-enough-password')
    token=TestClient(app).post('/auth/login',json={'username':'admin','password':'a-long-enough-password'}).json()['access_token']
    headers={'Authorization':f'Bearer {token}'}
    client=TestClient(app)
    created=client.post('/energies',json={'country_iso':'FR','energy_code':'H2','unit':'kg',
      'price_per_unit':'10','factors':{},'source':'Synthetic fixture data',
      'license':'not for production','source_date':'2026-11-23','quality':'unverified'},headers=headers)
    assert created.status_code==201,created.text
    assert client.post('/energies/FR/H2/archive').status_code==401
    res=client.post('/energies/FR/H2/archive',headers=headers)
    assert res.status_code==204,res.text
    assert client.get('/energies',headers=headers).json()==[]
    assert len(client.get('/energies/FR/H2/versions',headers=headers).json())==1
