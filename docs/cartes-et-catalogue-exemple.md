# Correctifs de l'interface - cartes, catalogue et enregistrement

**Date :** 23 novembre 2026. **Statut :** prototype, tests locaux ; validation sur le poste utilisateur encore nécessaire.

## 1. Cartes dans Simulations et Stations en Normandie

### Problème observé

Sur Windows, les tuiles OpenStreetMap peuvent déborder des deux cartes et recouvrir les formulaires, y compris les sections « Véhicule et énergie ». Une cause plausible est l'absence de chargement du CSS Leaflet depuis le CDN alors que le JavaScript a été chargé. Sans les règles CSS de positionnement/masquage, les images de tuiles et les panneaux Leaflet ne sont pas confinés dans leur conteneur.

### Protection appliquée

- `src/simco2/ui/leaflet-layout.css` est **servi par l'application locale** et chargé dans `index.html` indépendamment du CDN.
- Il fournit les règles minimales pour le positionnement relatif du conteneur, les calques absolus, l'ordre d'empilement et la présentation de base des contrôles.
- `style.css` impose `overflow: hidden`, `isolation: isolate` et `contain: layout paint` aux deux cartes. Les tuiles ne peuvent donc plus masquer les champs voisins ni la navigation.
- Les cartes recalculent leur taille après ouverture/changement d'onglet et lors des changements de dimensions (ResizeObserver). Les marqueurs départ/arrivée sont désormais vectoriels, sans images d'icônes externes.
- Si le JavaScript Leaflet est indisponible, le message de repli reste affiché. Si les tuiles OSM sont indisponibles, la carte peut être vide ; le logiciel ne prétend pas afficher des données hors ligne.

**Recette manuelle requise :** Windows PowerShell, Chrome/Edge, connexion réelle ; calcul Caen-Rouen, passage à Stations, redimensionnement fenêtre, navigation FR/EN et zoom de navigateur. Vérifier que toute carte reste dans son cadre et n'empêche pas de cliquer dans les formulaires. Le test navigateur reproduit un DOM Leaflet avec feuille CSS externe absente et une tuile artificiellement surdimensionnée ; il ne remplace pas une recette avec les serveurs de tuiles réels.

## 2. Premier autocar dans « Solutions de transport »

Le catalogue présente un **autocar diesel de démonstration** lorsque la base ne contient pas encore de véhicule : 50 places, consommation fictive 0,2 L/km (20 L/100 km), réservoir utile 100 L et réserve 5 L. Aucun constructeur réel, aucune fiche homologuée, aucun prix ni facteur d'émission national n'est inventé. La carte est marquée « Exemple fictif ».

L'exemple est un **aperçu** jusqu'à ce que l'utilisateur clique sur « Ajouter cet exemple ». L'action crée alors un véritable modèle enregistré via l'API existante. L'ouverture de la page ou la connexion ne crée aucune donnée implicitement. Un modèle enregistré devient sélectionnable dans Simulations ; les valeurs peuvent être modifiées, sans changer les résultats historiques. Le catalogue présente désormais les données sous forme de fiches détaillées (places, énergie, consommation, capacité, source) plutôt qu'un tableau de codes et de révisions.

## 3. Libellé « Enregistrer »

Le bouton des énergies affiche désormais **« Enregistrer »** (anglais **« Save »**). Le bouton des véhicules reste « Enregistrer le véhicule ». La création ou modification garde une trace d'historique en interne : les scénarios anciens pointent vers la révision utilisée au moment de leur exécution, et ne sont pas recalculés silencieusement. Les détails de révision restent disponibles via « Historique » ; le numéro de version n'encombre plus le catalogue principal.

## Tests

- `python -m pytest -q` : tests de non-régression, règles CSS locales, libellés et absence d'ajout silencieux de l'exemple.
- `PYTHONPATH=src python tests/browser_smoke.py` : parcours FR/EN, carte de simulation et carte de station avec CSS CDN indisponible simulé, ajout explicite de l'autocar, enregistrement d'une énergie et d'un véhicule, simulation et résultat PDF.
- `node --check src/simco2/ui/app.js` et `python -m compileall -q src`.

La version reste un **prototype mono-ligne** : aucun fournisseur de routage ne garantit pour l'instant les contraintes d'un autocar ; les données stations et les facteurs nationaux ne sont pas certifiés.
