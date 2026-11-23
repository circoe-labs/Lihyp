# Haute-Normandie : annuaire des stations et futur calcul de ravitaillement

**Statut :** correctif de carte et de recherche livré en PR ; **le planificateur avec plein en journée n'est pas encore implémenté**. Les données stations sont indicatives et ne valent pas preuve de compatibilité autocar.

## Répertoire Haute-Normandie

- Dans **Stations en Normandie**, choisir **Haute-Normandie (Eure 27, Seine-Maritime 76)** (sélection initiale) ou **Toute la Normandie (5 départements)**.
- Sources diesel/essence : DGCCRF, jeu [Prix des carburants en France — Flux instantané v2](https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/), exploité en lecture via Opendatasoft API v2.1. Le serveur filtre les départements `27` et `76` avant de transmettre les points : l'inventaire est chargé automatiquement par pages de 100 jusqu'à 1 000 enregistrements, avec un bouton pour les éventuelles pages suivantes. Cache serveur : 15 minutes.
- Le jeu officiel donne l'adresse, la localisation, les carburants déclarés disponibles et des services éventuels (piste poids lourds, automate 24/24, relevé carburant). **Il ne certifie ni l'accessibilité des autocars, ni la disponibilité du carburant au moment d'une course.** Les données instantanées dépendent de la publication et de l'API ; aucune liste artificielle de points actifs n'est préchargée.
- Le survol d'un marqueur fait grandir le point et ouvre un encart détaillé. Le clic conserve la sélection ; un clic dans la liste recentre la carte et ouvre la fiche. La liste est exploitable même sans les tuiles OpenStreetMap.
- Conformément à la décision métier Q19, aucun tarif individuel de station n'est envoyé au navigateur : les coûts du logiciel utilisent des **prix nationaux par énergie**, distincts des emplacements de stations.
- Les repères H₂ sont issus d'un autre annuaire, non homologué ici pour les autocars ; ne pas utiliser les pressions/débits sans confirmation de l'exploitant.

## Contrat métier du planificateur futur (tâche 22, **non livré dans cette PR**)

Les réponses métier verrouillées Q10 imposent trois stratégies : **régler automatiquement un besoin de plein**, **restreindre aux stations imposées**, ou **optimiser les arrêts**. Le moteur doit calculer un emploi du temps **par véhicule**, avec continuité du lieu et de l'énergie pendant la journée ; il doit pouvoir relancer le véhicule après son ravitaillement. Le prototype actuel `BaselineEngine` refuse tout `refuel_mode != no_refuel` et ne simule pas les rotations, le trajet retour ou la réutilisation d'un véhicule.

Pour un ravitaillement, le plan doit déterminer :

1. Heure et lieu de fin de service précédant le plein, énergie restante et réserve minimale.
2. Station réellement **compatible** (type d'énergie, possibilité d'accès/autocar, horaires, pression/embout/débit, disponibilité et éventuelle capacité). Une station seulement **référencée** ne suffit pas pour prouver la faisabilité.
3. Trajet **à vide** vers cette station et son temps routier, consommation et émissions associés.
4. Approche/branchements, attente éventuelle en file, durée du remplissage calculée par quantité et débit (ou modèle de charge électrique avec courbe et limites) et durée de débranchement.
5. Trajet à vide de retour vers le point de reprise ; continuité des créneaux passagers et pauses réglementaires lorsqu'elles sont demandées et correctement paramétrées.
6. Après reprise : voyages voyageurs possibles, énergie à bord, horaires de fin de service, coût global et bilan CO₂e. Un plein ne saurait rendre magiquement faisable une course qui ne peut atteindre aucune station avec sa réserve.

**Durée du passage par la station :**

`temps_plein = trajet_vers_station + attente + accès/branchements + quantité_à_remplir / débit + sortie/débranchements + trajet_reprise`.

**Temps écoulé de la journée par véhicule :**

`heure_fin - heure_début`, soit temps de service voyageurs, trajet à vide, temps de plein et attente, pauses, embarquement, immobilisations **sans les compter deux fois**. Les durées cumulées de roulage des différents véhicules sont des **heures-véhicules** et ne s'additionnent pas pour représenter la fin de journée d'une flotte qui roule en parallèle.

**Énergie consommée :** distances en charge + déplacements à vide et auxiliaires selon le modèle retenu. **CO₂e** : cette consommation multipliée par le facteur correspondant au périmètre choisi (direct ou puits-roue ; ACV seulement si paramétré), sans additionner deux fois les émissions directes. **Coût** : énergie consommée et prix national, personnel/attente, maintenance/kilomètres additionnels et postes TCO activés ; n'utiliser aucun prix local de pompe. La quantité achetée et l'énergie effectivement consommée sont deux grandeurs distinctes, avec suivi de l'état initial/final du réservoir.

Les sorties attendues dans les tableaux et PDF sont : `trips`, `refuel_events`, itinéraires à vide, heure de départ/arrivée/reprise, distance voyageurs, distance à vide, temps roulant, temps d'attente, temps de plein, heures-véhicules, durée de journée, coût, énergie, CO₂e, faisabilité, diagnostics et références de provenance.

## Recette nécessaire avant d'annoncer le ravitaillement comme opérationnel

- Deux rotations avec un plein intermédiaire et reprise du service selon un planning faisable.
- Station incompatible, fermée, inaccessible ou sans carburant : arrêt rejeté avec diagnostic.
- Plein nécessaire mais aucune station accessible avant réserve : résultat non réalisable, jamais trajet fictif.
- Temps de détour, de file et de remplissage variable, avec modification observable du planning, du TCO et des émissions.
- Comparaison de véhicules à périmètres identiques et cohérence de l'énergie sur plusieurs jours ; limites réglementaires vérifiées à la source.
- Données de stations figées par date/source pour chaque simulation reproductible ; mise à jour ultérieure ne modifie pas les anciens résultats.

**Attention :** cette note est un contrat d'implémentation futur, pas une affirmation que les calculs ci-dessus sont opérationnels dans le moteur actuel.
