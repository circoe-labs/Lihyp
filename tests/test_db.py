from simco2.adapters.db import Database
from simco2.domain.errors import DomainError, MissingReference
import pytest


def test_versioned_energy_audit_and_no_prices_on_station(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    db.setup()
    actor = db.create_user("a", "this-is-a-very-long-pass")
    eid = dict(country_iso="FR", energy_code="DIESEL", unit="L",
               price_per_unit="2", factors={"direct": "2.7"},
               source="Données synthétiques de test", source_date="2026-01-01")
    v1 = db.append_energy(eid, actor)
    v2 = db.append_energy({**eid, "price_per_unit": "3"}, actor)
    assert db.get_energy(v1["id"])["payload"]["price_per_unit"] == "2"
    assert db.get_energy(v2["id"])["revision"] == 2
    assert db.list_energies("FR")[0]["revision"] == 2
    assert db.audit_for(actor)
    assert db.energy_catalog()["energy_types"]
    with pytest.raises(DomainError):
        db.append_station({"name": "x", "price_per_l": "1"}, actor)
    with pytest.raises(MissingReference):
        db.get_energy("nope")


def test_tokens_and_user_separation(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    db.setup()
    a = db.create_user("alice", "long-unique-passphrase-1")
    b = db.create_user("bob", "long-unique-passphrase-2")
    _, token = db.authenticate("alice", "long-unique-passphrase-1")
    assert db.actor_for_token(token)["id"] == a
    db.revoke_token(token)
    assert db.actor_for_token(token) is None
    with pytest.raises(DomainError):
        db.authenticate("alice", "wrong")
    scenario = db.create_scenario({"name": "test"}, a)
    with pytest.raises(MissingReference):
        db.get_scenario(scenario["id"], b)


def test_station_multi_equipment_and_db_immutable_revisions(tmp_path):
    import sqlite3
    db = Database(tmp_path / 'db.sqlite')
    db.setup()
    actor = db.create_user('third', 'long-passphrase-third')
    s = db.append_station({'name': 'Station démonstration',
        'equipments': [{'energy_code': 'ELECTRIC', 'connector': 'CCS', 'ports': 2},
                       {'energy_code': 'H2', 'connector': 'H70', 'ports': 1}],
        'source': 'Fixture non vérifiée'}, actor)
    assert len(db.list_stations()[0]['payload']['equipments']) == 2
    with db.session() as con:
        with pytest.raises(sqlite3.IntegrityError):
            con.execute('UPDATE station_versions SET payload_json=? WHERE id=?', ('{}', s['id']))


def test_station_subrecords_are_immutable(tmp_path):
    import sqlite3
    db = Database(tmp_path / 'db.sqlite')
    db.setup()
    actor = db.create_user('stations', 'long-passphrase-stations')
    station = db.append_station({'name':'Station fictive',
        'latitude': '49.1', 'longitude': '0.2',
        'access': 'public', 'operational_status':'unverified',
        'source':'Fixture hypothétique', 'observed_at':'2026-11-20',
        'equipments': [{'energy_code':'ELECTRIC','connector':'CCS','ports':2}]}, actor)
    with db.session() as con:
        with pytest.raises(sqlite3.IntegrityError):
            con.execute('UPDATE station_coordinates SET latitude=? WHERE station_version_id=?',
                        ('0', station['id']))
        with pytest.raises(sqlite3.IntegrityError):
            con.execute('DELETE FROM station_equipments WHERE station_version_id=?',
                        (station['id'],))


def test_login_attempts_rate_limited_and_login_audited(tmp_path):
    db = Database(tmp_path / 'db.sqlite')
    db.setup()
    user_id = db.create_user('limited', 'strong-password-test-01')
    for i in range(5):
        with pytest.raises(DomainError) as ex:
            db.authenticate('limited', 'bad-password', '192.0.2.1')
        assert ex.value.code == 'invalid_credentials'
    with pytest.raises(DomainError) as ex:
        db.authenticate('limited', 'strong-password-test-01', '192.0.2.1')
    assert ex.value.code == 'too_many_attempts'
    uid, token = db.authenticate('limited', 'strong-password-test-01', '192.0.2.2')
    assert uid == user_id
    assert any(e['action'] == 'login' for e in db.audit_for(user_id))


def test_emission_factors_are_normalized_and_versioned(tmp_path):
    db = Database(tmp_path / 'db.sqlite')
    db.setup()
    actor = db.create_user('factory', 'long-passphrase-factory')
    row = db.append_energy(dict(country_iso='FR',energy_code='DIESEL',unit='L',
        price_per_unit='1.8',factors={'direct':'2.7','well_to_wheel':'3.3'},
        source='Hypothèse test',source_date='2026-01-01'), actor)
    with db.session() as con:
        factors = con.execute('SELECT perimeter, kgco2e_per_unit FROM emission_factors WHERE energy_version_id=?',
                              (row['id'],)).fetchall()
        assert {x['perimeter']:x['kgco2e_per_unit'] for x in factors} == {
            'direct':'2.7','well_to_wheel':'3.3'}


def test_station_source_may_mention_tariffs_without_station_pricing(tmp_path):
    db = Database(tmp_path / 'db.sqlite')
    db.setup()
    a = db.create_user('user1', 'long-password-station')
    station = db.append_station({'name': 'Station témoin',
        'source': 'Source sur les tarifs nationaux, non vérifiée'}, a)
    assert station['payload']['name'] == 'Station témoin'
