# Navigation et parcours UI — proposition fonctionnelle

## Navigation principale
`Simulations`, `Véhicules`, `Énergies`, `Stations`, `Cartographie / API`, `Résultats` (la restitution peut aussi être sous-page de simulation), `Compte`. Onglets à valider avec utilisateur; aucun visuel final approuvé.

## Parcours principal
1. Créer une simulation; nom, période, pays, objectifs.
2. Définir lignes sur carte (A/B, sens, arrêts), services passagers (global, plages, horaires précis), calendrier.
3. Choisir politique flotte (un modèle / tous / mixte), politique réseau (seul/isolées/mutualisées), dépôts et stationnements.
4. Choisir niveau temporel, profil de consommation, émissions, TCO, ravitaillement/recharge, contraintes.
5. Prévisualiser routes, vérifier données manquantes et coûts API; lancer simulation avec job/progression.
6. Lire statut, résultats tableau, fiches détaillées, carte, planning, diagnostics et matrice de comparaison.
7. Générer PDF avec mêmes résultats gelés.

## Table résultats — colonnes minimales
`solution`, `faisabilité`, `type et nombre véhicules`, `passagers servis/non servis`, `taux de remplissage`, `km en charge`, `km à vide`, `heures roulage`, `heures attente`, `heures recharge`, `kWh/L/kg`, `TCO EUR`, `EUR/passager`, `kgCO₂e`, `gCO₂e/passager-km`, `nb ravitaillements`, `objectif/rang`, `données manquantes`.

## Accessibilité
Clavier, contrastes, unités et info-bulles (CO₂e / ACV / TCO), couleurs non uniques pour signaler faisabilité, affichage mobiles en lecture simple; priorité écran large.
