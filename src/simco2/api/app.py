"""FastAPI prototype; aucun endpoint n'accepte prix par station."""

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import HTMLResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles

from simco2.adapters.db import Database, rid
from simco2.adapters.routing import (ORSRoutingProvider, OSRMRoutingProvider,
                                      GeoplatformGeocoder)
from simco2.adapters.routing_settings import RoutingSettings
from simco2.adapters.discovery import (NORMANDY_H2, FuelStationDirectory,
                                        FUEL_SOURCE, AREA_DEPARTMENTS)
from simco2.api.schemas import (
    EnergyInput, VehicleInput, StationInput, ScenarioInput, LoginInput, RunInput,
    RoutePreviewInput, RouteResolveInput, RouteInput, ComparisonInput,
    RoutingConfigInput, RoutingKeyInput)
from simco2.domain.engine import BaselineEngine
from simco2.domain.service_day import schedule_day
from simco2.adapters.station_optimization import route_candidates
from simco2.domain.errors import DomainError, MissingReference, RoutingFailure
from simco2.reporting import render_pdf


def create_app(db_path: str | Path | None = None, *, geocoder=None, routing_provider=None,
               fuel_directory=None, routing_settings=None) -> FastAPI:
    app = FastAPI(title="SimCO2 — prototype de simulation transport voyageurs",
                  version="0.1.0", description="Prototype mono-ligne et données non vérifiées")
    db = Database(db_path or os.getenv("SIMCO2_DB_PATH", "./simco2.sqlite"))
    db.setup()
    app.state.db = db
    engine = BaselineEngine()
    app.state.geocoder = geocoder if geocoder is not None else GeoplatformGeocoder()
    app.state.fuel_directory = fuel_directory if fuel_directory is not None else FuelStationDirectory()
    app.state.routing_settings = routing_settings or RoutingSettings()
    # Injected provider is reserved for deterministic tests; production resolves
    # settings at request time so a locally saved key takes effect immediately.
    app.state.routing_provider = routing_provider

    def active_router():
        return app.state.routing_provider or app.state.routing_settings.provider()

    def is_local_operator(actor: dict, request: Request) -> bool:
        # Admin requests must carry an explicit bearer token. HTTPS is required
        # over a network; loopback remains available for local development.
        secure_transport = (request.url.scheme == "https" or
                            request.client is not None and
                            request.client.host in ("127.0.0.1", "::1", "testclient") and
                            request.url.hostname in ("127.0.0.1", "localhost", "::1", "testserver"))
        return (actor.get("username") == os.getenv("SIMCO2_OPERATOR_USERNAME", "admin")
                and secure_transport)

    def assert_local_operator(actor: dict, request: Request):
        if not is_local_operator(actor, request):
            raise HTTPException(status_code=403, detail="Connexion administrateur requise (HTTPS hors du poste local)")

    @app.exception_handler(DomainError)
    async def handle_domain_error(request, exc: DomainError):
        code = (404 if isinstance(exc, MissingReference) else
                503 if isinstance(exc, RoutingFailure) else
                401 if exc.code == "invalid_credentials" else
                429 if exc.code == "too_many_attempts" else 422)
        return JSONResponse(status_code=code, content={"error": exc.as_dict()})

    def database():
        return app.state.db

    def require_actor(request: Request, authorization: Annotated[str | None, Header()] = None,
                      db: Database = Depends(database)) -> dict:
        # The admin credential is only ever sent in the Authorization header.
        # Public visitors receive a separate HttpOnly cookie, never an admin session.
        bearer = (authorization[7:] if authorization and authorization.startswith("Bearer ")
                  else None)
        if authorization and not bearer:
            raise HTTPException(status_code=401, detail="Jeton d'accès invalide")
        token = bearer if bearer is not None else request.cookies.get("simco2_guest", "")
        user = db.actor_for_token(token)
        if not user or (bearer is None and not user["username"].startswith("guest_")):
            raise HTTPException(status_code=401, detail="Session expirée : actualisez la page")
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
                            "manual_stations", "single_line_snapshot", "limited_day_planner", "bounded_auto_refuel_search", "baseline_fixed_consumption",
                            "baseline_tco", "direct_and_wtw_co2e", "simple_report_pdf"],
            "not_implemented": ["multi_day", "network_optimizer", "mixed_fleet", "repositioning",
                                "globally_optimal_refuel_selection", "charge", "regulatory_rules", "lifecycle_acv",
                                "jobs", "live_data_import", "map_dashboard"],
            "notice": "Les sources nationales/stations ne sont pas vérifiées, Q24 ouvert.",
        }

    @app.post("/public/session")
    def public_session(request: Request, response: Response, db: Db):
        # Refreshing the page must not send visitors back to a login portal.
        existing = db.actor_for_token(request.cookies.get("simco2_guest", ""))
        if existing and existing["username"].startswith("guest_"):
            return {"mode": "public"}
        client_key = request.client.host if request.client else "unknown"
        db.consume_public_quota(client_key, "new_session", 25)
        _, token = db.create_guest()
        response.set_cookie("simco2_guest", token, httponly=True, samesite="lax",
                            secure=request.url.scheme == "https", max_age=8 * 3600,
                            path="/")
        return {"mode": "public"}

    @app.post("/auth/login")
    def login(data: LoginInput, db: Db, request: Request):
        if data.username != os.getenv("SIMCO2_OPERATOR_USERNAME", "admin"):
            raise HTTPException(status_code=401, detail="Compte administrateur requis")
        if request.url.scheme != "https" and not (request.client and
                request.client.host in ("127.0.0.1", "::1", "testclient") and
                request.url.hostname in ("127.0.0.1", "localhost", "::1", "testserver")):
            raise HTTPException(status_code=403, detail="HTTPS requis pour la connexion administrateur")
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
    def audit(actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
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
    def add_energy(data: EnergyInput, actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
        return db.append_energy(data.model_dump(mode="json"), actor["id"])

    @app.post("/energies/{country}/{code}/archive", status_code=204)
    def archive_energy(country: str, code: str, actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
        db.archive_energy(country, code, actor["id"])
        return Response(status_code=204)

    @app.get("/vehicles")
    def vehicles(actor: Actor, db: Db):
        return db.list_vehicles()

    @app.post("/vehicles", status_code=201)
    def add_vehicle(data: VehicleInput, actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
        return db.append_vehicle(data.model_dump(mode="json"), actor["id"])

    @app.post("/vehicles/{vehicle_key}/versions", status_code=201)
    def add_vehicle_version(vehicle_key: str, data: VehicleInput, actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
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
    def add_station(data: StationInput, actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
        return db.append_station(data.model_dump(mode="json"), actor["id"])

    @app.post("/stations/{station_key}/versions", status_code=201)
    def revise_station(station_key: str, data: StationInput, actor: Actor, db: Db, request: Request):
        assert_local_operator(actor, request)
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

    def scenario_payload(data: ScenarioInput, actor: dict, db: Database) -> dict:
        payload = data.model_dump(mode="json", exclude={"route_quote_id"})
        if data.route_quote_id:
            payload["route"] = db.get_route_quote(data.route_quote_id, actor["id"])
        # En particulier, on n'accepte jamais un itinéraire externe forgé par le client.
        RouteInput.model_validate(payload["route"])
        return payload

    @app.post("/scenarios", status_code=201)
    def add_scenario(data: ScenarioInput, actor: Actor, db: Db):
        check_references(data, db)
        return db.create_scenario(scenario_payload(data, actor, db), actor["id"])

    @app.get("/scenarios/{scenario_id}")
    def scenario(scenario_id: str, actor: Actor, db: Db):
        return db.get_scenario(scenario_id, actor["id"])

    @app.post("/scenarios/{scenario_id}/revisions", status_code=201)
    def scenario_revision(scenario_id: str, data: ScenarioInput, actor: Actor, db: Db):
        check_references(data, db)
        return db.append_scenario_revision(scenario_id, scenario_payload(data, actor, db), actor["id"])

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
    def report(run_id: str, actor: Actor, db: Db, lang: str = "fr"):
        if lang not in ("fr", "en"):
            raise HTTPException(status_code=422, detail="Unsupported language")
        saved = db.get_run(run_id, actor["id"])
        pdf = render_pdf(saved, lang=lang)
        return Response(content=pdf, media_type="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="simulation-{run_id}.pdf"'})

    @app.post("/comparisons", status_code=201)
    def compare_vehicles(data: ComparisonInput, actor: Actor, db: Db, request: Request):
        """Comparer des cas séparés sur un itinéraire, une demande et un périmètre identiques."""
        if actor["username"].startswith("guest_"):
            db.consume_public_quota(request.client.host if request.client else "unknown",
                                    "comparison", 20)
        from simco2.api.schemas import ScenarioInput
        quote = db.get_route_quote(data.route_quote_id, actor["id"])
        energies = {e["energy_code"]: e for e in db.list_energies(data.country_iso)}
        # Supplemental legs are routed once and frozen in all comparison snapshots.
        # A mirrored distance is not a credible reverse itinerary.
        day_legs = {}
        # Older clients only had an optional station object. Preserve their
        # imposed-station semantics; new clients state a policy explicitly.
        # When an old client supplied a station, that meant "imposed". An
        # explicit new station_policy=automatic MUST take precedence.
        legacy_station = (data.refuel_station is not None and
                          "station_policy" not in data.model_fields_set)
        day_station_policy = "imposed" if legacy_station else data.station_policy
        day_station = (data.refuel_station.model_dump(mode="json")
                       if data.day_plan and day_station_policy == "imposed" and data.refuel_station else None)
        if data.day_plan and day_station_policy == "imposed" and not day_station:
            raise DomainError("station_required", "Choisissez une station pour le mode imposé")
        if day_station:
            day_station["quality"] = "user_selected_unverified"
            day_station["station_operational_and_bus_access_verified"] = False
            selected_energy_codes = {db.get_vehicle(v)["payload"]["energy_code"]
                                     for v in data.vehicle_version_ids}
            if not selected_energy_codes.intersection(day_station["energy_codes"]):
                raise DomainError("station_energy_incompatible",
                                  "La station imposée ne distribue aucune des énergies sélectionnées")
        station_options = {}
        station_search_warnings = []
        if data.day_plan:
            origins = quote.get("origin_coordinates"), quote.get("destination_coordinates")
            if not all(origins):
                raise DomainError("day_route_coordinates_missing",
                                  "Planification impossible sans coordonnees calculees cote serveur")
            provider = active_router()
            if provider is None:
                raise RoutingFailure("provider_unconfigured", "Aucun fournisseur de routage")
            from decimal import ROUND_HALF_UP
            profile = quote.get("profile")
            def frozen_leg(a, b, label):
                result = provider.route(tuple(a), tuple(b), profile)
                if (result.provider != quote.get("provider") or result.profile != profile
                        or result.distance_m <= 0 or result.duration_s <= 0):
                    raise RoutingFailure("mismatched_routing_provider",
                                         "Routage retour/station incompatible avec le trajet initial")
                return {"label": label, "distance_m": str(result.distance_m),
                        "duration_s": str(result.duration_s), "provider": result.provider,
                        "profile": result.profile, "valid_at": result.valid_at,
                        "restrictions": list(result.restrictions)}
            if any(data.passengers > db.get_vehicle(v)["payload"]["seats"]
                   for v in data.vehicle_version_ids):
                start_coordinates, end_coordinates = origins
                day_legs["reverse"] = frozen_leg(end_coordinates, start_coordinates, "retour a vide")
                if day_station:
                    station_point = (day_station["longitude"], day_station["latitude"])
                    day_legs["via_station"] = {
                        "to_station": frozen_leg(end_coordinates, station_point, "detour station"),
                        "from_station": frozen_leg(station_point, start_coordinates, "station vers origine")}
                if day_station_policy == "automatic":
                    needed = set()
                    for vehicle_id in data.vehicle_version_ids:
                        v = db.get_vehicle(vehicle_id)["payload"]
                        code = v["energy_code"]
                        flow = {"DIESEL": data.diesel_flow_l_per_min,
                                "H2": data.hydrogen_flow_kg_per_min}.get(code, "0")
                        if data.passengers > v["seats"] and float(flow) > 0:
                            needed.add(code)
                    if needed:
                        # The official fuel directory is paginated. Do not
                        # silently pretend that this bounded sample is complete.
                        catalog = list(NORMANDY_H2)
                        if "DIESEL" in needed:
                            for offset in (0, 100, 200):
                                page = app.state.fuel_directory.page(offset, 100, area="normandy")
                                if page.get("unavailable"):
                                    station_search_warnings.append(
                                        "Répertoire DGCCRF indisponible : aucun arrêt gazole automatique vérifié.")
                                    break
                                catalog.extend(page.get("stations") or [])
                                if not page.get("has_more"):
                                    break
                                if offset == 200:
                                    station_search_warnings.append(
                                        "Répertoire DGCCRF partiel (300 premières stations) : optimum non prouvé.")
                        station_options, routing_warnings = route_candidates(
                            provider, quote, catalog, needed, max_per_energy=4)
                        station_search_warnings.extend(routing_warnings)
                    else:
                        station_search_warnings.append(
                            "Aucun débit de plein renseigné ou aucun second trajet : recherche de stations inutile.")
        entries = []
        for version_id in data.vehicle_version_ids:
            vehicle = db.get_vehicle(version_id)
            payload = vehicle["payload"]
            energy = energies.get(payload["energy_code"])
            if energy is None:
                raise DomainError("missing_energy", "Configurer l'énergie " + payload["energy_code"] + " avant comparaison")
            scenario = ScenarioInput.model_validate({
                "name": (data.name + " - " + payload["label"])[:200],
                "country_iso": data.country_iso, "start_date": data.start_date,
                "end_date": data.start_date, "timezone": "Europe/Paris",
                "route_quote_id": data.route_quote_id, "passengers": data.passengers,
                "window_start": data.window_start, "window_end": data.window_end,
                "max_vehicles": data.max_vehicles, "tco_scope": data.tco_scope,
                "emission_scope": data.emission_scope,
                "infrastructure_daily_eur": data.infrastructure_daily_eur,
                "vehicle_version_id": version_id, "energy_version_id": energy["id"],
            })
            check_references(scenario, db)
            scenario_doc = scenario.model_dump(mode="json", exclude={"route_quote_id"})
            scenario_doc["route"] = quote
            if data.day_plan:
                scenario_doc["schedule_mode"] = "single_line_day_greedy"
                scenario_doc["refuel_mode"] = ("optimized" if day_station_policy == "automatic"
                                               else day_station_policy)
            revision_id = rid()
            snapshot = {
                "scenario_revision_id": revision_id, "scenario_revision_number": 1,
                "scenario": scenario_doc, "vehicle_version": vehicle,
                "energy_version": energy, "routing_snapshot": quote,
                "day_legs": day_legs if data.day_plan else None,
                "day_station": day_station,
                "day_station_policy": day_station_policy if data.day_plan else None,
                "day_station_options": station_options if data.day_plan else None,
                "day_station_search_warnings": station_search_warnings if data.day_plan else None,
                "day_refuel_rates_per_min": {
                    "DIESEL": data.diesel_flow_l_per_min,
                    "H2": data.hydrogen_flow_kg_per_min,
                } if data.day_plan else None,
                "day_handling_minutes": data.handling_minutes if data.day_plan else None,
                "solver_version": "single-line-day-v0.1" if data.day_plan else engine.ENGINE_VERSION,
                "country": data.country_iso,
                "timezone": "Europe/Paris",
                "units": {"distance": "m", "time": "s", "money": "EUR", "co2e": "kgCO2e"},
                "random_seed": None, "time_limit_seconds": None,
            }
            result = (schedule_day(snapshot) if data.day_plan else engine.solve(snapshot)).result
            entries.append({"scenario_id": rid(), "revision_id": revision_id,
                            "run_id": rid(), "scenario": scenario_doc,
                            "snapshot": snapshot, "result": result})
        shared = {
            "route": quote, "country_iso": data.country_iso,
            "start_date": data.start_date.isoformat(), "passengers": data.passengers,
            "window_start": data.window_start, "window_end": data.window_end,
            "max_vehicles": data.max_vehicles, "tco_scope": data.tco_scope,
            "emission_scope": data.emission_scope,
            "infrastructure_daily_eur": data.infrastructure_daily_eur,
            "vehicle_version_ids": list(data.vehicle_version_ids),
            "comparison_kind": "independent_homogeneous_day_plans" if data.day_plan
                               else "independent_homogeneous_cases",
            "day_plan": data.day_plan,
            "day_legs": day_legs if data.day_plan else None,
            "day_station": day_station,
            "day_station_policy": day_station_policy if data.day_plan else None,
            "day_station_options": station_options if data.day_plan else None,
            "day_station_search_warnings": station_search_warnings if data.day_plan else None,
            "day_refuel_rates_per_min": {
                "DIESEL": data.diesel_flow_l_per_min,
                "H2": data.hydrogen_flow_kg_per_min,
            } if data.day_plan else None,
            "day_handling_minutes": data.handling_minutes if data.day_plan else None,
            "optimality_proven": False,
        }
        return db.record_comparison(data.name, shared, entries, actor["id"])

    @app.get("/comparisons")
    def comparisons(actor: Actor, db: Db):
        return db.list_comparisons(actor["id"])

    @app.get("/comparisons/{comparison_id}")
    def get_comparison(comparison_id: str, actor: Actor, db: Db):
        return db.get_comparison(comparison_id, actor["id"])

    @app.get("/stations/discovery")
    def station_discovery(actor: Actor, offset: int = 0, limit: int = 100,
                          area: str = "normandy"):
        if offset < 0 or offset > 10000 or not 1 <= limit <= 100 or area not in AREA_DEPARTMENTS:
            raise HTTPException(status_code=422, detail="Zone ou pagination invalide")
        fuel = app.state.fuel_directory.page(offset, limit, area=area)
        hydrogen = [station for station in NORMANDY_H2
                    if station.get("department_code") in AREA_DEPARTMENTS[area]]
        return {"hydrogen": hydrogen, "fuel": fuel,
                "coverage": "Eure et Seine-Maritime" if area == "upper_normandy" else "Normandie",
                "warnings": ["Données à vérifier avant déplacement ou planification.",
                             "Les stations H2 listées ne sont pas certifiées pour autocars.",
                             "Aucun tarif par station n'est utilisé."],
                "fuel_source": FUEL_SOURCE}

    @app.get("/routing/status")
    def routing_status(actor: Actor, request: Request):
        status = app.state.routing_settings.status(operator=is_local_operator(actor, request))
        if app.state.routing_provider is not None:
            status.update({"provider": "fixture", "available": True, "endpoint": "test fixture"})
        return {**status, "configured": bool(status["configured"].get("ors")),
                "geoapify_configured": status["configured"].get("geoapify", False),
                "prototype_only": status["provider"] == "osrm_demo"}

    @app.get("/routing/config")
    def routing_config(actor: Actor, request: Request):
        assert_local_operator(actor, request)
        return app.state.routing_settings.status(operator=True)

    @app.post("/routing/config")
    def save_routing_config(data: RoutingConfigInput, actor: Actor, request: Request):
        assert_local_operator(actor, request)
        if os.getenv("SIMCO2_ROUTING_MODE"):
            raise HTTPException(status_code=409, detail="Fournisseur fixé par l'environnement serveur")
        app.state.routing_settings.select(data.provider, data.profile)
        return app.state.routing_settings.status(operator=True)

    @app.post("/routing/keys")
    def save_routing_key(data: RoutingKeyInput, actor: Actor, request: Request):
        assert_local_operator(actor, request)
        env_key = "SIMCO2_GEOAPIFY_API_KEY" if data.provider == "geoapify" else "ORS_API_KEY"
        if os.getenv(env_key):
            raise HTTPException(status_code=409, detail="Clé gérée par l'environnement serveur")
        # Uniquement côté serveur, jamais dans les journaux, snapshots ou réponses.
        app.state.routing_settings.put_key(data.provider, data.key)
        return app.state.routing_settings.status(operator=True)

    @app.delete("/routing/keys/{provider}")
    def remove_routing_key(provider: str, actor: Actor, request: Request):
        assert_local_operator(actor, request)
        env_key = "SIMCO2_GEOAPIFY_API_KEY" if provider == "geoapify" else "ORS_API_KEY"
        if os.getenv(env_key):
            raise HTTPException(status_code=409, detail="Clé gérée par l'environnement serveur")
        app.state.routing_settings.remove_key(provider)
        return app.state.routing_settings.status(operator=True)

    @app.post("/routing/test")
    def test_routing(data: RoutePreviewInput, actor: Actor, request: Request):
        assert_local_operator(actor, request)
        router = active_router()
        if router is None:
            raise RoutingFailure("provider_unconfigured", "Configurer un fournisseur de routage")
        if app.state.routing_provider is None:
            profile = app.state.routing_settings.selected()[1]
        else:
            profile = data.profile or "driving-car"
        result = router.route(data.origin, data.destination, profile)
        return {"distance_m": str(result.distance_m), "duration_s": str(result.duration_s),
                "provider": result.provider, "profile": profile,
                "restrictions": list(result.restrictions), "valid_at": result.valid_at}

    @app.post("/routing/resolve")
    def resolve_route(data: RouteResolveInput, actor: Actor, db: Db, request: Request):
        if actor["username"].startswith("guest_"):
            db.consume_public_quota(request.client.host if request.client else "unknown",
                                    "route", 40)
        provider = active_router()
        if provider is None:
            raise RoutingFailure("provider_unconfigured", "Routage non configuré sur le serveur")
        start, start_label = app.state.geocoder.locate(data.origin)
        stop, stop_label = app.state.geocoder.locate(data.destination)
        profile = data.profile or ("driving-car" if app.state.routing_provider is not None
                                   else app.state.routing_settings.selected()[1])
        route = provider.route(start, stop, profile)
        if not route.geometry or route.geometry.get("type") != "LineString":
            raise RoutingFailure("invalid_geometry", "Le fournisseur n'a pas fourni de tracé")
        from decimal import ROUND_HALF_UP
        distance = int(route.distance_m.to_integral_value(rounding=ROUND_HALF_UP))
        duration = int(route.duration_s.to_integral_value(rounding=ROUND_HALF_UP))
        if not distance or not duration:
            raise RoutingFailure("invalid_result", "Distance ou durée calculée invalide")
        payload = RouteInput.model_validate({
            "origin": start_label, "destination": stop_label,
            "distance_m": distance, "duration_s": duration,
            "provider": route.provider, "source": "Routage automatique: " + route.provider,
            "origin_coordinates": start, "destination_coordinates": stop,
            "geometry": route.geometry, "valid_at": route.valid_at,
            "profile": profile, "restrictions": list(route.restrictions),
        }).model_dump(mode="json")
        quote_id = db.save_route_quote(actor["id"], payload)
        return {"quote_id": quote_id, "route": payload, "expires_in_seconds": 1800}

    @app.post("/routing/preview")
    def route_preview(data: RoutePreviewInput, actor: Actor, request: Request):
        assert_local_operator(actor, request)
        # Ancienne API conservée pour les outils experts.
        key = app.state.routing_settings.key_for("ors")
        router = ORSRoutingProvider(key) if key else None
        if router is None:
            raise RoutingFailure("provider_unconfigured", "Clé ORS absente sur le serveur")
        out = router.route(data.origin, data.destination, data.profile or "driving-hgv")
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
