# Lot UX : stations de Normandie et énergies par pays

Statut : proposition de PR, 23 novembre 2026. Cette interface reste un prototype ; ne pas l'utiliser comme répertoire d'avitaillement certifié.

## Stations en Normandie

- Les filtres **H₂**, **Essence**, **Gazole** et **Manuelle** sont des cases indépendantes. Une station-service qui distribue plusieurs carburants est comptée dans chacun des filtres pertinents, mais n'apparaît qu'une seule fois dans la liste.
- La carte et la liste des lieux visibles sont côte à côte sur grand écran, puis superposées verticalement sur mobile. La liste est défilante.
- Le survol d'un point ouvre sa fiche Leaflet, le clic la maintient et affiche aussi les détails dans le panneau à droite. Cliquer une ligne recentre la carte et ouvre la fiche. La liste et la fiche restent utilisables même sans tuiles ni bibliothèque cartographique.
- La fiche présente uniquement les données disponibles : nom, adresse, carburants, pression H₂ déclarée si présente, provenance et avertissement sur les accès autocar. **Aucun prix local** n'est diffusé ou affiché.
- Les nombres des filtres ne représentent que les stations actuellement **chargées** : les stations de carburants DGCCRF sont paginées et leur disponibilité dépend du service externe. Leur répartition par carburant n'est pas un inventaire exhaustif de la Normandie.
- Une donnée d'annuaire H₂ référencée n'est pas une preuve de fonctionnement, ni d'accessibilité à un autocar. Vérifier auprès de l'exploitant et les restrictions locales.
- Un lien vers la source n'est affiché que si la valeur source est une URL HTTP(S) valide ; les champs de la fiche sont échappés pour ne pas interpréter de code HTML de tiers.

## Énergies par pays

- La vue d'accueil devient un tableau de consultation de prix nationaux et facteurs par **énergie, prix/unité, direct, puits-à-roue, source, actions**. Le gros formulaire n'est plus affiché d'emblée.
- **Ajouter une énergie** ouvre le formulaire ; **Modifier** préremplit ce formulaire et interdit de changer le code d'énergie pendant la modification (une nouvelle version technique est enregistrée en interne).
- **Retirer du catalogue** demande confirmation puis masque l'énergie des nouvelles simulations. La suppression physique des versions historiques est interdite par la base. Enregistrer à nouveau cette énergie la rend à nouveau visible.
- L'historique reste consultable pour les énergies visibles, et les anciens calculs et références restent inchangés après retrait ou modification.
- Aucun prix ou facteur national non vérifié n'est inséré automatiquement. Les chiffres vus dans les maquettes sont illustratifs, **pas des valeurs prêtes à l'emploi**.
- Les libellés de ces fonctions sont disponibles en français et en anglais.

## Vérifications

`python -m pytest -q` — y compris tests d'archivage, d'authentification et de conservation de l'historique.

`PYTHONPATH=src python tests/browser_smoke.py` — Parcours Chrome/Chromium hors-ligne : liste, filtres et détails de stations, formulaire énergie caché par défaut, création, modification et historiques, traduction FR/EN et clipping des cartes.

`node --check src/simco2/ui/app.js` — Contrôle syntaxique.

## À confirmer sur un poste connecté

Tester les fonds de carte réels OSM sous Windows Chrome/Edge, les popups au survol et au clic, la pagination DGCCRF complète, le chargement rapide des points, la lisibilité mobile et les limites d'utilisation des sources. L'accès aux cartes et au service DGCCRF dépend de services tiers.
