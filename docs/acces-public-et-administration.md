# Acces public et administration Lihyp (PR de securisation)

## Principe

- L'interface et les comparaisons sont accessibles sans formulaire de connexion. Une session visiteur temporaire est etablie via `POST /public/session` (cookie HttpOnly, SameSite=Lax, expiration 8 h). Elle conserve les simulations propres au navigateur pendant cette session ; ce mode **ne remplace pas les comptes utilisateurs persistants**.
- Dans l'onglet **API de routage**, l'exploitant s'authentifie avec le compte `admin` et le mot de passe qu'il a choisi. Son jeton est conserve uniquement dans la memoire de la page et ne constitue pas un cookie visiteur. Un rechargement verrouille de nouveau l'administration mais maintient la session visiteur.
- Les visites publiques peuvent **consulter** les energies, vehicules et stations, sans les modifier. Les changements d'energies, de vehicules, de stations et de routage necessitent une session admin : le serveur renvoie 403 a une session visiteur, y compris en appelant directement l'API. Les cles Geoapify/ORS ne sont ni affichees ni retournees au navigateur.
- Les endpoints publics de routage ne renvoient pas les cles du fournisseur. Des quotas horaires simples limitent les sessions, routages et comparaisons. Une mise en production publique exige aussi un limiteur de debit et une supervision **au niveau du reverse proxy**, et un mecanisme d'anti-abus plus robuste.

## Initialiser le compte administrateur (Windows)

Depuis la racine Lihyp, avec le serveur arrete et **dans le dossier contenant `simco2.sqlite`**, ouvrir PowerShell :

```powershell
.\.venv\Scripts\python.exe -m simco2.cli create-user --username admin
```

Si le compte `admin` existe deja, definir un nouveau mot de passe sans modifier les donnees :

```powershell
.\.venv\Scripts\python.exe -m simco2.cli set-password --username admin
```

Le mot de passe est saisi sans affichage et doit compter au moins 12 caracteres. `set-password` invalide les sessions admin precedentes. Ni l'application ni le depot ne contiennent un mot de passe par defaut.

La variable d'environnement `SIMCO2_OPERATOR_USERNAME` permet de changer l'identifiant autorise ; par defaut `admin`.

## Securite et limites

- L'authentification admin a distance **exige HTTPS**, et il faut configurer un serveur ou un reverse proxy TLS. En local `http://127.0.0.1:8000` fonctionne. Ne jamais exposer directement Uvicorn sur Internet sans configuration de securite deployee.
- Les sessions publiques sont temporaires, ne restaurent pas les historiques apres expiration et stockent des comptes ephemeres dans SQLite. Nettoyage et retention restent a developper.
- Des quotas par adresse du client au niveau application existent, mais ne constituent pas une protection DDoS fiable. Le calcul d'itineraire utilise un fournisseur externe potentiellement payant : prevoir quotas contractuels, restrictions de cle API et limites au reverse proxy.
- Les sauvegardes de la base `simco2.sqlite` et des reglages de routage restent indispensables. La PR ne migre pas vers PostgreSQL.
- Les versions d'energies et de vehicules restent conservees pour l'audit des calculs passes.

## Test manuel de recette

1. Aller sur la racine : les simulations sont visibles sans connexion.
2. Aller a **Energies par pays** : consulter la liste ; la modification demande l'acces administrateur.
3. Aller a **API de routage**, saisir `admin` et le mot de passe choisi.
4. Retourner a **Energies par pays**, ajouter une energie en remplissant pays, prix (point ou virgule decimal), source, date et licence ; le message de confirmation apparait sous la liste. Un champ invalide affiche une erreur a cote d'Enregistrer.
5. Cliquer **Actualiser** : la page reste sur les energies, sans retour au portail. Une actualisation complete du navigateur reste en mode public, et l'admin doit se reconnecter dans **API de routage**.
6. Dans **Vehicules**, observer les cartes sur plusieurs colonnes, puis verifier sur mobile qu'elles repassent sur une seule colonne.
