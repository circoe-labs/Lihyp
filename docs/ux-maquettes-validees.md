# UX validée — écrans Simulations et Véhicules

Implémentation des deux maquettes approuvées le 24 novembre 2026.

## Simulations
- Composition **gauche** : itinéraire, choix compacts de véhicules, hypothèses de service et options avancées repliées.
- **Droite** : carte/itinéraire avec indicateurs de routage réellement fournis, action « Comparer », tableau de résultats de la comparaison, **une** frise de service sélectionnable par modèle puis autocar.
- Pas de distances, horaires, stations, prix ni CO₂e décoratifs : avant calcul les métriques affichent « — » ; après calcul les résultats viennent du routage et des snapshots du moteur.
- Courses = courses voyageurs planifiées (pas une preuve d'optimalité, ni nécessairement des allers-retours).
- Le fournisseur de carte ne recalcule pas les distances. Sans Leaflet, affichage du schéma et avertissement déjà prévus.
- Les erreurs de prévalidation restent accolées au bouton de comparaison. L'historique conserve ses fonctionnalités sous un panneau repliable.

## Véhicules
- Une seule bibliothèque : onglets **Bibliothèque (9)** et **Mes véhicules**, jamais deux séries de tuiles affichées ensemble.
- Bandeau de statistiques réelles, filtres recherche/énergie/places/constructeur, cartes en grille 3/2/1 colonnes selon largeur, panneau de détails et formulaire d'édition réservé à l'administrateur.
- Données de références fournies par l'utilisateur : prix, consommations et capacités restent marqués **non vérifiés**.
- Autonomie affichée = `(capacité utile - réserve) / consommation par km`, estimation hors consommation horaire et conditions de conduite. Les coûts sur 100 km restent indicatifs hors TCO complet.
- Les stations, énergies et leurs prix ne sont ni préremplis ni inventés. La création de véhicule reste une action explicite d'administrateur.

## Recette
- `python -m pytest -q` : tests Python.
- `PYTHONPATH=src:tests python tests/browser_ux_review.py` : recette Chromium si Chromium et Playwright sont installés (facultatif, test hors ligne avec données fictives seulement).
- Vérifications navigateur : affichage public, carte et fallback hors ligne, comparaison de 4 motorisations, sélection de frise, filtres et onglets de catalogue, connexion admin, et contrôles de débordement et de chevauchement à 1920 / 1280 / 820 / 390 px.
- Données de la recette artificielles. Le routage réel et l'optimisation des stations restent soumis aux limites existantes du moteur ; ne pas présenter les valeurs de la maquette comme les résultats attendus.
