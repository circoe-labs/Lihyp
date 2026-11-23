# Registre de revue d’implémentation — SimCO2

**Date : 20 novembre 2026 | État : prototype local, pas de livraison métier finale.**

## Résultat et méthode de contrôle

Le transfert livré contenait **30 tâches numérotées et aucune application**. Un premier lot vertical J2 a été codé.
L’équipe de travail ci-dessous est une répartition des passes de conception / implémentation / audit, **pas un ensemble de sous-agents réellement lancés** (outil absent).

| Passe | Périmètre | Contrôle transversal / action de reprise |
|---|---|---|
| Architecte / contrats | Décisions, unités, protocole routage et statuts | Rejet de toute « optimalité prouvée » dans un moteur de heuristique; états stricts et ADR réversible. |
| Domaine / calcul | Consommation, capacité, coût, émissions, baseline | Fixture 80/50, garde réserve d’énergie, non-double-compte WTW, absence de retour fictif. |
| API / données / sécurité | Versions, auth, audit, snapshot, catalogue | Tests à deux utilisateurs, Argon2, tokens hachés; refus de tarification station; triggers de versions. |
| Produit / restitution | UI en français, résultats, PDF, sources | Reprise du PDF après détection d’un titre « Courses » orphelin; rendu PDF final confirmé. |
| QA d’intégration | Tests offline, navigateur ASGI, revue task-by-task | Reprise de l’immutabilité : triggers ajoutés aux coordonnées de station et test de régression ajouté. |

**Preuves locales :** `python -m pytest -q` => **23 passed** ; `python -m compileall -q src tests` ; `node --check src/simco2/ui/app.js`; 25 routes OpenAPI ; installation editable depuis une copie propre dans le Python déjà provisionné. Le pipeline CI GitHub est déclaré mais **son exécution distante et le lint Ruff ne sont pas attestés**. Navigateur Chromium avec pont ASGI testé, non preuve d’un déploiement HTTP réseau. Un rapport PDF 2 pages a été ouvert, rendu et relu, avec coûts et émissions concordant avec l’API sauvegardée.

**Fixture synthétique uniquement :** 80 voyageurs / 50 places, 100 km/course, 0,2 L/km, 2 EUR/L, 2,7 kgCO2e/L => **2 véhicules + 2 courses, 40 L, 80 EUR, 108 kgCO2e direct**. Ces chiffres ne sont PAS des données nationales vérifiées.

## Verdict par tâche (une tâche ouverte reste ouverte)

| ID | État | Vérification / manque restant |
|---:|---|---|
| 00 | **Acceptée** | Pilotage et arbitrages : Classification des 30 tâches, dépendances et limites explicites. |
| 01 | **Acceptée** | Contrats et conventions : Interfaces Routage/Moteur, unités, statuts et décisions provisoires tracés. |
| 02 | **Acceptée** | Socle et CI : Installation editable depuis copie propre dans Python provisionné, tests offline et contrat OpenAPI OK; CI distante non exécutée. |
| 03 | **Acceptée** | Unités métier : Somme L+kWh refusée, conversions explicites et heure locale DST refusée/sélectionnée. |
| 04 | **Acceptée** | Comptes, accès et audit : Deux comptes; catalogues communs; traçabilité, mots de passe Argon2, tokens hachés et expiration. |
| 05 | **Acceptée** | Modèle énergie par pays : Facteurs directs/WTW versionnés; prix uniquement par énergie/pays; versions immuables. |
| 06 | Bloqué par sources | France et codes énergie amorcés sans prix/facteurs nationaux vérifiés, licences ni dates de validité confirmées. |
| 07 | Partiel | Saisie, révisions et historique UI présents ; pas de preview de comparaison détaillée, dépendance aux références nationales 06 ouverte. |
| 08 | Partiel | Versions de véhicules et quelques attributs compatibles ; variabilité de variantes, réservoirs multiples et tests complets non modélisés. |
| 09 | Partiel | Formulaire et catalogue véhicule présents ; fiche exhaustive et provenance des essais non finalisées. |
| 10 | Non commencé | Import CSV/XLSX, mapping, doublons, aperçu/rollback absents. |
| 11 | **Acceptée** | Stations et équipements : Stations multi-énergie/connecteurs, coordonnées et éléments historiques immuables; tarifs stations refusés. |
| 12 | Partiel | Stations saisissables via API et UI, mais imports CSV/XLSX/GeoJSON et UX équipement multi-formulaire absents. |
| 13 | Non commencé | Synchronisation externe vérifiée, licences, suivi et rollback non implémentés. |
| 14 | Partiel | ORS server-side avec gestion d’erreurs et provider fixture testé offline ; géocodage, cache, validation de gabarit autocar et test externe live manquants. |
| 15 | Partiel | Scénarios/révisions/snapshots de run persistants ; demande et flotte multi-modalité structurées non disponibles. |
| 16 | Partiel | Formulaire scénario minimal mono-ligne, sans assistant complet ni carte. |
| 17 | Partiel | Consommation fixe pure exacte, stratégies contextuelle/mesurée non livrées. |
| 18 | Partiel | TCO variable/véhicule/complet limité, allocation pure testée ; mutualisation réelle entre lignes et règles de ventilation non validées. |
| 19 | Partiel | Direct et puits-roue sans double-compte, facteurs versionnés ; ACV incomplète délibérément refusée. |
| 20 | Partiel testé | 80 passagers sur 50 places => 2 courses; ordonnancement simplifié 1 véhicule par course, sans trajets retour, rotation ou réemploi. |
| 21 | Non commencé | Continuité jours et dépôts absents. |
| 22 | Non commencé | Ravitaillement, compatibilité énergétique et itinéraires stations absents. |
| 23 | Non commencé | Recharge, files et ports partagés absents. |
| 24 | Non commencé | Optimisation du réseau et flotte mixte, résultats certifiés/gap absents. |
| 25 | Non commencé | Contraintes réglementaires vérifiées absentes. |
| 26 | Partiel | API de lancement et persistance synchrone ; queue, jobs, idempotence, annulation, retries et progression absents. |
| 27 | Partiel | Détails + tableau de runs à chiffres cohérents ; comparaisons multicritères, dashboard carte/planning absents. |
| 28 | Partiel vérifié | PDF de 2 pages rendu, totaux accordés API et provenance visible ; aucune carte ou comparaison, dépendance 27 incomplète. |
| 29 | Partiel / bloqué | 23 tests et QA écran/PDF, mais pas de tests réels Normandie, charge, sauvegarde, sécurité production ou recette métier finale. |

