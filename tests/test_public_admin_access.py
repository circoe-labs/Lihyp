"""Public access is password-free; configuration mutations require the admin bearer."""
from fastapi.testclient import TestClient
from simco2.api.app import create_app
from test_api import energy, vehicle


def test_anonymous_home_and_isolated_visitor_session(tmp_path):
    app = create_app(tmp_path / 'public.sqlite')
    c1 = TestClient(app)
    c2 = TestClient(app)
    home = c1.get('/')
    assert home.status_code == 200
    assert 'id="shell" class="shell"' in home.text
    assert c1.get('/energies').status_code == 401
    response = c1.post('/public/session')
    assert response.status_code == 200
    cookie = response.headers['set-cookie']
    assert 'httponly' in cookie.lower() and 'samesite=lax' in cookie.lower()
    assert c1.get('/energies').status_code == 200
    assert c1.get('/vehicles').status_code == 200
    assert c1.post('/energies', json=energy()).status_code == 403
    assert c1.post('/vehicles', json=vehicle()).status_code == 403
    assert c1.get('/routing/config').status_code == 403
    assert c1.post('/routing/config', json={'provider':'osrm_demo','profile':'driving-car'}).status_code == 403
    assert c1.post('/routing/keys', json={'provider':'ors','key':'not-a-real-secret'}).status_code == 403
    assert c1.post('/routing/test', json={'origin':[1,2], 'destination':[3,4]}).status_code == 403
    assert c1.post('/routing/preview', json={'origin':[1,2], 'destination':[3,4]}).status_code == 403
    assert c1.post('/public/session').status_code == 200  # refresh uses same visitor
    assert c2.post('/public/session').status_code == 200
    assert c1.get('/auth/me').json()['id'] != c2.get('/auth/me').json()['id']


def test_admin_must_log_in_explicitly_and_can_update_catalogues(tmp_path):
    app=create_app(tmp_path / 'admin.sqlite')
    app.state.db.create_user('admin', 'a-very-long-administrator-password')
    c=TestClient(app)
    assert c.post('/auth/login', json={'username':'missing','password':'a-long-password'}).status_code==401
    assert c.post('/auth/login', json={'username':'admin','password':'not-the-password'}).status_code==401
    token=c.post('/auth/login', json={'username':'admin','password':'a-very-long-administrator-password'}).json()['access_token']
    c.headers['Authorization']='Bearer '+token
    assert c.get('/routing/config').status_code==200
    assert c.post('/energies',json=energy()).status_code==201
    assert c.post('/vehicles',json=vehicle()).status_code==201
    assert c.get('/audit').status_code==200
    c.headers.pop('Authorization')
    assert c.post('/public/session').status_code==200
    assert c.get('/energies').status_code==200
    assert c.get('/routing/config').status_code==403


def test_admin_password_rotation_revokes_tokens(tmp_path):
    app=create_app(tmp_path/'rotate.sqlite')
    db=app.state.db
    db.create_user('admin','an-original-very-long-password')
    c=TestClient(app)
    response=c.post('/auth/login',json={'username':'admin','password':'an-original-very-long-password'})
    assert response.status_code==200
    token=response.json()['access_token']
    db.update_password('admin','a-new-very-long-password-2026')
    c.headers['Authorization']='Bearer '+token
    assert c.get('/routing/config').status_code==401
    assert c.post('/auth/login',json={'username':'admin','password':'an-original-very-long-password'}).status_code==401
    assert c.post('/auth/login',json={'username':'admin','password':'a-new-very-long-password-2026'}).status_code==200


def test_public_throttle_is_enforced(tmp_path):
    db=create_app(tmp_path/'throttle.sqlite').state.db
    for _ in range(2):
        db.consume_public_quota('127.0.0.1', 'route', 2)
    from simco2.domain.errors import DomainError
    import pytest
    with pytest.raises(DomainError) as info:
        db.consume_public_quota('127.0.0.1','route',2)
    assert info.value.code=='too_many_attempts'
