# Plan d’exécution / TODO

## Règles de l’orchestrateur
- Exécuter **00** d’abord; il attribue tâches, ordonne dépendances, ne coche qu’après tests et revue.
- Lire `README.md`, décisions, architecture, modèle et questions ouvertes avant modification.
- Pour tout code, charger les skills **`/caveman`** et **`/coding-guideline`** s’ils sont présents dans `~/ai/skills/`; si absents, signaler absence et appliquer discipline équivalente (code modulaire, tests).
- Ne jamais inventer sources, facteurs carbone, réglementation, stations actives ou statut d’optimalité.
- Actualiser ce fichier ainsi que les TASK.md en cas de changement de plan; consigner décision dans `docs/01-decision-log.md`.
- Une seule tâche en cours par agent sauf travaux explicitement indépendants; produire le rapport via template.

## Suivi des tâches (statut du lot prototype du 20 novembre 2026)

- [x] **00 — Piloter les tâches et décisions** (`00-orchestrator/TASK.md`)
- [x] **01 — Stabiliser conventions et contrats** (`01-architecture-contracts/TASK.md`)
- [x] **02 — Initialiser dépôt et CI** (`02-repo-skeleton/TASK.md`)
- [x] **03 — Types et unités métier** (`03-domain-units/TASK.md`)
- [x] **04 — Comptes et journal d’audit** (`04-auth-audit/TASK.md`)
- [x] **05 — Schéma pays, énergies et facteurs** (`05-country-energy-schema/TASK.md`)
- [ ] **06 — Référentiel initial énergies** (`06-energy-seeding/TASK.md`)
- [ ] **07 — Écran énergies par pays** (`07-energy-ui/TASK.md`)
- [ ] **08 — Modèle et versions de véhicules** (`08-vehicle-schema/TASK.md`)
- [ ] **09 — CRUD véhicules et essais** (`09-vehicle-crud-ui/TASK.md`)
- [ ] **10 — Import véhicules CSV/XLSX** (`10-vehicle-import/TASK.md`)
- [x] **11 — Modèle des stations et équipements** (`11-stations-schema/TASK.md`)
- [ ] **12 — Saisie et import stations** (`12-station-import/TASK.md`)
- [ ] **13 — Synchronisation externe contrôlée** (`13-station-sync/TASK.md`)
- [ ] **14 — Géocodage et routage** (`14-routing-adapter/TASK.md`)
- [ ] **15 — Schéma scénarios et snapshots** (`15-scenario-schema/TASK.md`)
- [ ] **16 — Assistant de configuration des simulations** (`16-scenario-ui/TASK.md`)
- [ ] **17 — Calculateur énergétique déterministe** (`17-calculator-energy/TASK.md`)
- [ ] **18 — Calculateur TCO et allocation** (`18-calculator-cost/TASK.md`)
- [ ] **19 — Calculateur CO₂e par périmètre** (`19-calculator-emissions/TASK.md`)
- [ ] **20 — Planificateur simple ligne** (`20-baseline-scheduler/TASK.md`)
- [ ] **21 — Continuité jours et dépôts** (`21-multi-day-depot/TASK.md`)
- [ ] **22 — Moteur de ravitaillement** (`22-refuel-engine/TASK.md`)
- [ ] **23 — Simulation des bornes et files** (`23-charging-engine/TASK.md`)
- [ ] **24 — Optimisation réseau et flotte** (`24-optimizer/TASK.md`)
- [ ] **25 — Contraintes réglementaires configurables** (`25-regulatory-rules/TASK.md`)
- [ ] **26 — API d’exécutions et progression** (`26-simulation-jobs/TASK.md`)
- [ ] **27 — Résultats interactifs comparables** (`27-results-ui/TASK.md`)
- [ ] **28 — Rapport PDF professionnel** (`28-pdf-report/TASK.md`)
- [ ] **29 — Validation finale, sécurité et livraison** (`29-e2e-hardening/TASK.md`)

## État du lot vertical (2026-11-20)
- Clôturées après revue et tests : **00, 01, 02, 03, 04, 05, 11**.
- Toutes les autres tâches restent ouvertes, même lorsque des capacités partielles existent.
- **23 tests Python réussis** ; UI Chromium via pont ASGI, contrôle PDF 2 pages, installation depuis copie propre dans environnement provisionné.
- Voir `reports/implementation-review.md` et `reports/task-XX-closure.md` pour les preuves, réserves et dépendances.
- Le travail a été fait par étapes de spécialité suivies de passes de revue, **sans exécution d'agents délégués** : le runtime ne fournit pas de mécanisme de sous-agents.
- Décisions métiers Q1-Q23 inchangées ; Q24 non arbitrée (visibilité scénarios limitée au propriétaire temporairement).
