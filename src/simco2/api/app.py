"""FastAPI prototype; aucun endpoint n'accepte prix par station."""

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles

from simco2.adapters.db import Database
from simco2.adapters.routing import ORSRoutingProvider
from simco2.api.schemas import (
    EnergyInput, VehicleInput, StationInput, ScenarioInput, LoginInput, RunInput,
    RoutePreviewInput)
from simco2.domain.engine import BaselineEngine
from simco2.domain.errors import DomainError, MissingReference, RoutingFailure
from simco2.reporting import render_pdf


def create_app(db_path: str | Path | None = None) -> FastAPI:
    app = FastAPI(title="SimCO2 — prototype de simulation transport voyageurs",
                  version="0.1.0", description="Prototype mono-ligne et données non vérifiées")
    db = Database(db_path or os.getenv("SIMCO2_DB_PATH", "./simco2.sqlite"))
    db.setup()
    app.state.db = db
    engine = BaselineEngine()

    @app.exception_handler(DomainError)
    async def handle_domain_error(request, exc: DomainError):
        code = (404 if isinstance(exc, MissingReference) else
                503 if isinstance(exc, RoutingFailure) else
                401 if exc.code == "invalid_credentials" else
                429 if exc.code == "too_many_attempts" else 422)
        return JSONResponse(status_code=code, content={"error": exc.as_dict()})

    def database():
        return app.state.db

    def require_actor(authorization: Annotated[str | None, Header()] = None,
                      db: Database = Depends(database)) -> dict:
        token = (authorization[7:] if authorization and authorization.startswith("Bearer ")
                 else None)
        user = db.actor_for_token(token or "")
        if not user:
            raise HTTPException(status_code=401, detail="Authentification requise")
        return user

    Actor = Annotated[dict, Depends(require_actor)]
    Db = Annotated[Database, Depends(database)]

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "simco2", "mode": "prototype"}

    @app.get("/feature-status")
    def features():
        return {
            "ready_for_production": False,
            "implemented": ["user_login", "audit", "versioned_energy", "versioned_vehicle",
                            "manual_stations", "single_line_snapshot", "baseline_fixed_consumption",
                            "baseline_tco", "direct_and_wtw_co2e", "simple_report_pdf"],
            "not_implemented": ["multi_day", "network_optimizer", "mixed_fleet", "repositioning",
                                "refuel", "charge", "regulatory_rules", "lifecycle_acv",
                                "jobs", "live_data_import", "map_dashboard"],
            "notice": "Les sources nationales/stations ne sont pas vérifiées, Q24 ouvert.",
        }

    @app.post("/auth/login")
    def login(data: LoginInput, db: Db, request: Request):
        client_key = request.client.host if request.client else "unknown"
        user_id, token = db.authenticate(data.username, data.password, client_key)
        return {"access_token": token, "token_type": "bearer", "expires_in_seconds": 8*3600,
                "user": {"id": user_id, "username": data.username}}

    @app.post("/auth/logout", status_code=204)
    def logout(actor: Actor, db: Db, authorization: Annotated[str, Header()]):
        db.revoke_token(authorization[7:])
        return Response(status_code=204)

    @app.get("/auth/me")
    def me(actor: Actor):
        return actor

    @app.get("/audit")
    def audit(actor: Actor, db: Db):
        return db.audit_for(actor["id"])

    @app.get("/energies/catalog")
    def energy_catalog(actor: Actor, db: Db):
        return db.energy_catalog()

    @app.get("/energies")
    def energies(actor: Actor, db: Db, country: str = "FR"):
        return db.list_energies(country)

    @app.get("/energies/versions/{version_id}")
    def get_energy_version(version_id: str, actor: Actor, db: Db):
        return db.get_energy(version_id)

    @app.get("/energies/{country}/{code}/versions")
    def energy_history(country: str, code: str, actor: Actor, db: Db):
        return db.energy_history(country, code)

    @app.post("/energies", status_code=201)
    def add_energy(data: EnergyInput, actor: Actor, db: Db):
        return db.append_energy(data.model_dump(mode="json"), actor["id"])

    @app.get("/vehicles")
    def vehicles(actor: Actor, db: Db):
        return db.list_vehicles()

    @app.post("/vehicles", status_code=201)
    def add_vehicle(data: VehicleInput, actor: Actor, db: Db):
        return db.append_vehicle(data.model_dump(mode="json"), actor["id"])

    @app.post("/vehicles/{vehicle_key}/versions", status_code=201)
    def add_vehicle_version(vehicle_key: str, data: VehicleInput, actor: Actor, db: Db):
        return db.append_vehicle(data.model_dump(mode="json"), actor["id"], vehicle_key)

    @app.get("/vehicles/{vehicle_key}/versions")
    def vehicle_history(vehicle_key: str, actor: Actor, db: Db):
        return db.vehicle_history(vehicle_key)

    @app.get("/vehicles/versions/{version_id}")
    def get_vehicle_version(version_id: str, actor: Actor, db: Db):
        return db.get_vehicle(version_id)

    @app.get("/stations")
    def stations(actor: Actor, db: Db):
        return db.list_stations()

    @app.post("/stations", status_code=201)
    def add_station(data: StationInput, actor: Actor, db: Db):
        return db.append_station(data.model_dump(mode="json"), actor["id"])

    @app.post("/stations/{station_key}/versions", status_code=201)
    def revise_station(station_key: str, data: StationInput, actor: Actor, db: Db):
        return db.append_station(data.model_dump(mode="json"), actor["id"], station_key)

    def check_references(data: ScenarioInput, db: Database):
        vehicle = db.get_vehicle(data.vehicle_version_id)["payload"]
        energy = db.get_energy(data.energy_version_id)["payload"]
        if (vehicle["energy_code"] != energy["energy_code"] or
            vehicle["unit"] != energy["unit"] or energy["country_iso"] != data.country_iso):
            raise DomainError("incompatible_references", "Véhicule et énergie/pays incompatibles")

    @app.get("/scenarios")
    def scenarios(actor: Actor, db: Db):
        return db.list_scenarios(actor["id"])

    @app.post("/scenarios", status_code=201)
    def add_scenario(data: ScenarioInput, actor: Actor, db: Db):
        check_references(data, db)
        return db.create_scenario(data.model_dump(mode="json"), actor["id"])

    @app.get("/scenarios/{scenario_id}")
    def scenario(scenario_id: str, actor: Actor, db: Db):
        return db.get_scenario(scenario_id, actor["id"])

    @app.post("/scenarios/{scenario_id}/revisions", status_code=201)
    def scenario_revision(scenario_id: str, data: ScenarioInput, actor: Actor, db: Db):
        check_references(data, db)
        return db.append_scenario_revision(scenario_id, data.model_dump(mode="json"), actor["id"])

    @app.get("/runs")
    def runs(actor: Actor, db: Db):
        return db.list_runs(actor["id"])

    @app.post("/runs", status_code=201)
    def add_run(data: RunInput, actor: Actor, db: Db):
        scenario_rev = db.get_scenario_revision(data.scenario_revision_id, actor["id"])
        scenario = scenario_rev["payload"]
        vehicle_ver = db.get_vehicle(scenario["vehicle_version_id"])
        energy_ver = db.get_energy(scenario["energy_version_id"])
        snapshot = {
            "scenario_revision_id": scenario_rev["id"],
            "scenario_revision_number": scenario_rev["revision"],
            "scenario": scenario,
            "vehicle_version": vehicle_ver,
            "energy_version": energy_ver,
            "routing_snapshot": scenario["route"],
            "solver_version": engine.ENGINE_VERSION,
            "country": scenario["country_iso"],
            "timezone": scenario["timezone"],
            "units": {"distance": "m", "time": "s", "money": "EUR", "co2e": "kgCO2e"},
            "random_seed": None,
            "time_limit_seconds": None,
        }
        result = engine.solve(snapshot)
        return db.record_run(scenario_rev["id"], snapshot, result.result, actor["id"])

    @app.get("/runs/{run_id}")
    def run(run_id: str, actor: Actor, db: Db):
        return db.get_run(run_id, actor["id"])

    @app.get("/runs/{run_id}/results")
    def results(run_id: str, actor: Actor, db: Db):
        return db.get_run(run_id, actor["id"])["result"]

    @app.get("/runs/{run_id}/report.pdf")
    def report(run_id: str, actor: Actor, db: Db):
        saved = db.get_run(run_id, actor["id"])
        pdf = render_pdf(saved)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="simulation-{run_id}.pdf"'})

    @app.get("/routing/status")
    def routing_status(actor: Actor):
        # Ne jamais exposer la cle du fournisseur.
        return {"provider": "openrouteservice", "configured": bool(os.getenv("ORS_API_KEY")),
                "note": "ORS à vérifier pour les limitations de gabarit/autocars."}

    @app.post("/routing/preview")
    def route_preview(data: RoutePreviewInput, actor: Actor):
        router = ORSRoutingProvider(os.getenv("ORS_API_KEY", ""))
        out = router.route(data.origin, data.destination, data.profile)
        return {"distance_m": str(out.distance_m), "duration_s": str(out.duration_s),
                "provider": out.provider, "version": out.provider_version,
                "valid_at": out.valid_at, "geometry": out.geometry,
                "restrictions": out.restrictions}

    ui_dir = Path(__file__).resolve().parents[1] / "ui"
    app.mount("/assets", StaticFiles(directory=str(ui_dir)), name="assets")

    @app.get("/", response_class=HTMLResponse)
    def index():
        return (ui_dir / "index.html").read_text(encoding="utf-8")

    return app


app = create_app()
