# 02 — Architecture cible (proposition à confirmer)

## Style
Monolithe modulaire web pour la v1 avec traitements de simulation asynchrones **en tant que jobs côté serveur**, événements de progression stockés, worker isolé. Pas d’obligation microservices. Séparer algorithme métier des API, de l’ORM, du moteur de routage, et du PDF.

## Pile suggérée, non choisie par le client
- Frontend TypeScript/React ou équivalent, cartographie Leaflet/MapLibre, graphiques, formulaires typés.
- API backend Python/FastAPI ou équivalent, domaine fortement typé, worker de simulation Python, solveur OR-Tools/CP-SAT selon formulation.
- PostgreSQL + PostGIS (géométrie) et migrations; Redis/file pour jobs seulement si utile; stockage objet PDF.
- OpenRouteService via adaptateur `RoutingProvider` substituable; quotas, timeouts, retry raisonnable, cache et signature des matrices.
- ReportLab/HTML→PDF, avec rendu déterministe et contrôle de mise en page.

**Les suggestions ne sont pas des décisions du demandeur.** Décider en tâche 01 sur critères de maintenance, licences, coûts, déploiement.

## Frontend : écrans
Véhicules (liste/detail/variantes/essais/import); API et Routage (clé masquée, vérification); Énergies (pays/énergies/prix/facteurs/version); Stations (carte/liste/import/compatibilité); Simulation (configuration réseau+demande+période+flotte+objectif+contraintes, progression); Résultats (table, fiches, dashboard, carte et planning); utilisateurs (login). Sauvegarde et partage selon arbitrage Q24.

## Modules backend
`identity`, `reference_data`, `vehicles`, `energy`, `stations`, `routing`, `demand`, `scenarios`, `simulation`, `optimizer`, `accounting`, `emissions`, `reporting`, `audit`. Flux : validation entrée → snapshot versionné → pré-calcul routes/matrice et compatibilité → planification/solveur → évaluation déterministe coûts/émissions → vérification contraintes → résultats immuables → PDF.

## Contrats d'adaptateurs (interfaces)
- `RoutingProvider.route(origin, destination, vehicle_profile, departure_time?) -> RouteResult | RoutingError`; `matrix(positions, vehicle_profile)`. Émettre distance_m, duration_s, geometry, provider/version, valid_at, profile, restrictions.
- `EnergyReferenceRepository(country, version)`; `StationDataProvider.fetch()` validé avant activation.
- `OptimizationEngine.solve(snapshot, time_limit_s, random_seed) -> SolveResult` incluant status `{optimal, feasible, infeasible, timeout_with_solution, timeout_no_solution, invalid_input}` et bound/gap si disponibles.
- `PdfRenderer.render(result_snapshot, template_version) -> PDF`.

## Versionnement / reproductibilité
Chaque exécution fixe `scenario_revision`, `catalog_vehicle_versions`, `energy_country_price_factors`, `station_versions`, `routing_snapshot`, `solver_version`, `objective_weights`, `seed`, `time_limit`, `timezone`, `units`; ne recalculer que sur action explicite. Résultats et PDF comportent un identifiant de simulation et la date.

## API indicative, à stabiliser en contrat OpenAPI
`/auth/*`, `/vehicles`, `/vehicles/{id}/versions`, `/vehicles/imports`, `/energies/countries/{iso}`, `/stations`, `/stations/imports`, `/routing/preview`, `/scenarios`, `/scenarios/{id}/revisions`, `/simulation-runs`, `/simulation-runs/{id}`, `/simulation-runs/{id}/results`, `/simulation-runs/{id}/report.pdf`.

## Sécurité et fiabilité
Clé ORS stockée côté serveur et jamais exposée, journaux sans secrets, TLS, authentification, validation d'import et taille fichiers, audit auteur/date, limitation d'API, sauvegardes restaurables, quotas jobs par utilisateur. Même droits métier = pas d'absence de sécurité.

## Découpage du solveur
(1) normaliser demandes et calendriers, (2) créer tâches de course, (3) générer arcs temporellement faisables incluant trajets à vide, (4) résoudre affectation et routage de flotte, (5) intégrer station/énergie selon fidélité sélectionnée, (6) calculer TCO/CO₂e et vérifier contraintes, (7) évaluer plusieurs solutions et comparer, (8) rendre diagnostics. Pour grands problèmes, heuristique + borne et statut clair; pas d’optimalité inventée.

## Etat d'implémentation local (20 novembre 2026)

Le schéma ci-dessus demeure une **cible, non une livraison**. Le lot vertical décrit dans ADR-0001 implémente uniquement des contrats `RoutingProvider`, `SimulationEngine`, SQLite local, API FastAPI, et PDF simple. Les jobs asynchrones, PostgreSQL/PostGIS, cartographie et solveur complet restent absents. Ne pas extrapoler l'existence d'interfaces indicatives ci-dessus à une fonctionnalité livrée. La matrice de conformité figure dans `reports/implementation-review.md`.
