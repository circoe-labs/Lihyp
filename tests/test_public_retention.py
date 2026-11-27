"""Fixed 20-minute public workspaces; permanent admin records never purged."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import sqlite3

import pytest
from fastapi.testclient import TestClient

from simco2.adapters.db import Database
from simco2.api.app import create_app


def _records(db, owner):
    scenario = db.create_scenario({"name": "Rotation de test"}, owner)
    revision = scenario["latest_revision"]["id"]
    run_id, comparison_id = str(uuid4()), str(uuid4())
    with db.session() as con:
        con.execute("INSERT INTO simulation_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (run_id, revision, owner, "{}", "x" * 64, "{}", "ok",
                     datetime.now(timezone.utc).isoformat()))
        con.execute("INSERT INTO comparison_groups VALUES (?, ?, ?, ?, ?, ?)",
                    (comparison_id, owner, "Essai", "{}", "x" * 64,
                     datetime.now(timezone.utc).isoformat()))
        con.execute("INSERT INTO comparison_members VALUES (?, ?, ?)",
                    (comparison_id, run_id, 0))
    quote_id = db.save_route_quote(owner, {"geometry": "demo"})
    return scenario["id"], revision, run_id, comparison_id, quote_id


def test_guest_deleted_everywhere_without_touching_admin(tmp_path):
    db = Database(tmp_path / "retention.sqlite")
    db.setup()
    admin = db.create_user("admin", "long-administrator-password")
    guest, token = db.create_guest()
    active_guest, active_token = db.create_guest()
    temporary = _records(db, guest)
    permanent = _records(db, admin)
    with db.session() as con:
        con.execute("UPDATE users SET created_at=? WHERE id=?",
                    ((datetime.now(timezone.utc) - timedelta(minutes=21)).isoformat(), guest))
    assert db.actor_for_token(token) is None  # immediate authorization expiry
    assert db.actor_for_token(active_token) is not None
    assert db.cleanup_expired_guests() == 1
    assert db.cleanup_expired_guests() == 0  # idempotent
    with db.session() as con:
        for table, query in [
            ("scenarios", "id"), ("scenario_revisions", "id"),
            ("simulation_runs", "id"), ("comparison_groups", "id"),
            ("route_quotes", "id"),
        ]:
            idx = {"scenarios":0, "scenario_revisions":1, "simulation_runs":2,
                   "comparison_groups":3, "route_quotes":4}[table]
            assert con.execute(f"SELECT 1 FROM {table} WHERE {query}=?", (temporary[idx],)).fetchone() is None
            assert con.execute(f"SELECT 1 FROM {table} WHERE {query}=?", (permanent[idx],)).fetchone()
        assert con.execute("SELECT COUNT(*) FROM comparison_members WHERE comparison_id=?",
                           (temporary[3],)).fetchone()[0] == 0
        assert con.execute("SELECT 1 FROM users WHERE id=?", (guest,)).fetchone() is None
        assert con.execute("SELECT 1 FROM users WHERE id=?", (active_guest,)).fetchone()
        assert con.execute("SELECT COUNT(*) FROM audit_events WHERE actor_id=?", (guest,)).fetchone()[0] == 0
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
        with pytest.raises(sqlite3.IntegrityError):
            con.execute("DELETE FROM simulation_runs WHERE id=?", (permanent[2],))


def test_refresh_does_not_extend_guest_and_old_database_is_cleaned(tmp_path):
    dbpath = tmp_path / "upgrade.sqlite"
    app = create_app(dbpath)
    client = TestClient(app)
    first = client.post("/public/session")
    assert first.status_code == 200
    assert first.json()["expires_in_seconds"] == 1200
    assert "Max-Age=1200" in first.headers["set-cookie"]
    actor = client.get("/auth/me").json()
    with app.state.db.session() as con:
        con.execute("UPDATE users SET created_at=? WHERE id=?",
                    ((datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                     actor["id"]))
    again = client.post("/public/session")
    assert again.status_code == 200
    assert 500 <= again.json()["expires_in_seconds"] <= 610
    assert client.get("/auth/me").json()["id"] == actor["id"]
    with app.state.db.session() as con:
        con.execute("UPDATE users SET created_at=? WHERE id=?",
                    ((datetime.now(timezone.utc) - timedelta(minutes=21)).isoformat(),
                     actor["id"]))
        # An existing older version could have a session token lasting 8 hours.
        con.execute("UPDATE session_tokens SET expires_at=? WHERE user_id=?",
                    ((datetime.now(timezone.utc) + timedelta(hours=8)).isoformat(),
                     actor["id"]))
    assert client.get("/auth/me").status_code == 401
    renewed = client.post("/public/session")
    assert renewed.status_code == 200
    assert client.get("/auth/me").json()["id"] != actor["id"]
    # Re-opening an existing DB must keep administrative records.
    reopened = Database(dbpath)
    reopened.setup()
    assert reopened.cleanup_expired_guests() == 0


def test_local_docker_admin_remains_explicit_opt_in(tmp_path, monkeypatch):
    app = create_app(tmp_path / "docker-admin.sqlite")
    app.state.db.create_user("admin", "a-very-long-administrator-password")
    c = TestClient(app, base_url="http://127.0.0.1:8000")
    # Mock bridge IP with custom ASGI scope: a normal test client is local.
    # The opt-in must be disabled unless explicitly set in server environment.
    assert "SIMCO2_DOCKER_LOCAL_HTTP_ADMIN" not in app.openapi()["info"]["title"]
    monkeypatch.setenv("SIMCO2_DOCKER_LOCAL_HTTP_ADMIN", "1")
    assert c.post("/auth/login", json={"username": "admin",
           "password": "a-very-long-administrator-password"}).status_code == 200
