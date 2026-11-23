# Rapport de clôture — tâche 02 : Socle et CI

**Statut :** réussi dans le périmètre du prototype, réserve de production.  
**Révision code :** lot de livraison initial, sans SHA Git (dossier ZIP).  
**Auteur / date :** implémentation et revue structurées, 2026-11-20.

## Objectif et résultat

Installation editable depuis copie propre dans Python provisionné, tests offline et contrat OpenAPI OK; CI distante non exécutée.

## Fichiers / modules changés

`pyproject.toml; .github/workflows/ci.yml; src/simco2/*; tests/*`.

## Contrats et décisions

Q1-Q23 restent verrouillées et inchangées. ADR-0001 = architecture **provisoire** ; Q24 demeure ouverte. Domaine indépendant de FastAPI/SQLite; valeurs nationales non préchargées ni réputées officielles.

## Tests exécutés (commandes, sorties, preuves)

- `python -m pytest -q` : **23 passed**, suite offline.
- `python -m compileall -q src tests` : attendu sans erreur, exécuté au contrôle final.
- Installation `pip install --no-deps --no-build-isolation -e <copie propre>` : réussie dans l'environnement provisionné, puis 22 tests passés avant l'ajout du test stations immuables; relancée au contrôle final.
- Contrat OpenAPI : 25 paths générés sans erreur.
- UI/PDF : `reports/browser_overview.png`, `reports/browser_results.png`, `reports/example-illustrative.pdf`.

## Vérifications métier (TCO, CO₂e, route, énergie)

Fixture illustrée 80 passagers, 50 sièges : deux courses, 40 L, 80 EUR, 108 kgCO2e direct ; aucun tarif national certifié. Modèle d'énergie/de coûts/carbone et cohérence référentielle testés conjointement. Le routage ORS externe n'a pas été appelé.

## Limites, risques, hypothèses

Le prototype n'inclut pas les modes d'optimisation, imports, dépôts, multi-jours ni réglementation. Les CI hébergées, le déploiement Internet et les données nationales restent hors preuve. Voir revue centrale pour le registre complet.

## Journal / docs / TODO mis à jour

`tasks/TODO.md`, `docs/adr/0001-architecture-technique-provisoire.md`, `docs/adr/0002-registre-implementation.md`, `reports/implementation-review.md`, `IMPLEMENTATION.md`.

## Prochaine tâche admissible

Task 06 : obtenir et vérifier données et licences pays-énergies avant de rendre les valeurs de référence utilisables.
