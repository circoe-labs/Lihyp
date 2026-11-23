# Task 00 — Piloter les tâches et décisions

## Goal
Orchestrer le handoff, contrôler l’avancement et préserver la cohérence des décisions.

## Context
Simulateur transport voyageurs Normandie, tarifs nationaux par énergie et pays, référentiels/versionnement, calculs TCO et CO₂e. Voir `docs/01-decision-log.md` et `docs/open-questions.md`. **Non (orchestration)**

## Scope
### In Scope
Lire tout le dossier; établir état initial; contrôler dépendances et compléter TODO avant chaque changement; enregistrer rapports; modifier ou scinder des TASK.md si nécessaire.

### Out of Scope
Fonctionnalités d'autres tâches; changements métier non validés; données externes fictives en production; optimisations prématurées.

## Dependencies
Aucune. Vérifier les prérequis dans `tasks/TODO.md`; si tâche amont est en échec, bloquer et documenter.

## Implementation Steps
1. Relire décisions et interfaces touchées; noter hypothèses non tranchées.
2. Écrire contrat et cas de test ciblés avant le comportement.
3. Implémenter **seulement** le périmètre : Lire tout le dossier; établir état initial; contrôler dépendances et compléter TODO avant chaque changement; enregistrer rapports; modifier ou scinder des TASK.md si nécessaire.
4. Vérifier intégration/sérialisation/erreurs et documentation; collecter preuves.
5. Mettre à jour `tasks/TODO.md`, remettre rapport de fin de tâche.

## Files Likely Touched
Modules correspondant à `orchestrator` dans `domain/`, `api/`, `adapters/`, `ui/`, `tests/`, migrations le cas échéant; chemins définitifs selon ADR de tâche 01.

## Architecture Constraints
Frontières service/adaptateur, types explicites, unités sûres, diagnostics typés, invariants, snapshot versionné quand applicable. Ne pas lier domaine au fournisseur ORS, au framework UI ou à l'ORM. Pas de valeurs nationales inventées; respect du prix national unique Q19.

## Testing Requirements
Tests unitaires et intégration offline sur fixtures déterministes, au moins un cas nominal, un cas erreur et une frontière métier; tests de régression pour toute règle chiffrée. CI et contrôle manuel UI/PDF si pertinent.

## Acceptance Criteria
- [x] Registre cohérent, pas de tâche cochée sans preuve; prochains travaux déterminés.
- [x] Exécution des tests pertinents réussie; preuves et résultats inclus au compte-rendu.
- [x] Documentation et décisions ouvertes mises à jour sans changer une décision verrouillée.
- [x] Aucun placeholder présenté comme fonctionnalité finie.

## Documentation Updates
Mettre à jour `docs/02-architecture-spec.md` si contrat change, `docs/04-testing-and-quality.md` si nouvelle couverture, `docs/open-questions.md` pour arbitrages, `tasks/TODO.md` pour statut.

## Handoff Notes
À transmettre au prochain agent : fichiers touchés, commandes lancées, captures de résultats/test, limitations, risques, ADR applicables et prochaine tâche admissible. Pas de confiance implicite dans des données externes non vérifiées.

## Compte-rendu et preuve du lot 2026-11-20
Tâche acceptée sur le périmètre vérifiable du prototype : voir `../../reports/task-00-closure.md`. Les choix métier/prod non traités restent ouverts.
