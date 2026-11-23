# Task 29 — Validation finale, sécurité et livraison

## Goal
Exécuter recette bout en bout et préparer déploiement fiable.

## Context
Simulateur transport voyageurs Normandie, tarifs nationaux par énergie et pays, référentiels/versionnement, calculs TCO et CO₂e. Voir `docs/01-decision-log.md` et `docs/open-questions.md`. **Oui : charger `/caveman` et `/coding-guideline` depuis `~/ai/skills/` si disponibles.**

## Scope
### In Scope
Tests perf limites, sauvegarde/restauration, journaux, droits, accessibilité, check release, doc opérateur.

### Out of Scope
Fonctionnalités d'autres tâches; changements métier non validés; données externes fictives en production; optimisations prématurées.

## Dependencies
28 et tous les composants activés. Vérifier les prérequis dans `tasks/TODO.md`; si tâche amont est en échec, bloquer et documenter.

## Implementation Steps
1. Relire décisions et interfaces touchées; noter hypothèses non tranchées.
2. Écrire contrat et cas de test ciblés avant le comportement.
3. Implémenter **seulement** le périmètre : Tests perf limites, sauvegarde/restauration, journaux, droits, accessibilité, check release, doc opérateur.
4. Vérifier intégration/sérialisation/erreurs et documentation; collecter preuves.
5. Mettre à jour `tasks/TODO.md`, remettre rapport de fin de tâche.

## Files Likely Touched
Modules correspondant à `e2e-hardening` dans `domain/`, `api/`, `adapters/`, `ui/`, `tests/`, migrations le cas échéant; chemins définitifs selon ADR de tâche 01.

## Architecture Constraints
Frontières service/adaptateur, types explicites, unités sûres, diagnostics typés, invariants, snapshot versionné quand applicable. Ne pas lier domaine au fournisseur ORS, au framework UI ou à l'ORM. Pas de valeurs nationales inventées; respect du prix national unique Q19.

## Testing Requirements
Tests unitaires et intégration offline sur fixtures déterministes, au moins un cas nominal, un cas erreur et une frontière métier; tests de régression pour toute règle chiffrée. CI et contrôle manuel UI/PDF si pertinent.

## Acceptance Criteria
- [ ] Recette sur fixtures Normandie validées; aucun bug bloquant critique.
- [ ] Exécution des tests pertinents réussie; preuves et résultats inclus au compte-rendu.
- [ ] Documentation et décisions ouvertes mises à jour sans changer une décision verrouillée.
- [ ] Aucun placeholder présenté comme fonctionnalité finie.

## Documentation Updates
Mettre à jour `docs/02-architecture-spec.md` si contrat change, `docs/04-testing-and-quality.md` si nouvelle couverture, `docs/open-questions.md` pour arbitrages, `tasks/TODO.md` pour statut.

## Handoff Notes
À transmettre au prochain agent : fichiers touchés, commandes lancées, captures de résultats/test, limitations, risques, ADR applicables et prochaine tâche admissible. Pas de confiance implicite dans des données externes non vérifiées.

## État d’implémentation du lot 2026-11-20

**Ouvert (non accepté).** Un ou plusieurs critères/sous-modules ne sont pas démontrés. Détails et travaux à reprendre : `../../reports/implementation-review.md` (ligne tâche 29). Aucun succès du prototype ne vaut clôture automatique.
