# Correctif UX — comparaison non lancée et tracé d'itinéraire invisible

Statut : correctif prototype, 23 novembre 2026. Ne modifie ni les règles métier du moteur ni le calcul routier serveur.

## Causes repérées dans l'interface

1. Le bouton « Comparer les véhicules » déclenche une comparaison **à partir de deux véhicules admissibles**. Un véhicule dépourvu d'énergie configurée n'est pas admissible. Le formulaire s'arrêtait sans afficher d'alerte à proximité du bouton ; le message commun était en haut de page, souvent hors écran.
2. Les champs obligatoires des « Options avancées » pouvaient empêcher la soumission native du formulaire avant l'exécution du gestionnaire JavaScript, sans ouvrir automatiquement le panneau fermé.
3. Le calcul d'itinéraire peut réussir tandis que le navigateur n'a pas chargé la bibliothèque Leaflet depuis son CDN. Dans ce cas, le serveur possède une géométrie, mais la carte interactive ne peut pas la tracer. Les anciens tests hors ligne validaient le bandeau de repli, pas un tracé visible.

## Corrections

- Afficher une alerte de proximité immédiatement sous le bouton lorsque des véhicules admissibles manquent, que le trajet n'est pas calculé, qu'un champ obligatoire est invalide, ou que l'API retourne une erreur. Indiquer également la progression et la réussite.
- Au clic sur Comparer, ouvrir « Options avancées » si un de ses champs est invalide ; la validation native conserve ses garde-fous.
- Utiliser Leaflet pour tracer l'itinéraire lorsqu'il est disponible. Sinon, dessiner **la géométrie réelle fournie par le serveur sous forme de schéma SVG**, avec point de départ et d'arrivée, sans nécessiter de bibliothèque externe. L'avertissement indique clairement que ce n'est *pas* un fond cartographique en ligne.
- Masquer le tracé devenu obsolète lorsque l'origine ou la destination change ; un nouveau calcul routier est alors requis. Le CSS empêche toujours le débordement des tuiles.

## Vérifications manuelles sur Windows

1. Avec un seul véhicule et une énergie configurée, cliquer **Comparer les véhicules** : une explication apparaît juste sous le bouton ; aucune comparaison fictive n'est affichée.
2. Créer un second véhicule, configurer son énergie, choisir les deux modèles. Cliquer **Calculer l'itinéraire** puis **Comparer les véhicules** : le résultat apparaît en-dessous.
3. Vider un champ avancé obligatoire, refermer le panneau, puis cliquer sur Comparer : le panneau s'ouvre et le champ est indiqué.
4. Désactiver temporairement le chargement de Leaflet et recalculer Caen → Rouen : un schéma de tracé avec deux extrémités et la géométrie serveur est affiché. Lorsque Leaflet fonctionne et que les tuiles sont accessibles, la carte OSM interactive reste préférée.
5. Modifier la destination : le tracé précédent doit disparaître jusqu'au recalcul. Vérifier les libellés FR/EN.

## Limites explicites

- Deux véhicules restent requis pour une **comparaison** ; le correctif n'invente pas de second véhicule. Les résultats dépendent des hypothèses énergie/véhicule saisies.
- Le schéma de secours ne remplace pas une carte routière géographique avec fond de carte, échelle et interaction. Un blocage CDN ou réseau doit encore être résolu pour rétablir l'affichage OSM interactif.
- Les profils routiers choisis ne certifient pas l'accès autocar. Les modes avancés de recharge et pauses réglementaires ne sont pas ajoutés ici.
