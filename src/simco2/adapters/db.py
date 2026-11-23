"""Référentiels SQLite immuables, propriété de scénario provisoire et audit."""
from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from argon2 import PasswordHasher, exceptions as argon_errors

from simco2.domain.errors import DomainError, MissingReference


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def jdump(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def rid() -> str:
    return str(uuid4())


class Database:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self.hasher = PasswordHasher(time_cost=2, memory_cost=10240, parallelism=1)

    @contextmanager
    def session(self):
        con = sqlite3.connect(self.path, timeout=20)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("PRAGMA busy_timeout = 20000")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def setup(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with self.session() as con:
            con.executescript(schema)

    @staticmethod
    def _dict(row):
        return dict(row) if row is not None else None

    @staticmethod
    def _event(con, actor: str, kind: str, obj_id: str, action: str,
               before: dict | None, after: dict | None):
        con.execute("INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (rid(), actor, kind, obj_id, action,
                     jdump(before) if before else None,
                     jdump(after) if after else None, utc_now()))

    def create_user(self, username: str, password: str) -> str:
        if not username or len(username) > 120 or len(password) < 12:
            raise DomainError("weak_credentials", "Identifiant requis et mot de passe >= 12 caractères")
        uid = rid()
        with self.session() as con:
            con.execute("INSERT INTO users VALUES (?, ?, ?, 1, ?)",
                        (uid, username, self.hasher.hash(password), utc_now()))
        return uid

    def authenticate(self, username: str, password: str,
                     client_key: str = "unknown") -> tuple[str, str]:
        with self.session() as con:
            # Fenêtre glissante 15 minutes, par login + origine de connexion.
            cutoff = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
            con.execute("DELETE FROM auth_failures WHERE created_at<?", (cutoff,))
            attempts = con.execute("""SELECT COUNT(*) FROM auth_failures
                WHERE username=? AND client_key=?""", (username, client_key)).fetchone()[0]
            if attempts >= 5:
                raise DomainError("too_many_attempts", "Trop de tentatives, réessayer plus tard")
            row = con.execute("SELECT * FROM users WHERE username=? AND active=1", (username,)).fetchone()
            try:
                if not row or not self.hasher.verify(row["password_hash"], password):
                    raise ValueError("bad credentials")
            except (ValueError, argon_errors.VerificationError, argon_errors.InvalidHashError):
                con.execute("INSERT INTO auth_failures VALUES (?, ?, ?, ?)",
                            (rid(), username, client_key, utc_now()))
                # On commit la tentative avant de renvoyer l'erreur.
                con.commit()
                raise DomainError("invalid_credentials", "Identifiants invalides") from None
            con.execute("DELETE FROM auth_failures WHERE username=? AND client_key=?",
                        (username, client_key))
            token = secrets.token_urlsafe(32)
            thash = hashlib.sha256(token.encode()).hexdigest()
            exp = (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat()
            con.execute("INSERT INTO session_tokens VALUES (?, ?, ?)", (thash, row["id"], exp))
            self._event(con, row["id"], "session", row["id"], "login", None,
                        {"login": username, "client_key": client_key})
            return row["id"], token

    def actor_for_token(self, token: str) -> dict | None:
        if not token:
            return None
        h = hashlib.sha256(token.encode()).hexdigest()
        with self.session() as con:
            row = con.execute("""SELECT u.id, u.username, u.active, t.expires_at
               FROM session_tokens t JOIN users u ON t.user_id=u.id WHERE t.token_hash=?""", (h,)).fetchone()
            if not row or not row["active"]:
                return None
            if datetime.fromisoformat(row["expires_at"]) <= datetime.now(timezone.utc):
                return None
            return {"id": row["id"], "username": row["username"]}

    def revoke_token(self, token: str):
        with self.session() as con:
            con.execute("DELETE FROM session_tokens WHERE token_hash=?",
                        (hashlib.sha256(token.encode()).hexdigest(),))

    def audit_for(self, user_id: str) -> list[dict]:
        with self.session() as con:
            return [dict(r) for r in con.execute("""SELECT id, actor_id, entity_type,
                entity_id, action, created_at FROM audit_events WHERE actor_id=?
                ORDER BY created_at DESC LIMIT 100""", (user_id,))]

    def energy_catalog(self):
        with self.session() as con:
            countries = [dict(r) for r in con.execute("SELECT * FROM country_catalog")]
            codes = [dict(r) for r in con.execute("SELECT * FROM energy_types")]
            return {"countries": countries, "energy_types": codes,
                    "notice": "Prix et facteurs NON préremplis : valeurs nationales non vérifiées."}

    def list_energies(self, country: str = "FR") -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT * FROM energy_versions e WHERE country_iso=?
                AND revision=(SELECT MAX(revision) FROM energy_versions x
                    WHERE x.country_iso=e.country_iso AND x.energy_code=e.energy_code)
                ORDER BY energy_code""", (country,)).fetchall()
            return [self._version_row(r) for r in rows]

    @staticmethod
    def _version_row(row) -> dict:
        d = dict(row)
        d["payload"] = json.loads(d.pop("payload_json"))
        return d

    def get_energy(self, version_id: str) -> dict:
        with self.session() as con:
            row = con.execute("SELECT * FROM energy_versions WHERE id=?", (version_id,)).fetchone()
        if not row:
            raise MissingReference("Version énergie inexistante")
        return self._version_row(row)

    def energy_history(self, country: str, code: str) -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT * FROM energy_versions WHERE country_iso=?
                 AND energy_code=? ORDER BY revision DESC""", (country, code)).fetchall()
            return [self._version_row(r) for r in rows]

    def append_energy(self, payload: dict, actor: str) -> dict:
        country = payload["country_iso"]
        code = payload["energy_code"]
        with self.session() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT unit FROM energy_types WHERE code=?", (code,)).fetchone()
            if not row:
                raise DomainError("unknown_energy", "Énergie inconnue")
            if row["unit"] != payload["unit"]:
                raise DomainError("unit_mismatch", "Unité différente de l'énergie cataloguée")
            if not con.execute("SELECT 1 FROM country_catalog WHERE iso=?", (country,)).fetchone():
                raise DomainError("unknown_country", "Pays non pris en charge")
            prev = con.execute("""SELECT * FROM energy_versions WHERE country_iso=?
                AND energy_code=? ORDER BY revision DESC LIMIT 1""", (country, code)).fetchone()
            rev = 1 if prev is None else prev["revision"] + 1
            eid = rid()
            con.execute("INSERT INTO energy_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (eid, country, code, rev, jdump(payload), actor, utc_now()))
            for perimeter, factor in payload.get("factors", {}).items():
                con.execute("""INSERT INTO emission_factors VALUES (?, ?, ?, ?, ?)""",
                            (eid, perimeter, str(factor), payload["source"], payload["source_date"]))
            self._event(con, actor, "energy", eid, "create_version",
                        self._version_row(prev) if prev else None, payload)
        return self.get_energy(eid)

    def list_vehicles(self) -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT * FROM vehicle_versions v
                WHERE revision=(SELECT MAX(revision) FROM vehicle_versions x
                   WHERE x.vehicle_key=v.vehicle_key)
                ORDER BY created_at DESC""").fetchall()
            return [self._version_row(r) for r in rows]

    def get_vehicle(self, version_id: str) -> dict:
        with self.session() as con:
            row = con.execute("SELECT * FROM vehicle_versions WHERE id=?", (version_id,)).fetchone()
        if not row:
            raise MissingReference("Version véhicule inexistante")
        return self._version_row(row)

    def vehicle_history(self, vehicle_key: str) -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT * FROM vehicle_versions WHERE vehicle_key=?
                ORDER BY revision DESC""", (vehicle_key,)).fetchall()
            return [self._version_row(r) for r in rows]

    def append_vehicle(self, payload: dict, actor: str, vehicle_key: str | None = None) -> dict:
        key = vehicle_key or rid()
        with self.session() as con:
            con.execute("BEGIN IMMEDIATE")
            prev = con.execute("""SELECT * FROM vehicle_versions WHERE vehicle_key=?
                ORDER BY revision DESC LIMIT 1""", (key,)).fetchone()
            if vehicle_key is not None and prev is None:
                raise MissingReference("Véhicule à mettre à jour introuvable")
            rev = 1 if prev is None else prev["revision"] + 1
            vid = rid()
            con.execute("INSERT INTO vehicle_versions VALUES (?, ?, ?, ?, ?, ?)",
                        (vid, key, rev, jdump(payload), actor, utc_now()))
            self._event(con, actor, "vehicle", vid, "create_version",
                        self._version_row(prev) if prev else None, payload)
        return self.get_vehicle(vid)

    def list_stations(self) -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT * FROM station_versions s
                WHERE revision=(SELECT MAX(revision) FROM station_versions x
                   WHERE x.station_key=s.station_key)
                ORDER BY created_at DESC""").fetchall()
            return [self._version_row(r) for r in rows]

    def append_station(self, payload: dict, actor: str, station_key: str | None = None) -> dict:
        def has_price_key(item):
            if isinstance(item, dict):
                return any((k.lower().startswith(("price", "tarif", "unit_cost")) or
                            has_price_key(v)) for k, v in item.items())
            if isinstance(item, list):
                return any(has_price_key(v) for v in item)
            return False

        if has_price_key(payload):
            raise DomainError("no_station_pricing", "Prix par station interdits (Q19)")
        key = station_key or rid()
        with self.session() as con:
            con.execute("BEGIN IMMEDIATE")
            prev = con.execute("""SELECT * FROM station_versions WHERE station_key=?
                ORDER BY revision DESC LIMIT 1""", (key,)).fetchone()
            if station_key is not None and prev is None:
                raise MissingReference("Station introuvable")
            rev = 1 if prev is None else prev["revision"] + 1
            sid = rid()
            con.execute("INSERT INTO station_versions VALUES (?, ?, ?, ?, ?, ?)",
                        (sid, key, rev, jdump(payload), actor, utc_now()))
            if "latitude" in payload and "longitude" in payload:
                con.execute("INSERT INTO station_coordinates VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (sid, str(payload["latitude"]), str(payload["longitude"]),
                             payload["access"], payload["operational_status"],
                             payload["source"], payload["observed_at"]))
            for equipment in payload.get("equipments", []):
                con.execute("""INSERT INTO station_equipments VALUES
                   (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (rid(), sid, equipment["energy_code"], equipment["connector"],
                     equipment["ports"], equipment.get("max_power_kw"),
                     equipment.get("flow_per_min"), equipment.get("pressure_bar")))
            self._event(con, actor, "station", sid, "create_version",
                        self._version_row(prev) if prev else None, payload)
            return {"id": sid, "station_key": key, "revision": rev, "payload": payload}

    def save_route_quote(self, actor: str, payload: dict) -> str:
        """Un devis de route doit venir du serveur, pas d'un formulaire modifiable."""
        qid = rid()
        expires = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        with self.session() as con:
            con.execute("DELETE FROM route_quotes WHERE expires_at < ?", (utc_now(),))
            con.execute("INSERT INTO route_quotes VALUES (?, ?, ?, ?, ?)",
                        (qid, actor, jdump(payload), expires, utc_now()))
        return qid

    def get_route_quote(self, quote_id: str, actor: str) -> dict:
        with self.session() as con:
            row = con.execute("SELECT payload_json FROM route_quotes WHERE id=? "
                              "AND owner_id=? AND expires_at>?",
                              (quote_id, actor, utc_now())).fetchone()
        if not row:
            raise MissingReference("Itinéraire expiré ou non accessible : recalculer l'itinéraire")
        return json.loads(row["payload_json"])

    def create_scenario(self, payload: dict, actor: str) -> dict:
        sid, rev_id = rid(), rid()
        with self.session() as con:
            con.execute("INSERT INTO scenarios VALUES (?, ?, ?, ?)",
                        (sid, actor, payload["name"], utc_now()))
            con.execute("INSERT INTO scenario_revisions VALUES (?, ?, 1, ?, ?, ?)",
                        (rev_id, sid, jdump(payload), actor, utc_now()))
            self._event(con, actor, "scenario", sid, "create", None,
                        {"name": payload["name"], "revision_id": rev_id})
        return self.get_scenario(sid, actor)

    def get_scenario(self, sid: str, actor: str) -> dict:
        with self.session() as con:
            row = con.execute("SELECT * FROM scenarios WHERE id=? AND owner_id=?",
                              (sid, actor)).fetchone()
            if not row:
                raise MissingReference("Scénario introuvable ou non visible (Q24 provisoire)")
            latest = con.execute("""SELECT * FROM scenario_revisions WHERE scenario_id=?
                ORDER BY revision DESC LIMIT 1""", (sid,)).fetchone()
            d = dict(row)
            d["latest_revision"] = self._version_row(latest)
            return d

    def list_scenarios(self, actor: str) -> list[dict]:
        with self.session() as con:
            rows = con.execute("SELECT id FROM scenarios WHERE owner_id=? ORDER BY created_at DESC",
                               (actor,)).fetchall()
        return [self.get_scenario(r["id"], actor) for r in rows]

    def append_scenario_revision(self, sid: str, payload: dict, actor: str) -> dict:
        with self.session() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM scenarios WHERE id=? AND owner_id=?",
                              (sid, actor)).fetchone()
            if not row:
                raise MissingReference("Scénario introuvable")
            prev = con.execute("""SELECT * FROM scenario_revisions WHERE scenario_id=?
                ORDER BY revision DESC LIMIT 1""", (sid,)).fetchone()
            new_id, rev = rid(), prev["revision"] + 1
            con.execute("INSERT INTO scenario_revisions VALUES (?, ?, ?, ?, ?, ?)",
                        (new_id, sid, rev, jdump(payload), actor, utc_now()))
            con.execute("UPDATE scenarios SET name=? WHERE id=?", (payload["name"], sid))
            self._event(con, actor, "scenario", sid, "create_revision",
                        self._version_row(prev), {"revision_id": new_id, "payload": payload})
        return self.get_scenario(sid, actor)

    def get_scenario_revision(self, version_id: str, actor: str) -> dict:
        with self.session() as con:
            row = con.execute("""SELECT r.* FROM scenario_revisions r
                JOIN scenarios s ON r.scenario_id=s.id
                WHERE r.id=? AND s.owner_id=?""", (version_id, actor)).fetchone()
        if not row:
            raise MissingReference("Révision scénario introuvable ou non visible")
        return self._version_row(row)

    def record_run(self, scenario_revision_id: str, snapshot: dict, result: dict,
                   actor: str) -> dict:
        run_id = rid()
        snapshot_json = jdump(snapshot)
        sha = hashlib.sha256(snapshot_json.encode("utf-8")).hexdigest()
        with self.session() as con:
            con.execute("""INSERT INTO simulation_runs VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)""",
                (run_id, scenario_revision_id, actor, snapshot_json, sha,
                 jdump(result), result["status"], utc_now()))
            self._event(con, actor, "simulation_run", run_id, "create", None,
                        {"status": result["status"], "snapshot_sha256": sha})
        return self.get_run(run_id, actor)

    def get_run(self, run_id: str, actor: str) -> dict:
        with self.session() as con:
            row = con.execute("SELECT * FROM simulation_runs WHERE id=? AND owner_id=?",
                              (run_id, actor)).fetchone()
        if not row:
            raise MissingReference("Exécution introuvable ou non visible")
        out = dict(row)
        out["snapshot"] = json.loads(out.pop("snapshot_json"))
        out["result"] = json.loads(out.pop("result_json"))
        return out

    def list_runs(self, actor: str) -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT id FROM simulation_runs WHERE owner_id=?
                ORDER BY created_at DESC LIMIT 100""", (actor,)).fetchall()
        return [self.get_run(r["id"], actor) for r in rows]

    def record_comparison(self, name: str, shared: dict, entries: list[dict], actor: str) -> dict:
        """Persiste un groupe et tous ses runs d'un seul coup, ou rien du tout."""
        cid = rid()
        shared_json = jdump(shared)
        digest = hashlib.sha256(shared_json.encode("utf-8")).hexdigest()
        with self.session() as con:
            con.execute("BEGIN IMMEDIATE")
            con.execute("INSERT INTO comparison_groups VALUES (?, ?, ?, ?, ?, ?)",
                        (cid, actor, name, shared_json, digest, utc_now()))
            for i, item in enumerate(entries):
                scenario_id, revision_id, run_id = (item[k] for k in (
                    "scenario_id", "revision_id", "run_id"))
                snapshot = item["snapshot"]
                result = item["result"]
                snap_json = jdump(snapshot)
                snap_digest = hashlib.sha256(snap_json.encode("utf-8")).hexdigest()
                con.execute("INSERT INTO scenarios VALUES (?, ?, ?, ?)",
                            (scenario_id, actor, item["scenario"]["name"], utc_now()))
                con.execute("INSERT INTO scenario_revisions VALUES (?, ?, 1, ?, ?, ?)",
                            (revision_id, scenario_id, jdump(item["scenario"]), actor, utc_now()))
                con.execute("INSERT INTO simulation_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (run_id, revision_id, actor, snap_json, snap_digest,
                             jdump(result), result["status"], utc_now()))
                con.execute("INSERT INTO comparison_members VALUES (?, ?, ?)", (cid, run_id, i))
                self._event(con, actor, "simulation_run", run_id, "compare", None,
                            {"comparison_id": cid, "snapshot_sha256": snap_digest})
            self._event(con, actor, "comparison", cid, "create", None,
                        {"members": len(entries), "shared_sha256": digest})
        return self.get_comparison(cid, actor)

    def get_comparison(self, comparison_id: str, actor: str) -> dict:
        with self.session() as con:
            row = con.execute("SELECT * FROM comparison_groups WHERE id=? AND owner_id=?",
                              (comparison_id, actor)).fetchone()
            if not row:
                raise MissingReference("Comparaison introuvable ou non accessible")
            runs = con.execute("""SELECT r.*, m.display_order FROM comparison_members m
                JOIN simulation_runs r ON r.id=m.run_id WHERE m.comparison_id=?
                ORDER BY m.display_order""", (comparison_id,)).fetchall()
            shared = json.loads(row["shared_json"])
            results = []
            for entry in runs:
                snapshot = json.loads(entry["snapshot_json"])
                results.append({"run_id": entry["id"], "snapshot_sha256": entry["snapshot_sha256"],
                                "vehicle_version": snapshot["vehicle_version"],
                                "energy_version": snapshot["energy_version"],
                                "result": json.loads(entry["result_json"]),
                                "status": entry["status"]})
            return {"id": row["id"], "name": row["name"],
                    "shared": shared, "shared_sha256": row["shared_sha256"],
                    "created_at": row["created_at"], "entries": results,
                    "notice": "Comparaison de cas indépendants, sans flotte mixte ni optimum certifié."}

    def list_comparisons(self, actor: str) -> list[dict]:
        with self.session() as con:
            rows = con.execute("""SELECT c.id, c.name, c.created_at, COUNT(m.run_id) AS count
                FROM comparison_groups c JOIN comparison_members m ON m.comparison_id=c.id
                WHERE c.owner_id=? GROUP BY c.id ORDER BY c.created_at DESC LIMIT 100""",
                (actor,)).fetchall()
            return [dict(row) for row in rows]
