# 04 — Tests et qualité

## Pyramide de tests
- Unitaires domaine : conversions d'unités, coût, CO₂e, consommation, capacité, temps, énergie, revenus (aucun revenu demandé), absence de division par zéro.
- Propriétés/invariants : coût/émissions non négatifs, conservation de l'énergie, unités cohérentes, pas de chevauchement d'affectations, pas de transport au-delà de capacité, pas de trajet de téléportation, aucun véhicule au-dessous de sa réserve.
- Scénarios déterministes : 1 ligne/1 véhicule; demande > capacité; aller-retour; multi-jours; période changement heure hiver/été Europe/Paris; dépôt distant; réapprovisionnement obligatoire; borne occupée; absence station compatible; station fermée; véhicule inaccessible au point de départ.
- Tests méta : augmentations de distance ne réduisent pas consommation fixe (toutes choses égales), restrictions supplémentaires ne rendent pas soudain faisable un cas infeasible (sur modèle exact), changement tarif national impacte seulement coûts et non émissions.
- Tests d'intégration : adaptateur ORS fake/live sur tests smoke limités, imports de fichiers avec doublons, version snapshots, migrations PostGIS, génération PDF.
- API/UI E2E : parcours catalogue → scénario → lancement → suivi → résultats → PDF; multiutilisateur partage de catalogues, identification auteur.
- Visual QA : cartes, tableaux, états vides, erreurs de formulaires, PDF 1 et 10 pages, pagination, légendes.

## Cas d'échec à exposer
Pas de route valide; quotas API atteints; station non disponible; aucune conversion d’énergie valide; facteur d’émission absent; temps de solveur dépassé; fausse compatibilité camion/bus; demandes contradictoires. Résultat doit fournir explication et état distinct sans produire « chiffres inventés ».

## Protocole de données
Fixtures de test synthétiques marquées comme telles; jamais introduire les prix ou facteurs illustratifs en production. Contrôle origine/licence/horodatage, complétude obligatoire selon périmètre sélectionné. Imports atomiques avec aperçu et rollback.

## Performance et exploitation
Objectifs de charge et SLA à décider; mesurer taille instance (lignes, tâches, véhicules, stations, jours), temps routage, solveur, mémoire, succès. Annulation jobs, idempotence démarrage, timeout, logs corrélés `run_id` et métriques.

## Gates CI
Format/lint, types, migration vérifiable, unitaires et intégrations offline, vérification OpenAPI/contrats, sécurité basique, génération PDF, tests non-régression de fixtures. Ne livrer étape cochée qu'après validation acceptance + tests.

## Couverture effective après le premier lot (2026-11-20)

- **23 tests pytest offline passés** au dernier contrôle local, couvrant unités, DST, référence 80/50, énergie/réserve, refus ACV/multi-jours, TCO, facteurs, snapshots, schéma, audit, droits à deux utilisateurs et ORS simulé.
- Contrôle de syntaxe Python/JS, génération OpenAPI (25 paths), copie propre installable dans environnement Python provisionné. Le lint Ruff existe dans CI mais n'a pas été exécuté localement (dépendance non présente offline); CI hébergée non exécutée.
- Browser smoke Chromium via ASGI TestClient bridge : navigation et résultats vérifiés ; ne vaut pas test réseau du serveur public.
- PDF 2 pages créé par l'API, rendu en images et inspecté : pagination corrigée, chiffres identiques aux résultats gelés.
- Données de test synthétiques exclusivement; aucune validation terrain ou performance/charge, aucune base réelle Normandie.
- Gates J3 à J6 **ouverts** : dépôt/recharge/ravitaillement/optimisation, facteurs vérifiés, accessibilité, carte, backup/restauration et sécurité production.
