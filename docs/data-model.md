# Modèle de données conceptuel (v1)

Tous les identifiants sont UUID; dates en UTC avec `timezone` Europe/Paris par défaut d'affichage; mesures SI internes (m, s, Wh/J selon convention stabilisée), conversions explicites; devise EUR initiale. Les tables référentielles sont historisées ou liées à `version_id`.

| Entité | Champs métier / relations clés |
|---|---|
| User | id, login, password_hash / external_auth_id, active, created_at |
| AuditEvent | actor_id, entity_type/id, action, time, before/after redacted |
| Country | iso3166, currency, timezone_default |
| EnergyType | code, label, family, canonical_unit (L, kg, kWh, Nm³...), density/conversion explicit if needed |
| EnergyCountryVersion | country, energy, price_per_unit, valid_from, source, source_date, manual_override, revision |
| EmissionFactor | country, energy, perimeter `{tank_to_wheel, well_to_wheel, lifecycle}`, kg_co2e/unit, methodology, source, version, completeness |
| VehicleModel / VehicleVariant | manufacturer/model, type bus/van/car, seats, standing_places optional, dimensions, max_mass, energy_carrier, engine, capacity, connectors, tank/pack usable energy, reserve, driving restrictions |
| VehicleConsumptionProfile | variant_version, `{fixed, contextual, measured}`, distance coefficient, time coefficient, passenger/weather/relief factors, auxiliary consumption, measurement protocol, source |
| VehicleCostProfile | variant_version, purchase, lifespan, residual, lease, annual fixed, maintenance km, maintenance h, insurance, finance, labor assumptions (if applicable), source |
| VehicleTest | variant_version, date, route/test conditions, energy_used, distance, duration, payload, measurement uncertainty |
| Station | name, geo_point, access_type, owner, opening_hours, operational_status, source/date, active |
| StationEquipment | station_id, energy, plug/pressure/connector, max_power_kw, available_ports, shared_power_kw, flow_rate, availability schedule |
| Depot | geo_point, capacities, charging/refuel equipment optional, available hours |
| RouteDefinition | origin, destination, optional via, stops, routing_profile, directionality, geometry/version |
| DemandEntry | route_id, date/time window, departure target optional, passenger_count, SLA/window hard/soft, calendar_pattern |
| Scenario / ScenarioRevision | owner, title, dates, mode, network policy, fleet policy, objective, constraints, ref/version IDs, status |
| FleetCandidate | scenario_revision, variant_id, available_count/max_count, depot relations |
| Run / RunInputSnapshot | scenario_revision, input JSON signed/hashed, provider/version, solver config, state |
| Assignment / Trip | run, vehicle_instance, trip_id, route, start/end, passenger_count, passenger_km, actual occupancy, empty_km, feasibility |
| StopActivity | run, vehicle, type `{loading, unloading, break, empty_move, refuel, charge, depot_wait}`, station_id, time, kWh/kg/L, SoC before/after |
| RunResult | fleet counts, route-level costs, aggregate TCO, kgCO2e, passenger counts, warnings, optimality, infeasibility reasons |
| ReportArtifact | run_id, pdf_path, checksum, generated_at, template_version |

## Invariants
- Tarif énergie : unique **par pays et énergie et version/période**, indépendant des stations. On doit pouvoir figer plusieurs révisions historiques, sans ambiguïté sur celle utilisée.
- Facteur d'émission : `(country, energy, perimeter, version)`; ACV véhicule ne peut pas être réduite mécaniquement au seul `kgCO₂e/kWh`; conserver catégories fabrication/fin de vie, durée de vie et allocation des impacts.
- Un véhicule ne chevauche jamais deux affectations; `seats >= boarded_passengers` à tout instant; réserves respectées avant toute liaison.
- Les kilomètres à vide et les charges aux stations sont tracés séparément des trajets avec passagers.
- Montants calculés avec Decimal ou représentation monétaire sûre, arrondis seulement à la présentation; aucune double imputation des coûts fixes.
- `0` passager : ne pas diviser par zéro; indiquer « non applicable » pour coût/passager, pas 0.
- Les imports n'écrasent pas les modifications locales et passent par une prévisualisation de diff.
