# Premier lot UX : simulations directes, routage, carte, anglais et stations normandes

Statut : **prototype**, non prêt pour un service externe permanent. Dernière revue : 23 novembre 2026.

## Parcours utilisateur

- L'application ouvre directement **Simulations** après connexion. Aucune vue d'ensemble et aucune page autonome « Résultats & PDF » : les résultats et le bouton PDF sont dans la simulation.
- Les formulaires de véhicules, énergies et stations manuelles restent accessibles comme **paramètres** ; les options avancées sont repliées par défaut.
- Une bascule **FR / EN** en haut à droite change les écrans, tableaux, messages courants, textes des formulaires, et la langue du PDF. Préférence conservée uniquement dans le navigateur (localStorage). Les libellés techniques reçus du moteur peuvent rester en français lorsque leur traduction n'est pas connue ; la traçabilité des résultats bruts est préservée.
- La saisie de l'origine et de la destination déclenche un **calcul demandé explicitement par le bouton** ; l'utilisateur ne renseigne plus les mètres ni les secondes. Un changement des lieux invalide le calcul précédent.
- La carte Leaflet/OpenStreetMap montre la ligne et ses points de départ/arrivée quand la bibliothèque et les tuiles sont accessibles. Sans connexion aux ressources cartographiques, un message indique la limitation, sans donner une fausse carte.

## Routage automatique et reproductibilité

- Géocodage des adresses/communes françaises : **Géoplateforme (IGN/BAN)**, `https://data.geopf.fr/geocodage/search`.
- Mode de démonstration par défaut : calcul routier par `https://router.project-osrm.org/route/v1/driving`. Cette infrastructure publique est un **service de démo**, sans engagement de disponibilité, sans gestion des dimensions ou restrictions d'autocars et sans garantie de conformité réglementaire.
- Mode ORS optionnel avec `ORS_API_KEY` et `SIMCO2_ROUTING_PROVIDER=ors` ; profil utilisé : `driving-car` dans le parcours actuel. Les profils ORS ne suffisent pas à certifier l'accès autocar.
- Un service OSRM **géré par l'exploitant** peut être configuré au moyen de `SIMCO2_OSRM_URL` et `SIMCO2_ROUTING_PROVIDER=osrm`. Les conditions, la confidentialité, les quotas, la couverture et la qualité doivent encore être vérifiés avant mise en production.
- En cas d'indisponibilité, aucun kilométrage ni temps n'est inventé ; l'application affiche l'erreur.
- L'API `POST /routing/resolve` retourne un `route_quote_id` lié à l'utilisateur, utilisable 30 minutes. Le serveur enregistre le fournisseur, les coordonnées, la géométrie, la distance, la durée et les avertissements. `POST /scenarios` copie le devis en **snapshot immuable** ; un client ne peut pas faire passer une distance modifiée pour un résultat du fournisseur.
- Les simulations antérieures utilisant une route manuelle restent acceptées via API avec `provider=manual`, pour compatibilité des archives. Elles ne sont plus la méthode proposée dans le nouveau formulaire.

## Répertoire des stations en Normandie

- **Hydrogène** : 7 lieux H₂ géolocalisés recensés par H2-Mobile (Rouen, Bretteville-sur-Odon, Pont-l'Évêque, Val-de-Reuil, Douains, Le Vieil-Évreux et Lillebonne), données figées à la revue du 23/11/2026. Localisations issues du GeoJSON public : `https://www.h2-mobile.fr/json/json-stations-h2.php`. Liste et fiches : `https://www.h2-mobile.fr/stations-hydrogene/region-normandie/`.
- Leur disponibilité annoncée, leur statut public/privé, les pressions de remplissage et la compatibilité avec les **autocars** ne sont **pas certifiés** par cette intégration. Certaines fiches ciblent voitures et utilitaires. Le droit de réutilisation, le suivi de mise à jour et les confirmations exploitants restent à valider avant un service public.
- **Essence / gazole** : les stations sont découvertes à la demande, en pages de 100 au plus, via le flux officiel DGCCRF : `https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/` (données sous Licence Ouverte v2.0 selon le portail). Les résultats sont restreints aux départements 14, 27, 50, 61 et 76, normalisés et mis en cache 15 minutes. Une page n'est **pas** un inventaire exhaustif ; il faut charger les pages suivantes. Si le fournisseur est indisponible, le répertoire H₂ reste visible et un avertissement apparaît.
- Les prix individuels des stations sont supprimés volontairement : conformément à la décision métier Q19, **un seul prix national par énergie et pays** est géré dans le référentiel énergie. Le flux de stations n'entre pas dans les calculs de coût ni de ravitaillement.
- La carte est un annuaire **informatif** ; elle ne simule pas encore les arrêts de ravitaillement, l'accessibilité autocar, la disponibilité réelle, ni le détour vers une station.

## Publication pour utilisateurs externes

Cette PR **n'effectue aucun déploiement**. Démarrer en local sur `127.0.0.1` ne rend pas le site accessible à l'extérieur. Pour un service toujours disponible, il faudra : hébergement avec HTTPS, domaine, configuration de secrets et de quotas, base de données durable et sauvegardée, stratégie d'inscription/gestion des comptes, sécurité et conformité RGPD, contrôle des fournisseurs de routage et de cartographie (y compris droits de réutilisation), suivi d'incidents, surveillance, et vérification des données de référence nationales.

## Recette

```bash
python -m pytest -q
python -m compileall -q src
node --check src/simco2/ui/app.js
PYTHONPATH=src python tests/browser_smoke.py  # Linux QA avec Playwright/Chromium installés
```

Tests de routage et géocodage avec des doubles HTTP : aucune donnée nationale ni station réelle n'est supposée disponible pour la CI. Le navigateur smoke est **facultatif** sur les postes sans Playwright. Les captures de contrôle local sont générées sous `reports/new_*.png` (non nécessaires au fonctionnement de l'application).
