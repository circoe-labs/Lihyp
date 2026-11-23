# Journée par véhicule : rotations, ravitaillement sans attente et tuiles chronologiques

**Tranche expérimentale proposée dans la PR #4**, 23 novembre 2026. Simulation mono-ligne / un jour ; pas d'homologation d'exploitation. Le solveur complet Q01/Q10 et la tâche 22 restent ouverts.

## Comportement utilisateur

- L'onglet **Simulations** conserve la comparaison des 2 à 8 modèles. Chaque solution dispose d'une **tuile** reprenant coût, CO₂e, nombre d'autocars, temps de service écoulé, heures-véhicules et nombre de pleins ; à l'intérieur, une chronologie par **véhicule physique** (`V001`, `V002`…) peut être dépliée.
- La présentation existe aussi pour les résultats historiques du mode simple, sans leur inventer de retour ni de plein. En mode simple, les courses peuvent commencer simultanément sur plusieurs autocars ; l'amplitude et la somme des heures-véhicules sont calculées **séparément**, pour ne pas additionner des heures de calendrier qui se chevauchent.
- Cocher **« Planifier les rotations et les pleins de la journée (prototype) »** active une simulation journalière **opt-in**. « Départs de » devient le début du service, et « à » sa **date/heure de fin autorisée** dans le mode journée. Les horaires sont calculés en Europe/Paris (stockés en UTC).
- Depuis **Stations en Normandie**, sélectionner une station, puis **« Choisir pour le planning »**. Cela fixe le repère choisi dans le formulaire. Renseigner explicitement le **débit réel ou hypothétique** (gazole en L/min, H₂ en kg/min) et, si nécessaire, le **temps de manipulation** en minutes. Il n'existe **aucun débit préchargé** ni de garantie d'accès/horaires. Les stations répertoriées ne prouvent pas l'ouverture, la disponibilité ou la compatibilité autocar.
- Le temps d'attente **avant le plein** est **fixé à zéro**, conformément à la décision utilisateur. Le temps de remplissage est `quantité nécessaire pour remonter au plein / débit` ; les manipulations éventuellement saisies s'ajoutent. Pour l'électricité, le mode constant-débit n'est **pas** réutilisé comme une courbe de recharge.

## Sous-modèle de calcul livré

Pour chaque modèle **indépendamment** :

1. Tous les autocars démarrent à l'origine de la ligne avec une capacité énergétique utile pleine ; leur réserve est intouchable. Le nombre de courses orientées dépend du nombre de voyageurs et de la capacité de places. Les voyageurs sont affectés aux courses sans dépassement de capacité.
2. Une première course est effectuée directement (route déjà calculée par le fournisseur). Les véhicules terminent cette course **à destination**, jamais téléportés au départ.
3. Si une course supplémentaire existe, le planificateur **essaie d'abord de réutiliser** un véhicule. Pour retourner au départ, il emprunte un **trajet retour explicitement demandé au fournisseur** (aucune symétrie arbitraire). Si l'énergie restante ne permet pas retour + course suivante + réserve, il considère un détour via la station choisie : destination → station → origine, avec deux jambes **routées séparément** et niveau d'énergie contrôlé à chaque étape.
4. Si l'énergie permet d'atteindre la station, un plein est modélisé au maximum de capacité utile ; le temps de remplissage est calculé sur la **quantité réellement ajoutée**. Aucune attente en station. Le véhicule repart et peut réaliser la course suivante si l'énergie et la plage horaire le permettent.
5. Si le réemploi n'est pas trouvé et que le parc le permet, un nouveau véhicule (au départ, plein au début de la plage) est utilisé. **Le modèle est heuristique** : il ne garantit ni minimisation du nombre d'autocars, ni une solution quand elle existe. Si aucune affectation n'est trouvée, la sortie est **`no_solution_found` / « Non résolu »**, distincte d'une impossibilité démontrée. Une course qui dépasse à elle seule la capacité/réserve est un cas réellement incompatible avec ce sous-modèle.

