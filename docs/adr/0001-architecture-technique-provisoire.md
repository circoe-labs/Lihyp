# ADR-0001 — Architecture prototype (20 novembre 2026)

**Statut : proposition technique réversible, non homologuée par le métier.**

## Décision provisoire

Monolithe modulaire Python 3.11+, FastAPI, SQLite pour poste de travail/prototype,
ReportLab pour la restitution, interface web HTML/CSS/JS sans outil de compilation.
Les modèles de domaine sont en `src/simco2/domain/` sans dépendance à FastAPI,
SQLite, ORS ou ReportLab. Les adaptateurs sont injectables.

Ce choix permet de lancer les tests intégralement hors ligne et de tester les calculs
avant le coût d'une infrastructure PostgreSQL/PostGIS + solveur et workers. SQLite
et les exécutions synchrones ne constituent **pas** l'architecture de production.
Le système cible garde l'option PostgreSQL/PostGIS, un worker isolé, OR-Tools et
une application frontend indépendante. Aucun de ces éléments n'est annoncé comme livré.

## Conventions et frontières

- Toutes les quantités arithmétiques utilisent `Decimal` et des unités explicites.
- Base : distance m, durée s, consommation par km et par heure dans l'unité de
  l'énergie; prix EUR/unité; facteur kgCO2e/unité. Conversion explicite.
- Pays unique par scénario; prix unique par énergie et pays, **jamais par station**.
- Date d'exploitation : date ISO, fuseau IANA; stocker instants UTC.
  Les heures locales ambiguës au changement d'heure exigent `fold` et les heures
  inexistantes sont rejetées.
- Une référence publiée est immuable : la correction crée une nouvelle version.
- Les exécutions enregistrent la copie intégrale d'entrée et SHA-256 canonique.
- Statuts de solveur : `optimal`, `feasible_not_proven`, `infeasible_proven`,
  `timeout_with_incumbent`, `timeout_no_solution`, `invalid_input`, `provider_error`.
  Le solveur prototype renvoie seulement `feasible_not_proven`, `invalid_input`
  ou `infeasible_proven` **lorsque l'infaisabilité est démontrée dans son sous-modèle**.
- Les calculs direct / puits-roue utilisent chaque facteur *en totalité* sans addition.
- Pour ce prototype, un segment est une course orientée. Les véhicules démarrent
  au point d'origine mais ne se téléportent jamais : un même véhicule ne peut
  reprendre une course sans trajet de retour fourni. Le parc est limité au nombre
  déclaré à l'entrée.

## Contrats

- `RoutingProvider.route(...) -> RouteResult` ou `RoutingFailure` typé; les
  fixtures sont explicitement synthétiques, aucun trajet routier inventé.
- `SimulationEngine.solve(snapshot) -> SolveResult` (contrat pur, pas d'E/S).
- `report.render(run, result) -> bytes` : chiffres issus du snapshot stocké.
- `POST /scenarios` -> révision; `POST /runs` -> exécution figée;
  `GET /runs/{id}` -> résultat; `GET /runs/{id}/report.pdf` -> rapport.
- JSON public : montants et mesures décimales en chaînes, pas de flottants
  binaires pour les calculs; statuts + erreurs structurées.

## Incertitudes conservées

Q24 visibilité des scénarios : **réservée temporairement au propriétaire**,
**non validé**. Catalogue partagé et droits métier identiques. Demande globale :
une amplitude de départ saisie par l'utilisateur est obligatoire. Sans
réapprovisionnement, véhicule incapable de parcourir une course -> infaisable;
les fonctions sophistiquées restent non implémentées. Frais fixes alloués aux
lignes selon temps de roulage dans le modèle pur, à valider. Prix et émissions
« hypothèse utilisateur » sont autorisés pour des essais mais indiqués comme
**non vérifiés**, jamais donnés nationaux certifiés.

## Analyse de risques et retour arrière

- Pas de comparaison vraie entre plusieurs motorisations ni solveur certifiant optimalité.
- Pas de simulation réelle de trajets retour, multi-jours, charges, files d'attente
  ou règles chauffeur sans données et moteur correspondants.
- SQLite ne remplace pas une base multi-utilisateur de production.
- Remplacement progressif possible grâce aux frontières de domaine, adaptateurs et
  snapshots. Les décisions Q1-Q23 restent inchangées.
