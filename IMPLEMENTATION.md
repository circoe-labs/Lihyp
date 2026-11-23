# SimCO2 — prototype exécutable (lot vertical J2)

**État au 20 novembre 2026 : prototype local, non prêt pour la production.**
Le ZIP de handoff d'origine ne contenait pas de code. Ce dépôt conserve ses 30 tâches
et ses décisions Q1 à Q23. Les choix techniques sont provisoires (ADR-0001),
la question Q24 reste ouverte. La matrice de recette et les limites sont dans
`reports/implementation-review.md`.

## Installer et démarrer

Prérequis : Python 3.11+ et accès aux dépendances PyPI lors de la première installation.
Depuis la racine du projet :

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m simco2.cli init-db
python -m simco2.cli create-user --username analyste
python -m uvicorn simco2.api.app:app --host 127.0.0.1 --port 8000
```

Le mot de passe est demandé de manière interactive (12 caractères minimum).
Ouvrir `http://127.0.0.1:8000/` pour l'interface en français et
`http://127.0.0.1:8000/docs` pour l'API OpenAPI.
Aucun compte ni aucune donnée de prix/facteur nationale n'est préchargé.
La base `./simco2.sqlite` est créée localement, **à ne pas publier**.
Changer son emplacement avec `SIMCO2_DB_PATH=/chemin/prive/simco2.sqlite`.
Ne pas exposer ce service sur Internet sans reverse proxy TLS, configuration
et audit de sécurité complémentaires.

## Interface simplifiée (premier lot du 23 novembre 2026)

Après connexion, l'onglet **Simulations** s'ouvre directement. L'utilisateur saisit
le départ, l'arrivée et le nombre de voyageurs, puis clique sur
**Calculer l'itinéraire** : la distance et la durée sont fournies par IGN + OSRM
(démonstration par défaut), avec une carte et un avertissement sur les restrictions
autocars. L'utilisateur ne peut plus saisir lui-même les mètres ou les secondes
dans le formulaire ; l'API historique conserve les scénarios manuels pour archives.

Les **résultats et le téléchargement PDF sont dans Simulations**, sans page dédiée.
Le bouton **FR / EN** change l'interface et la langue du PDF. L'onglet
**Stations en Normandie** présente sept lieux hydrogène H2-Mobile identifiés
et les stations essence/gazole du flux DGCCRF, chargées par pages et sans prix
station. Les données de stations restent indicatives et les valeurs de prix et
d'émission nationales ne sont pas devinées.

Voir `docs/ux-routing-i18n-stations.md` pour les fournisseurs, avertissements,
conditions de réutilisation et prérequis de mise en ligne.

Configuration facultative pour un routage autre que la démonstration OSRM :
`SIMCO2_ROUTING_MODE=geoapify` et `SIMCO2_GEOAPIFY_API_KEY`, ou
`SIMCO2_ROUTING_MODE=ors` et `ORS_API_KEY` côté serveur. Un OSRM administré
est disponible avec `SIMCO2_ROUTING_MODE=osrm` et `SIMCO2_OSRM_URL`.
**Ce prototype local n'est pas encore hébergé pour les utilisateurs externes.**


## Correctif cartes et catalogue de démonstration (23 novembre 2026)

- La feuille `/assets/leaflet-layout.css` est désormais servie localement : les cartes
  d'itinéraire et de stations restent confinées à leur cadre, même si la feuille
  Leaflet externe ne charge pas. Les tuiles et le script Leaflet demandent
  toujours une connexion Internet ; le service de routage reste estimatif.
- Dans **Véhicules**, un **autocar diesel fictif 50 places** est présenté dans le
  catalogue vide (20 L/100 km, réservoir de 100 L). Cliquer sur **Ajouter cet exemple**
  pour l'enregistrer volontairement ; aucun constructeur réel ou donnée nationale
  validée n'est ainsi attribué à tort. Il pourra ensuite être sélectionné dans
  les simulations après création d'une énergie compatible.
- Dans **Énergies**, le bouton affiche **Enregistrer** et non **Enregistrer une version** ;
  la protection de l'historique des anciennes simulations est inchangée.
- Les tests navigateur reproduisent les tuiles débordantes **sans CSS CDN**.
  Voir `docs/cartes-et-catalogue-exemple.md` pour les détails et la recette Windows.

Pour actualiser un environnement local après fusion : `git pull origin main`, puis
redémarrer Uvicorn. Si une ancienne page reste visible dans le navigateur,
recharger sans cache avec `Ctrl+F5`.

## Comparaisons et paramètres de routage (PR #2 complétée)

La page Simulations évalue **2 à 8 modèles** sous les mêmes hypothèses : date,
trajet calculé (devis serveur), demande, flotte maximale, périmètre TCO et CO₂e.
Les prix/facteurs proviennent de la dernière version enregistrée du référentiel
France correspondant à l'énergie du modèle. Si elle manque, le comparatif est
refusé avec une explication, jamais chiffré avec un prix inventé. Chaque modèle
est résolu **séparément** (pas de flotte mixte) et conserve son diagnostic,
son PDF individuel et un snapshot SHA-256. Une solution irréalisable reste affichée.
Les groupes sont consultables dans « Comparaisons enregistrées » ; un ancien
résultat reste inchangé après modification des références.

