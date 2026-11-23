# 00 — Produit et périmètre

## Vision
Outil d'aide à la décision de transport de voyageurs : **demande → réseau géographique → ressources → optimisation contrainte → résultats comparables → PDF**.

## Personae / cas d'utilisation
Analyste : définit un scénario, les dates, trajets/arrêts, passagers, horaires, objectifs et contraintes. Gestionnaire de données : crée et versionne véhicules, stations et facteurs nationaux. Collaborateur : exploite résultats et génère rapport. **Tous ont les mêmes droits métier** (Q23).

## Modules fonctionnels
1. **Véhicules :** modèle, variantes motorisations, capacité utile, dimensions et limites de circulation, réservoir/batterie, courbe de charge, coûts, consommation (distance, temps, auxiliaires), essais/fiabilité/sources, version.
2. **Cartographie / API :** clé et état API de routage, adresses et coordonnées, directions, distances, durées, géométries, contraintes et cache reproductible.
3. **Énergies par pays :** listes de carburants/électricité/H₂, unités, prix nationaux, facteurs directs/puits-roue/ACV pertinents, source/date/version; données préremplies éditables.
4. **Stations :** bornes/prises, carburants, capacité, pression H₂, puissance/raccords, horaires, accès public/privé, compatibilité, statut, source, date, import manuel/fichier/externe. Aucun tarif station (Q19).
5. **Scénarios / simulations :** période personnalisée, demandes globale/calendaire/horodatée, ligne seule/réseau indépendant/réseau mutualisé, comparaisons mono/catalogue/mixte, dépôts 0/1/N, trois profondeurs d'exploitation, objectif configurable, trois ravitaillements et trois niveaux de recharge.
6. **Résultats et PDF :** validation/faisabilité, comparaison, fiches, dashboard + carte + planning; rapport PDF avec hypothèses, calculs, source, avertissements.
7. **Utilisateurs :** login individuel, droits métier égaux, accès audité; partage/visibilité des simulations à arbitrer (Q24).

## Frontières fonctionnelles
- Les déplacements à vide, détour à la station, pause, embarquement, attente et retour dépôt comptent dans temps, énergie, coûts, CO₂e.
- La flotte ne peut pas transporter plus de personnes que ses places réellement disponibles; les horaires contraignent l'affectation.
- `Impossible` et `non résolu` sont différents; le moteur expose les explications.
- Les calculs doivent distinguer hypothèse, donnée mesurée, source nationale, estimation et absence de donnée.
- Le produit compare **CO₂e**, pas uniquement CO₂ à l'échappement; préciser périmètre ACV et frontières de système.

## Hors périmètre confirmé pour v1
- Export XLSX des résultats et collaboration/partage dédié : non choisis à Q21; l'**import véhicules et stations Excel/CSV reste requis**.
- Prix différenciés des stations, tarification temps réel, moteur de réservation de borne, vente de billets, paiement et suivi GPS live : non demandés.
- Garantie d'optimalité pour toutes tailles de réseaux : non promise.

## Exemple métier minimal
2 lignes Caen ↔ Rouen et Caen ↔ Le Havre; une période de 3 jours; profil voyageurs par jour, deux modèles (bus électrique et diesel), dépôt Caen, stations compatibles, contraintes de créneaux. Résultats : flotte, courses, enchaînements, recharges, coûts et CO₂e; scénarios indépendants puis mutualisés; même périmètre de calcul dans la comparaison.
