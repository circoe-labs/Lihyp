# Session reconstruite

> This is a reconstructed grill session based on available conversation context. Elle restitue les décisions et principaux échanges sans prétendre être une transcription verbatim.

## Brief initial
Le demandeur souhaite un logiciel métier web de simulation de lignes de transport de voyageurs (bus, minibus/camionnettes, voitures), comparant moteurs diesel, GPL, gaz, électrique, hydrogène et autres énergies. Un catalogue véhicules contient caractéristiques, consommations au kilomètre, à l’heure, et/ou kWh, essais, coûts, capacités et réservoirs. Un paramétrage API de routage, une interface de simulation d’origines/destinations, volumes voyageurs et rotations, un moteur de calcul d’itinéraires et de faisabilité et une base géolocalisée de stations sont attendus. Il faut gérer ravitaillement, trajets à vide, plannings, TCO et CO₂e. Le projet pilote porte sur la Normandie.

## Réponses QCM explicites
- **Q01:** Optimisation automatique des rotations. **Réponse :** La demande, les plages horaires et contraintes pilotent un moteur qui établit planning et flotte.
- **Q02:** Trois niveaux de définition de demande. **Réponse :** Volume global, volume par créneau et demande par départ précis.
- **Q03:** Trois modes de réseau. **Réponse :** Ligne seule, plusieurs lignes indépendantes, ou réseau avec mutualisation interlignes.
- **Q04:** Trois modes de flotte. **Réponse :** Comparaison individuelle, catalogue entier, composition optimisée de flotte mixte.
- **Q05:** Objectif configurable. **Réponse :** TCO, CO2e, nombre de véhicules, combinaison pondérée; contraintes dures séparées des objectifs.
- **Q06:** Trois niveaux de contraintes temporelles. **Réponse :** Rapide, détaillé et réglementaire, avec règles applicables à vérifier.
- **Q07:** Trois approches de consommation. **Réponse :** Fixe, ajustée selon contexte, et issue de tests terrain; multi-énergie et auxiliaires.
- **Q08:** Trois périmètres carbone. **Réponse :** Émissions directes, du puits à la roue, et ACV avec limites et sources explicitement indiquées.
- **Q09:** Trois périmètres TCO. **Réponse :** Variable exploitation; TCO véhicule; TCO exploitation complet avec coûts partagés.
- **Q10:** Trois politiques de ravitaillement. **Réponse :** Automatique nécessaire, stations imposées, optimisation des arrêts.
- **Q11:** Trois niveaux de recharge électrique. **Réponse :** Rapide, courbes/limites techniques, infrastructures partagées/congestion.
- **Q12:** Trois modes de dépôts. **Réponse :** Sans dépôt, un dépôt, plusieurs dépôts avec repositionnements.
- **Q13:** Période personnalisée. **Réponse :** Dates début/fin, état inter-journées; pas de multiplication d’une journée type.
- **Q14:** Trois modes de fréquentation. **Réponse :** Constante, profil calendaire, détail par date/ligne/créneau avec import.
- **Q15:** Catalogue véhicules polyvalent. **Réponse :** Saisie, import Excel/CSV et bibliothèque de modèles versionnés.
- **Q16:** Catalogue stations polyvalent. **Réponse :** Saisie, import Excel/CSV/GeoJSON et synchronisation externe contrôlée.
- **Q17:** Onglet Énergies par pays. **Réponse :** Tarifs unitaires nationaux et facteurs CO2e par énergie et périmètre, indépendants des stations.
- **Q18:** Valeurs préremplies et éditables. **Réponse :** Valeurs nationales sourcées, modifiables, avec année de référence et snapshot.
- **Q19:** Prix nationaux uniquement. **Réponse :** Une énergie a un prix national applicable partout dans le pays; pas de tarifs par station.
- **Q20:** Trois vues des résultats. **Réponse :** Tableau comparatif, fiches par solution, dashboard avec carte/graphiques/planning.
- **Q21:** Rapport PDF. **Réponse :** Exporter un rapport d’étude PDF; ni Excel des résultats ni partage demandé comme fonction dédiée.
- **Q22:** Application web. **Réponse :** Navigateurs desktop, backend calcul, base persistante, cartographie.
- **Q23:** Multiutilisateur droits identiques. **Réponse :** Comptes individuels, catalogues partagés, audit des modifications; pas de rôles métier.

## Correction explicite de l’utilisateur
À la question initiale sur les prix de l’énergie, le demandeur a demandé un **onglet Énergies par pays** où chaque énergie possède un coût et des facteurs d'émission. Au Q18, il a choisi des **références préremplies et modifiables**, et au Q19 les **prix nationaux uniquement**. Ne pas implémenter par défaut de variation de prix entre stations.

## Dernière question non répondue
Q24 : organisation des simulations entre utilisateurs (personnelles, communes, par projets ou hybrides). L’utilisateur a interrompu le questionnaire pour demander le handoff. Ne présumer aucune réponse.

## Artefact demandé
Un dossier de transmission complet et plan de tâches pour agent développeur. Aucun code existant ni maquettes approuvées n’ont été fournis.
