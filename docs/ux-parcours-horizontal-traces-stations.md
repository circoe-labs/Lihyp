# UX Lihyp — saisie horizontale, carte et stations

## Parcours simulation

- Sur grand écran, **1. Itinéraire**, **2. Véhicules** et **3. Hypothèses d'exploitation** occupent une ligne. Sur écran intermédiaire, deux colonnes et les hypothèses sur la largeur ; sur mobile, une colonne.
- **Carte et itinéraire**, **Comparer**, **Comparaison** et **Détail d'une solution** viennent ensuite et occupent la largeur du contenu. Le tableau de comparaison utilise donc tout l'espace disponible.
- Les listes de véhicules sont défilables dans le bloc qui les contient, pas dans une longue page de cartes.
- Le bandeau global de mise en garde, les micro-mentions répétitives et les titres « Paramètres » ont été retirés. **Les sources, unités et métadonnées de qualité ne sont pas effacées de la base, des historiques ni des rapports.**

## Carte et itinéraire

- Utilise la **géométrie LineString reçue du fournisseur** pour construire une polyline Leaflet, avec contour blanc et trait turquoise.
- Si Leaflet est absent ou ne dessine aucune ligne SVG visible, présente **le même tracé géographique** sous forme de schéma SVG. Il n'est jamais remplacé par une droite artificielle entre les villes.
- Si le fournisseur ne renvoie pas de coordonnées utilisables, la zone indique explicitement que le tracé n'est pas disponible.
- Le fond de carte interactif dépend toujours de la bibliothèque et des tuiles OpenStreetMap externes ; un fonctionnement hors réseau reste limité au schéma géométrique. Aucun itinéraire réel n'a été certifié par le test hors ligne.

## Stations

- Survolez le marqueur pour une **infobulle compacte** (nom, énergie, emplacement).
- Cliquez pour afficher **la fiche détaillée** avec informations d'accès et de provenance.
- Les marqueurs changent de taille au survol, puis retrouvent leur état sans laisser une fenêtre contextuelle ouverte.

## Recette

`python tests/browser_layout_station.py` : HTML/CSS/JS servis sous URLs de ressources, quatre largeurs (1920, 1280, 820, 390 px), trois colonnes ou empilement adapté, tracé de la géométrie, pas de débordement horizontal, clic et survol de station (double API Leaflet testant les événements). Les tests de livraison précédents restent requis dans GitHub Actions.

**Limites :** les valeurs de test sont des fixtures, et l'intégration avec un fournisseur réel de routage / la disponibilité réelle des stations doivent être vérifiées séparément.