Durées/distance : `service avec voyageurs`, `retour à vide`, `détour vers station`, `remplissage`, `manipulation` sont conservés comme événements horodatés dans les snapshots et résultats. `duration_wait_s` reste **0**. `duration_elapsed_s` est la durée entre le premier début et la dernière fin, tandis que `duration_vehicle_s` cumule les durées de chaque véhicule ; le roulage et l'immobilisation ne sont pas confondus. Les distances à vide, consommations associées, maintenance variable et émissions sont comptées avec les mêmes facteurs nationaux et limites TCO/CO₂e que les courses voyageurs. L'énergie achetée au plein n'est pas additionnée comme « consommée » une deuxième fois.

Traçabilité : les jambes de route supplémentaires sont calculées côté serveur **par le même fournisseur et profil** que le trajet initial, validées puis figées dans l'instantané. Aucune valeur de repli géographique n'est inventée en cas d'échec. L'API exige des tarifs/émissions présents dans les référentiels, sans injection de prix de station, et ne sauvegarde pas de secret fournisseur. La sélection de station est une donnée **déclarée par l'utilisateur, non vérifiée**.

## Limites incontournables avant usage opérationnel

- **Pas de vrai optimiseur certifié** : algorithme glouton mono-ligne, une seule journée, courses basées sur demande globale, une station sélectionnée, pas de dépôts, pas de mutualisation interlignes, pas de trajets de repositionnement autres que le retour et le détour modélisés.
- **Pas d'automatisme multi-stations ni d'optimisation des arrêts** (Q10, tâche 22 encore partielle). Aucun contrôle du gabarit réel des autocars, des heures d'ouverture, du débit annoncé, des conditions d'accès, de la congestion ni des pauses/règles chauffeur. La sélection d'une station n'en certifie pas l'utilisation ; aucune attente à la station n'est imputée.
- **Pas de recharge électrique** ni courbe de charge, ni gestion des batteries auxiliaires à l'arrêt ; pas de comparaison « ACV » complète. Les coûts de main-d'œuvre calculés sous le périmètre `complete` suivent les durées de roulage et de plein modélisées ; les autres immobilisations et règles sociales ne sont pas couvertes.
- Pas de retour dépôt à la fin de journée ni de livraison successive de passagers à un autre endroit que celui configuré. **La dernière course peut se terminer à destination.**
- Les fournisseurs de routage (Geoapify/ORS/OSRM démo) ne certifient pas tous les accès autobus. Des calculs approximatifs ne doivent jamais être présentés comme un planning d'exploitation vérifié.

## Test de référence synthétique

Un autocar 50 places, 80 voyageurs, 100 km par course à 2 h, un retour routé de 100 km/7 500 s, réservoir utile 50 L avec 5 L de réserve, 0,2 L/km, station sélectionnée avec détour de 10 km/600 s puis 90 km/6 500 s, pompe 30 L/min et 2 min de manipulation : le même autocar effectue 2 courses avec **un plein de 22 L (44 s)**, 100 km à vide, **60 L consommés** en roulant, et **0 s d'attente en station**. Ce résultat est une fixture d'essai, pas une donnée constructeur. Sans station et avec un parc de 2 autocars, les deux courses peuvent être en parallèle et le temps écoulé de la journée est distinct des heures-véhicules.

## Vérifications

- `tests/test_service_day.py` : énergie/réserve, passage station, séquencement, temps/distance, limites d'échelle, absence de station et absence de symétrie fictive.
- `tests/test_service_day_api.py` : isolation utilisateur, comparaison de deux solutions, provenance et empreintes des calculs, tarifs modifiés après coup et refus de coordonnées routières manquantes.
- `tests/browser_smoke.py` : tuiles jour, sélection de station depuis la carte, remplissage du débit, cas avec plein et retour dans le service, FR/EN et non-régression de l'interface.

Cette tranche **ne ferme pas** la tâche 22 complète : les trois politiques Q10, la compatibilité réelle des stations et les contraintes opérationnelles restent à développer.
