-- SQLite prototype, migration 0001. Les revisions sont des enregistrements immuables.
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS session_tokens (
  token_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_failures (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL,
  client_key TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_auth_failures ON auth_failures(username, client_key, created_at);
CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY,
  actor_id TEXT NOT NULL REFERENCES users(id),
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  action TEXT NOT NULL,
  before_json TEXT,
  after_json TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS country_catalog (
  iso TEXT PRIMARY KEY,
  currency TEXT NOT NULL,
  timezone_default TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS energy_types (
  code TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  unit TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS energy_versions (
  id TEXT PRIMARY KEY,
  country_iso TEXT NOT NULL REFERENCES country_catalog(iso),
  energy_code TEXT NOT NULL REFERENCES energy_types(code),
  revision INTEGER NOT NULL CHECK (revision >= 1),
  payload_json TEXT NOT NULL,
  created_by TEXT NOT NULL REFERENCES users(id),
  created_at TEXT NOT NULL,
  UNIQUE (country_iso, energy_code, revision)
);
CREATE TABLE IF NOT EXISTS emission_factors (
  energy_version_id TEXT NOT NULL REFERENCES energy_versions(id),
  perimeter TEXT NOT NULL CHECK (perimeter IN ('direct','well_to_wheel','lifecycle')),
  kgco2e_per_unit TEXT NOT NULL,
  source_label TEXT NOT NULL,
  source_date TEXT NOT NULL,
  PRIMARY KEY (energy_version_id, perimeter)
);
CREATE TABLE IF NOT EXISTS vehicle_versions (
  id TEXT PRIMARY KEY,
  vehicle_key TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK (revision >= 1),
  payload_json TEXT NOT NULL,
  created_by TEXT NOT NULL REFERENCES users(id),
  created_at TEXT NOT NULL,
  UNIQUE (vehicle_key, revision)
);
CREATE TABLE IF NOT EXISTS station_versions (
  id TEXT PRIMARY KEY,
  station_key TEXT NOT NULL,
  revision INTEGER NOT NULL CHECK (revision >= 1),
  payload_json TEXT NOT NULL,
  created_by TEXT NOT NULL REFERENCES users(id),
  created_at TEXT NOT NULL,
  UNIQUE (station_key, revision)
);
CREATE TABLE IF NOT EXISTS station_coordinates (
  station_version_id TEXT PRIMARY KEY REFERENCES station_versions(id),
  latitude TEXT NOT NULL,
  longitude TEXT NOT NULL,
  access TEXT NOT NULL,
  operational_status TEXT NOT NULL,
  source_label TEXT NOT NULL,
  observed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS station_equipments (
  id TEXT PRIMARY KEY,
  station_version_id TEXT NOT NULL REFERENCES station_versions(id),
  energy_code TEXT NOT NULL REFERENCES energy_types(code),
  connector TEXT NOT NULL,
  ports INTEGER NOT NULL CHECK (ports >= 1),
  max_power_kw TEXT,
  flow_per_min TEXT,
  pressure_bar TEXT
);
CREATE INDEX IF NOT EXISTS ix_station_equipments_energy ON station_equipments(energy_code);
CREATE TABLE IF NOT EXISTS scenarios (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES users(id),
  name TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scenario_revisions (
  id TEXT PRIMARY KEY,
  scenario_id TEXT NOT NULL REFERENCES scenarios(id),
  revision INTEGER NOT NULL CHECK (revision >= 1),
  payload_json TEXT NOT NULL,
  created_by TEXT NOT NULL REFERENCES users(id),
  created_at TEXT NOT NULL,
  UNIQUE (scenario_id, revision)
);
CREATE TABLE IF NOT EXISTS simulation_runs (
  id TEXT PRIMARY KEY,
  scenario_revision_id TEXT NOT NULL REFERENCES scenario_revisions(id),
  owner_id TEXT NOT NULL REFERENCES users(id),
  snapshot_json TEXT NOT NULL,
  snapshot_sha256 TEXT NOT NULL,
  result_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_audit_actor_date ON audit_events(actor_id, created_at);
CREATE INDEX IF NOT EXISTS ix_scenario_owner ON scenarios(owner_id);
CREATE INDEX IF NOT EXISTS ix_run_owner ON simulation_runs(owner_id);
-- Un catalogue national avec des types connus ne signifie pas des prix certifies.
INSERT OR IGNORE INTO country_catalog(iso, currency, timezone_default)
VALUES ('FR', 'EUR', 'Europe/Paris');
INSERT OR IGNORE INTO energy_types(code, label, unit)
VALUES ('DIESEL', 'Gazole (hypotheses utilisateur requises)', 'L');
INSERT OR IGNORE INTO energy_types(code, label, unit)
VALUES ('ELECTRIC', 'Electricite (hypotheses utilisateur requises)', 'kWh');
INSERT OR IGNORE INTO energy_types(code, label, unit)
VALUES ('H2', 'Hydrogene (hypotheses utilisateur requises)', 'kg');

-- Protection supplémentaire : une révision utilisée dans un résultat ne peut
-- jamais être modifiée ou effacée, y compris par manipulation SQL directe.
CREATE TRIGGER IF NOT EXISTS energy_no_update BEFORE UPDATE ON energy_versions
BEGIN SELECT RAISE(ABORT, 'energy revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS energy_no_delete BEFORE DELETE ON energy_versions
BEGIN SELECT RAISE(ABORT, 'energy revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS vehicle_no_update BEFORE UPDATE ON vehicle_versions
BEGIN SELECT RAISE(ABORT, 'vehicle revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS vehicle_no_delete BEFORE DELETE ON vehicle_versions
BEGIN SELECT RAISE(ABORT, 'vehicle revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS station_no_update BEFORE UPDATE ON station_versions
BEGIN SELECT RAISE(ABORT, 'station revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS station_no_delete BEFORE DELETE ON station_versions
BEGIN SELECT RAISE(ABORT, 'station revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS scenario_revision_no_update BEFORE UPDATE ON scenario_revisions
BEGIN SELECT RAISE(ABORT, 'scenario revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS scenario_revision_no_delete BEFORE DELETE ON scenario_revisions
BEGIN SELECT RAISE(ABORT, 'scenario revisions are immutable'); END;
CREATE TRIGGER IF NOT EXISTS run_no_update BEFORE UPDATE ON simulation_runs
BEGIN SELECT RAISE(ABORT, 'run results are immutable'); END;
CREATE TRIGGER IF NOT EXISTS run_no_delete BEFORE DELETE ON simulation_runs
BEGIN SELECT RAISE(ABORT, 'run results are immutable'); END;

CREATE TRIGGER IF NOT EXISTS factor_no_update BEFORE UPDATE ON emission_factors
BEGIN SELECT RAISE(ABORT, 'emission factors are immutable'); END;
CREATE TRIGGER IF NOT EXISTS factor_no_delete BEFORE DELETE ON emission_factors
BEGIN SELECT RAISE(ABORT, 'emission factors are immutable'); END;
CREATE TRIGGER IF NOT EXISTS equipment_no_update BEFORE UPDATE ON station_equipments
BEGIN SELECT RAISE(ABORT, 'station equipments are immutable'); END;
CREATE TRIGGER IF NOT EXISTS equipment_no_delete BEFORE DELETE ON station_equipments
BEGIN SELECT RAISE(ABORT, 'station equipments are immutable'); END;
CREATE TRIGGER IF NOT EXISTS coordinate_no_update BEFORE UPDATE ON station_coordinates
BEGIN SELECT RAISE(ABORT, 'station coordinates are immutable'); END;
CREATE TRIGGER IF NOT EXISTS coordinate_no_delete BEFORE DELETE ON station_coordinates
BEGIN SELECT RAISE(ABORT, 'station coordinates are immutable'); END;

-- Jeton de calcul routier lié à l'utilisateur, temporaire et non réutilisable
-- comme preuve d'un itinéraire provenant d'un prestataire extérieur.
CREATE TABLE IF NOT EXISTS route_quotes (
  id TEXT PRIMARY KEY,
  owner_id TEXT NOT NULL REFERENCES users(id),
  payload_json TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_route_quotes_owner ON route_quotes(owner_id, expires_at);