## Contrôle de cohérence par rapport au but du produit

Le produit final doit **simuler la demande multi-ligne et multi-jours**, dimensionner des flottes homogènes/mixes avec repositionnements, dépôts, ravitaillement et recharge, et comparer TCO et CO₂e à périmètre égal. Le lot exécutable ne couvre qu’une **course aller orientée répétée avec un véhicule distinct par course**. Il constitue une démonstration des contrats et invariants, pas un solveur de flotte réel.

La base fournit des versions de catalogues, snapshots SHA-256 et résultats persistés. Les facteurs/prix sont hypothétiques et saisissables mais étiquetés non vérifiés; ils ne sont pas automatiquement importés d’une autorité. Les facteurs CO₂e « direct » et « puits à la roue » sont calculés comme alternatives, sans addition. ACV incomplète refusée. Les résultats ne sont jamais `optimal`.

**Décision Q24 :** accès aux catalogues partagé; scénarios et runs visibles du propriétaire uniquement **provisoirement**, à faire arbitrer. Décisions Q1–Q23 inchangées.

## Ordre de délégation recommandé (paquets de travail à attribuer)

Les paquets ci-dessous sont **des instructions préparées, non des missions déjà déléguées**. Les sorties doivent être relues dans leur ensemble et corrigées si l’intégration ou les critères échouent.

1. **Sources de données (06, 07, 10, 12, 13)** — vérifier et citer prix/facteurs/années/licences + import atomique à aperçu, statut de station contrôlé. **Gate** : deux versions correctes, sources, tests d’import doublons/erreurs et absence de faux prix station.
2. **Modélisation métier et scénarios (08, 09, 14, 15, 16, 17)** — véhicule variantes et plusieurs réservoirs, demand modes/dates/créneaux, route ORS cachée/cache/profils compatibles, calibrations énergie. **Gate** : cas de retour réaliste et absence de « géométrie inventée », validation de snapshot.
3. **Exploitation (18, 19, 20, 21, 22, 23)** — règles TCO confirmées, ACV avec sources, rotations et état véhicule entre jours, ravitaillement, files de bornes. **Gate** : fixture 3 jours, conservation énergie, impossibilité de téléportation, coûts de flotte répartis exactement une fois.
4. **Optimisation (24, 25, 26)** — contraintes configurables vérifiées, flotte mixte/network solveur, vraie file de jobs, idempotence/cancel/timeout et gap. **Gate** : attestations de faisabilité, temps limite et statut d’optimalité vérifiés; doublons de lancement bloqués.
5. **Restitution / validation (27, 28, 29)** — tableaux comparables, dashboard/cartes, rapport PDF cartographié, contrôle accessibilité et sécurité, perf/sauvegardes. **Gate** : chiffres identiques dans trois vues, PDF et données figées, tests E2E et jeux Normandie validés par le métier.

## Réserves empêchant une mise en production

- Q24 et autres questions ouvertes non approuvées (rotation exacte, allocation fixe, service partiel, règles réglementaires, ACV).
- Absence de données de référence réelles vérifiées France/Normandie et de validation de l’exactitude de routes pour autocars.
- SQLite mono-poste et runs synchrones : aucun SLA, gestion de charge, quotas, isolation worker, backups/restaurations démontrés.
- CI distante et lint non vérifiés, pas de pentest ni audit opérationnel ; HTTP local seulement.
- Pas de preuve de conformité complète aux 30 critères; les tâches restantes ne sont pas clôturées.

## Commandes de reprise

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q src tests
python -m simco2.cli init-db
python -m simco2.cli create-user --username analyste
python -m uvicorn simco2.api.app:app --host 127.0.0.1 --port 8000
```

Voir `IMPLEMENTATION.md` pour la procédure d’utilisation, et les `reports/task-XX-closure.md` pour chaque tâche acceptée.
