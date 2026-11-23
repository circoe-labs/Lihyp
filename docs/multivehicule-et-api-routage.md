# Comparaison multi-véhicules et API de routage

**Statut : première itération de la PR #2 – prototype à valider sous Windows et avant hébergement public.**

## Objectif utilisateur

Le parcours de simulation sélectionne **plusieurs solutions de transport**, pas
une seule. Un même itinéraire Caen → Rouen est calculé une seule fois par le
fournisseur, avec distance, durée et tracé figés dans un devis d'une durée de 30
minutes lié à l'utilisateur. Ce devis est réutilisé pour **2 à 8 scénarios de
véhicules homogènes indépendants**. Le serveur associe à chaque véhicule la
dernière énergie disponible pour son pays et son code, puis vérifie la cohérence
unités et pays avant tout enregistrement.

La réponse `POST /comparisons` est stockée de manière atomique dans SQLite avec
une empreinte du contexte commun (`shared_sha256`) et un snapshot SHA-256 de
chaque calcul. Les résultats sont reliés à un identifiant de groupe, accessibles
à leur propriétaire via `GET /comparisons` et `GET /comparisons/{id}`. Chaque
ligne comporte son statut de faisabilité, son coût et ses émissions si
calculables, et un lien vers son PDF historique. Modifier un tarif ou véhicule
ne modifie pas les résultats archivés.

**Limites** : le moteur évalue une ligne et une journée, sans rotations,
repositionnements ni recharge. Deux véhicules sélectionnés **ne constituent pas
une flotte mixte optimisée** ; chaque véhicule est évalué comme si la flotte
était composée de ce seul modèle. En cas de données insuffisantes ou de
contrainte non satisfaite, la ligne est signalée, pas retirée du comparatif.
Aucune comparaison n'affirme un optimum garanti.

## Routage : options et clé serveur

Geoapify expose `bus`, `truck` (22 t / 4,1 m) et `heavy_truck` (40 t / 4,1 m).
Le profil **bus** est le choix par défaut pour des autocars, avec un avertissement
explicite : les restrictions dépendent de la couverture et de la qualité des
attributs OpenStreetMap. Le gabarit réel de chaque autocar et les règles locales
restent à vérifier manuellement avant exploitation. Ces profils ne sont pas des
contraintes personnalisables véhicule par véhicule. ORS offre `driving-hgv`
et `driving-car` ; OSRM public est uniquement une démonstration `driving-car`.

Documentation de référence :
- https://apidocs.geoapify.com/docs/routing/
- https://openrouteservice.org/dev/#/api-docs
- https://project-osrm.org/docs/v5.24.0/api/

- `GET /routing/config` affiche fournisseur, profil, endpoint et **booléens**
  de présence des clés, jamais leurs valeurs.
- `POST /routing/config` sélectionne fournisseur et profil parmi des choix
  validés par le serveur. Pas d'URL externe libre à injecter.
- `POST /routing/keys` et `DELETE /routing/keys/{provider}` sont limités à
  l'utilisateur `admin` (ou `SIMCO2_OPERATOR_USERNAME`) connecté depuis
  `127.0.0.1`, `::1` ou le client de tests ; aucun changement à distance.
- `POST /routing/test` appelle le fournisseur sélectionné pour deux coordonnées
  et renvoie uniquement distance, temps, avertissements et profil.
- `POST /routing/resolve` transforme un nom de lieu en devis serveur via la
  Géoplateforme française puis l'API choisie, sans exposer sa clé ; le calcul
  de comparaison n'accepte que les devis appartenant à l'utilisateur.

La première clé Geoapify enregistrée sélectionne Geoapify par défaut. Lorsque
aucune clé n'existe, le prototype peut utiliser OSRM de démonstration : ce n'est
**pas** un fournisseur de production. Les profils de la page changent la
configuration serveur ; ils ne garantissent pas que l'itinéraire calculé convient
à un véhicule précis. Par conception, la comparaison réutilise la **même**
géométrie de référence pour tous les véhicules : il faut donc vérifier les
restrictions des variantes si leurs dimensions diffèrent.

### Secrets et contraintes de déploiement

Les clés enregistrées depuis le navigateur local sont envoyées par API sous
session authentifiée et écrites dans `~/.simco2/routing-settings.json` sur le
**serveur local**. Les réponses ne contiennent jamais les valeurs, et le champ
est vidé après saisie. Elles ne vont ni dans les snapshots, ni dans SQLite, ni
dans le localStorage. Le fichier utilise un remplacement atomique et les
permissions `0600` lorsque le système les prend en charge ; son contenu reste
en clair pour le processus : **ne pas le synchroniser, publier ni le considérer
comme un coffre-fort de production**. Sous Windows, protéger le profil de
l'utilisateur et les ACL du fichier. Sur un hébergement public, injecter les
clés via un gestionnaire de secrets dans les variables d'environnement
`SIMCO2_GEOAPIFY_API_KEY` / `ORS_API_KEY` et forcer
`SIMCO2_ROUTING_MODE=geoapify` si souhaité. Ne pas distribuer de mot de passe
opérateur à des utilisateurs externes. L'accès HTTPS, les quotas, sauvegardes,
l'administration des comptes et la supervision restent à réaliser.

## Recette locale avant fusion

1. Créer deux modèles distincts (ou enregistrer l'autocar fictif puis en créer
   un second) et un tarif/facteur pour chaque énergie utilisée.
2. Dans « Simulations », saisir Caen et Rouen, calculer le parcours, sélectionner
   deux modèles et lancer la comparaison.
3. Vérifier le tableau : les deux modèles ont la même distance et le même nombre
   de voyageurs, mais leur consommation, coût et CO₂e reflètent chaque modèle.
4. Tester un modèle irréalisable : il reste affiché avec statut et diagnostic ;
   sa case de prix/CO₂e reste vide si non calculée.
5. Consulter les PDF individuels, puis modifier l'énergie et rouvrir le
   comparatif : ses chiffres restent inchangés.
6. Ouvrir « Paramètres > API de routage » : vérifier les statuts, tester une
   route, et si l'exploitant travaille en local, configurer une clé. Vérifier
   l'absence de clé en clair dans les réponses et la base SQLite.
7. Sous Chrome/Edge Windows avec Internet, essayer les cartes Simulations et
   Stations, le zoom de navigateur et l'alternance FR/EN. Les tests automatisés
   reproduisent des tuiles surdimensionnées hors CSS CDN, sans prouver la
   disponibilité de tuiles réelles sur Internet.

**Tests exécutés avant publication :** 35 tests Python, `node --check` et
parcours navigateur Chromium/Playwright avec faux routage, stations et tarifs.
Le test CI GitHub et les conditions de publication doivent être vérifiés
séparément sur la PR.
