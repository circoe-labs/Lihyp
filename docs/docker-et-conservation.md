# Lihyp : Docker et conservation des simulations

## Politique de conservation
- Chaque visiteur public reçoit un espace personnel (cookie HttpOnly, SameSite=Lax).
- L'espace dure **20 minutes après son ouverture**, quelle que soit l'activité. Actualiser le navigateur ne prolonge pas ce délai.
- Un balayage serveur toutes les **30 secondes** supprime définitivement : utilisateurs invités expirés, jetons, devis d'itinéraires, scénarios et révisions, exécutions, comparaisons et membres, journaux d'audit associés.
- L'accès API est refusé immédiatement dès la fin des 20 minutes, même entre deux balayages. Une page encore ouverte se recharge après expiration et repart sur une nouvelle session publique.
- Les simulations créées **pendant une authentification administrateur** restent enregistrées. Une connexion administrateur ultérieure ne transforme pas les simulations invitées précédentes en historiques permanents.
- Les référentiels partagés (énergies, véhicules, stations) restent permanents.
- Toute simulation temporaire utile doit être exportée en PDF **avant la fin de la session**. La suppression est définitive.

## Lancer en conteneur
Prérequis : Docker Desktop (Windows) avec Docker Compose, ou Docker Engine + Compose.

Depuis le dossier du dépôt :
```powershell
docker compose up -d --build
docker compose ps
```
Ouvrir http://127.0.0.1:8000. Pour les journaux : `docker compose logs -f app`. Pour arrêter sans perdre les données : `docker compose down`.

Les données administrateur et la configuration du routage sont stockées dans le volume nommé `lihyp_data`. **Ne pas utiliser `docker compose down -v`** : cette commande supprime le volume et ses données.

Créer le compte administrateur (une fois) :
```powershell
docker compose run --rm app python -m simco2.cli create-user --username admin
```
Si le compte existe déjà :
```powershell
docker compose run --rm app python -m simco2.cli set-password --username admin
```
Aucun mot de passe n'est livré avec l'image. Le mot de passe est demandé dans le terminal.

**Connexion admin dans Docker Desktop en local :** le port Docker est lié à
`127.0.0.1`, mais Docker peut transmettre les requêtes depuis une adresse
privée de passerelle. Dans ce cas, l'authentification HTTP est volontairement
refusée. Pour une utilisation **strictement locale**, créer un fichier
`.env` contenant `SIMCO2_DOCKER_LOCAL_HTTP_ADMIN=1`, puis redémarrer
`docker compose up -d`. **Supprimer cette option et utiliser HTTPS avant
toute publication en ligne.** Ne jamais l'activer lorsque le conteneur est
accessible via un proxy ou un réseau non fiable.

## Avant la publication Internet
Cette configuration est une **base de conteneurisation**, pas une mise en production complète.
- Le port est lié uniquement à `127.0.0.1` : placer un reverse proxy HTTPS (certificats et en-têtes fiables) devant l'application. L'accès administrateur exige HTTPS hors loopback.
- Le conteneur fonctionne avec un utilisateur non privilégié et **un seul processus Uvicorn**. SQLite gère plusieurs visiteurs simultanés modestes, mais il n'est pas conçu pour plusieurs réplicas/serveurs en écriture. Migrer vers PostgreSQL et mettre en place des tâches distribuées avant de monter horizontalement en charge.
- Les limites de routage (40/h) et comparaison (20/h) s'appliquent **à chaque session visiteur**, pas au proxy commun. Les créations de session sont limitées par IP (100/h par défaut, configurable via `SIMCO2_PUBLIC_SESSIONS_PER_IP_HOUR`).
- Derrière un reverse proxy, configurer `SIMCO2_TRUSTED_PROXY_IPS` et `FORWARDED_ALLOW_IPS` avec **les adresses exactes** des proxys contrôlés ; ils doivent remplacer les valeurs `X-Forwarded-For` fournies par les visiteurs. Ne jamais utiliser un joker pour faire confiance à toutes les origines.
- Utiliser des secrets serveur pour les API et mettre en place sauvegardes **cohérentes** de SQLite (via l'API sqlite3 backup), surveillance, politiques de trafic et gestion des mises à jour.
- Le routage OSRM de démonstration n'est pas garanti pour des calculs de production ou les gabarits autocars.
- Conserver la commande locale Python / `.venv` pour le développement et les tests ; Docker est une autre manière de déployer le même code Python.
