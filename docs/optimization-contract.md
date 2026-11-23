# Contrat de calcul et d'optimisation

## Entrées
Période début/fin et fuseau; liaisons orientées (option retour), demandes agrégées/créneaux/départs; options de mutualisation; véhicules autorisés/capacités/réservoirs/consommations/coûts; dépôts/retour éventuel; stations équipées/horaires; tarifs et facteurs nationaux versionnés; contraintes de temps/charge; objectifs et pondérations; délai max solveur.

## Fonction objective
Modes exclusifs : minimiser coût EUR, kgCO₂e ou nombre de véhicules; mode multicritère avec normalisation transparente par critères de référence et poids explicites, pas simple somme EUR+kg sans mise à l'échelle. Conserver valeurs individuelles de tous les critères. Optimisation sur coût complet ou partiel selon sélection TCO; respect obligatoire des contraintes dures.

## Faisabilité
Respecter capacité voyageurs, demande servie (ou signaler explicitement non servie si tolérance configurée), créneaux de départ/arrivée, durée de roulage et embarquement, compatibilité route/véhicule, affectation sans chevauchement, trajets à vide, temps de conduite et pause lorsqu'option réglementaire active et norme validée, énergie utilisable/réserve/consommation auxiliaire, compatibilité stations, temps de détour/attente/recharge, plage d'ouverture, position et SoC continus jour à jour. Un réseau mutualisé ne permet aucune téléportation d'un véhicule entre deux lignes.

## Modèles énergétiques
- Combustion fixe : `quantity = (km_passenger + km_empty)*unit_per_km + hours*unit_per_h` (éviter double-compte, vérifier unités).
- Profil contextuel : coefficient par vitesse/masse/température/pente, clairement signalé comme estimation et calibré.
- Mesuré : interpolation/extrapolation limitée avec avertissement.
- Électrique : `energy_to_battery = effective_power_integral dt`, puissance limitée par borne, véhicule, SoC et puissance partagée; rendement explicite; charge 10→80% non supposée linéaire si courbe fournie.
- Gaz/H₂/liquides : débit, volume/masse utile, temps fixe de branchement et remplissage. Ne pas confondre kg, Nm³, L et kWh.

## Calcul TCO
Variables distance (énergie, maintenance au km, péages) + variables temps (personnel et immobilisation selon périmètre) + fixes proratisés sur période (amortissement/loyer, assurance, infrastructures). Définir la règle de prorata et éviter allocations multiples lorsque les lignes partagent un véhicule : addition des coûts élémentaires sur l'exploitation puis ventilation à chaque ligne selon une clé explicitée (par ex. heures attribuables; à arbitrer). Indicateurs au minimum `EUR_total`, `EUR/vehicle`, `EUR/route`, `EUR/km`, `EUR/passenger`, avec dénominateurs clairement définis.

## Calcul CO₂e
Direct = émissions d’usage selon facteurs adaptés au carburant; du puits à la roue = amont+usage; ACV = énergie + fabrication/entretien/fin de vie du véhicule et infrastructures **si inclus et quantifiés**, amortie sur unité fonctionnelle explicitée. Ne pas ajouter les facteurs puits-roue au direct si ils incluent déjà ce dernier. Indicateurs `kgCO₂e_total`, `kgCO₂e/km`, `kgCO₂e/passenger`, `gCO₂e/passenger-km`; affichage du périmètre et source. Comparer un périmètre commun ou marquer non comparable.

## Résultat structuré
`status`, `objective`, `optimality_gap?`, `lower_bound?`, `runtime_ms`, `constraint_violations[]`, `unserved_demand[]`, `vehicles[]`, `trips[]`, `refuel_events[]`, `time_breakdown`, `distance_breakdown`, `cost_breakdown`, `co2e_breakdown`, `data_quality_warnings[]`, `provenance`, `input_snapshot_hash`.

## Test chiffré de référence — synthétique
Un trajet de 100 km, bus 50 places, 80 voyageurs, mono-sens, aucun retour exigé, 20 L/100km, diesel hypothétique 2 EUR/L, 2.7 kgCO₂e/L (valeurs **illustratives uniquement**, non nationales). Deux départs nécessaires si pas de limite horaire, consommation 40 L, coût énergie 80 EUR, facteur direct hypothétique 108 kgCO₂e. Ce cas exclut repositionnements et frais fixes **exprès** et sert à tester le calcul de base; dès ajout d’une obligation retour, la distance et les résultats doivent augmenter.

## Statuts de solveur
`optimal`, `feasible_not_proven`, `infeasible_proven`, `timeout_with_incumbent`, `timeout_no_solution`, `invalid_input`, `provider_error`. Ne jamais remplacer « délai dépassé » par « impossible ».