Dans **Paramètres > API de routage** : consulter le fournisseur, l'endpoint, le
profil et les clés présentes (jamais la valeur), puis tester un itinéraire.
En local, l'utilisateur **admin** sur l'interface loopback peut enregistrer une clé
Geoapify ou ORS et choisir le fournisseur/profil. Les clés sont conservées
**dans un fichier serveur hors dépôt** (`~/.simco2/routing-settings.json`), avec
permissions restreintes sur POSIX, et non dans les données de simulation ou
le stockage du navigateur. **Ce fichier est un stockage de confort local, pas un
coffre-fort pour une application hébergée.** En production, fournir des variables
d'environnement/secrets (jamais de clés dans Git), supprimer la gestion de clés
par navigateur, et déployer l'authentification, les quotas, HTTPS et la supervision.
Un compte externe ou une connexion non locale ne peut pas modifier ces paramètres.

La sélection automatique privilégie Geoapify **si sa clé existe**, sinon ORS,
puis OSRM public **à titre de démonstration uniquement**. Les profils Geoapify
sont `bus` (autocar par défaut), `truck` (22 t) et `heavy_truck` (40 t) ; leurs
restrictions dépendent des données cartographiques et ne prouvent pas la
conformité locale. Les calculs de distance et de temps ne sont pas vérifiés en
conditions réelles dans cette livraison (tests mockés). Source :
https://apidocs.geoapify.com/docs/routing/

Voir `docs/multivehicule-et-api-routage.md` pour la recette, les API et les limites.

## Parcours minimal testable

1. Se connecter avec son compte.
2. Dans « Énergies », enregistrer une hypothèse de prix et deux facteurs directs / puits-roue ; renseigner une source et une date. Ces valeurs sont **non vérifiées**.
3. Ajouter un véhicule compatible (capacité, unité, consommation, réserve, origine de l'information).
4. Dans « Simulations », saisir le départ, l'arrivée et les voyageurs, puis calculer le trajet avec le fournisseur configuré.
5. Choisir **au moins deux véhicules** et lancer la comparaison de solutions indépendantes ; inspecter coût, CO₂e et faisabilité par véhicule, puis exporter le PDF propre à chacun. Les valeurs des référentiels sont copiées dans un snapshot SHA-256.

**Fixture de recette synthétique (non officielle)** : 80 voyageurs, 50 places,
100 000 m par course, 7 200 s, 0,2 L/km, 0 L/h, capacité 100 L,
réserve 5 L, tarif hypothétique 2 EUR/L, facteur direct hypothétique
2,7 kgCO2e/L, deux véhicules autorisés. Attendu : 2 courses aller simple,
40 L, 80 EUR au périmètre TCO variable, 108 kgCO2e en direct.
Aucun trajet retour, navette inter-course ou repositionnement n'est inventé.

## Tests et preuves

```sh
python -m pytest -q
python -m compileall -q src
node --check src/simco2/ui/app.js  # Node.js facultatif pour le contrôle JS
python tests/browser_smoke.py      # Playwright Chromium facultatif, installé séparément
```

Le test navigateur utilise un pont de requêtes vers l'application ASGI,
car la navigation localhost directe est restreinte dans l'environnement de revue.
Il ne démontre pas une intégration réseau publique. Les PDF sont testés via l'API,
puis inspectés après rendu en images (voir `reports/example-illustrative.pdf`).
Les dépendances officielles et la CI sont définies dans `pyproject.toml` et
`.github/workflows/ci.yml`; le statut réel des tests est consigné dans la revue.

## Modules et frontières

- `src/simco2/domain`: contrats, quantités sûres et moteurs de calcul déterministes.
- `src/simco2/adapters`: SQLite, audit, versions, ORS optionnel et fixture de routage.
- `src/simco2/api`: API FastAPI, schémas stricts, authentification, snapshots.
- `src/simco2/ui`: interface responsive de démonstration.
- `src/simco2/reporting.py`: rendu de PDF depuis un résultat enregistré.
- `migrations/`, `tests/`, `docs/adr/`, `reports/`: migration, vérifications,
  hypothèses et traçabilité.

Pour prévisualiser une route ORS, déclarer une clé **seulement côté serveur** dans
`ORS_API_KEY`. Les résultats d'une prévisualisation ne sont pas substitués
silencieusement à la distance manuelle d'un scénario. Le profil `driving-hgv`
**n'atteste pas** la navigabilité des autocars ni les limitations locales.

## Périmètre explicitement non livré

Le moteur de service ne résout **pas** le problème de flotte complet : lignes
multiples, mélange des véhicules, réemploi en rotations, multi-jours, dépôts,
repositionnements, recharge et ravitaillement, import CSV/XLSX/GeoJSON, contraintes
réglementaires, optimisation certifiée, scénarios de demande détaillée,
optimisation multicritère, cartographie hors ligne et émissions ACV ne sont pas implémentées.
La **comparaison de 2 à 8 modèles indépendants** est disponible, mais elle n'est
ni une flotte mixte ni une optimisation d'affectation.
Les modes correspondants sont rejetés ou laissés indisponibles, **jamais annoncés
comme optimisés ou vérifiés**. Les calculs TCO complet sont limités aux postes
explicitement saisis. Le prix est unique par pays/énergie; aucun prix station n'existe.

## Prochaines étapes

Consulter `reports/implementation-review.md` pour l'ordre de délégation et les
critères de sortie. Valider en priorité les sources de données, la politique Q24,
les règles de rotation/dépôt et les périmètres TCO/CO2e avant la sophistication
du solveur ou la connexion à des données réelles.
