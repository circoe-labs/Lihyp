# Livraison UX — contrôle anti-décalage HTML / CSS / JavaScript

## Incident observé le 24 novembre 2026

Après la fusion de la refonte UX, certains navigateurs affichaient `uxFilters`, `uxDistance`, `uxVehicleDetail` et les panneaux sous forme de blocs empilés. Le code de la branche principale contenait pourtant les traductions et les règles CSS correspondantes. Les URLs auparavant non versionnées (`/assets/app.js` et `/assets/style.css`) pouvaient être reprises depuis le cache navigateur, alors que l'HTML avait changé. Cette hypothèse explique les symptômes; elle ne constitue pas une capture réseau du navigateur utilisateur.

## Correction

- `GET /` génère des références `app.js?v=<empreinte>` et `style.css?v=<empreinte>` à partir du SHA-256 des **fichiers effectivement servis**. Aucune manipulation des versions à la main, aucun second script ou CSS d'appoint.
- Les réponses `/` et `/assets/*` portent `Cache-Control: no-store` (et `Pragma: no-cache`), pour éviter les ressources de versions divergentes pendant les mises à jour suivantes.
- La table secondaire des repères énergie + maintenance sur 100 km est refermée par défaut sous **un panneau dépliable natif**. Aucune carte de véhicule n'est dupliquée.
- `tests/test_ui_asset_delivery.py` vérifie la correspondance entre les URL empreintes et les fichiers source, les en-têtes HTTP et les traductions.
- `tests/browser_delivery.py` demande au navigateur Chromium de charger les CSS/JS **par leurs URL**, en simulant un cache contenant les anciens bundles non versionnés. Il vérifie les libellés traduits, le CSS grid, les filtres et la table repliée, puis la création d'un itinéraire et une comparaison sur des données de test.
- `tests/browser_ux_review.py` conserve la recette fonctionnelle visuelle et les contrôles aux largeurs 1920, 1280, 820 et 390 pixels.
- Un job de recette Chromium est ajouté à GitHub Actions; la vérification UI n'est plus facultative.

## Installation Windows après fusion

Dans le dossier Lihyp, arrêter le serveur (`Ctrl+C`), puis exécuter `git pull origin main`, et relancer avec `.\.venv\Scripts\python.exe -m uvicorn simco2.api.app:app --host 127.0.0.1 --port 8000`. Lancer une **première** fois `Ctrl+F5` dans le navigateur pour récupérer l'HTML initial mis à jour. Les rechargements suivants utilisent les liens à empreinte.

Les fichiers de la base SQLite utilisateur ne sont ni migrés ni effacés. Aucun prix, facteur d'émission, véhicule ou calcul de simulation n'a été modifié par ce correctif.

## Limites

Les tests sont réalisés sur Chromium avec un catalogue et un fournisseur de routage fictifs. Ils ne certifient pas le rendu cartographique via l'API réelle ni la configuration Windows de chaque navigateur. Le test de livraison utilise Playwright avec les ressources provenant du TestClient FastAPI : la navigation directe vers un serveur loopback a été bloquée dans l'environnement d'exécution. Les contrôles HTTP des réponses sont exécutés séparément.
