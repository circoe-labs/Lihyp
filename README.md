# Handoff d'implémentation — Simulateur transport voyageurs / TCO / CO₂e

**Statut :** spécifications métier issues de 23 décisions confirmées, avec hypothèses d'architecture **proposées et non validées**. **Langue :** français. **Territoire de départ :** Normandie (France), avec référentiel énergétique par pays.

## Pour l'agent repreneur
1. Ouvrir `tasks/TODO.md` et commencer par **tâche 00 Orchestrateur**.
2. Lire `docs/00-overview.md`, `docs/01-decision-log.md`, `docs/02-architecture-spec.md`, `docs/data-model.md`, `docs/optimization-contract.md`, `docs/open-questions.md`.
3. Avancer par petits incréments testés; documenter les hypothèses non tranchées; ne pas considérer les choix technologiques suggérés comme validés.
4. Maintenir le journal des décisions et un suivi des résultats de tests; ne pas présenter un solveur approximatif comme optimal garanti.

## Dossiers
- `grill-session.md` : restitution reconstruite des besoins et échanges.
- `docs/` : domaine, architecture, calculs, contrats, données, planning, QA, ambiguïtés, provenance.
- `tasks/TODO.md` : registre des tâches et règles d'orchestration.
- `tasks/NN-*/TASK.md` : une capacité par tranche de travail.
- `templates/` : modèles de tâche et de compte-rendu.

## Cible métier
Simuler une demande voyageurs sur une ou plusieurs lignes, dimensionner et planifier une flotte homogène ou mixte, intégrer les kilomètres à vide, dépôts, pauses, énergie, ravitaillements et infrastructure; comparer faisabilité, coût total de possession et CO₂e à périmètre identique; éditer un rapport PDF audit-able.

## Limites immédiates
La question 24 (visibilité et rangement des simulations entre utilisateurs) est **non répondue**. L'absence de réponse n'autorise pas à retenir implicitement une organisation par projets. Les sources de données stations et les chiffres d'énergie ne sont **pas vérifiés** dans ce handoff et doivent être importés/sourcés avant usage réel.

## Lot applicatif ajouté (2026-11-20)

Un prototype local **exécutable mais non homologué** a été ajouté à ce paquet de transfert. Démarrage : `IMPLEMENTATION.md`; état de la recette, tâches acceptées et ouvertes : `reports/implementation-review.md`. Tous les critères du produit final ne sont **pas** livrés.

## Nouvelle interface (23/11/2026)

Navigation directe vers Simulations après connexion, estimation de trajet
demandée à un fournisseur de routage, carte départ/arrivée, annuaire H₂ et
stations-service de Normandie, commutateur **FR/EN**, PDF dans la simulation.
Tout ceci reste un prototype non déployé en public et sans données nationales
de prix ou d'émissions vérifiées. Lire `IMPLEMENTATION.md` et
`docs/ux-routing-i18n-stations.md` avant utilisation.


## Comparer des véhicules et configurer le routage (PR #2)

La page **Simulations** permet désormais de comparer **2 à 8 véhicules** sur un
même itinéraire, avec coûts, CO₂e, faisabilité et PDF par solution, sans
optimisation de flotte mixte. L'onglet **Paramètres > API de routage** expose
Geoapify (profil `bus` par défaut), les options `truck`/`heavy_truck`, ORS et
le routage OSRM de démonstration. Seul l'exploitant connecté localement peut
saisir/supprimer des clés dans l'interface ; en production, utiliser un
système de secrets côté serveur. Lire `docs/multivehicule-et-api-routage.md`.

## Refonte Stations et Énergies (PR distincte)

Stations en Normandie : filtres H₂/essence/gazole, carte + liste synchronisées et fiches détaillées au survol/clic. Énergies par pays : tableau de consultation, ajout et modification dans un panneau distinct, retrait réversible sans effacement des simulations historiques. Les données de stations ne sont pas certifiées et **aucun prix national fictif n'est ajouté**. Voir `docs/stations-et-energies-ux.md`.

## Annuaire Haute-Normandie et futur ravitaillement

La page **Stations en Normandie** propose désormais le secteur **Haute-Normandie (Eure 27 et Seine-Maritime 76)**, en plus de toute la région, avec chargement des stations essence/gazole depuis le flux officiel DGCCRF. Au survol d'un point, sa taille augmente et une fiche de renseignements apparaît ; le clic conserve la sélection. Les données restent indicatives, notamment pour l'accès autocar.

La possibilité d'effectuer un plein pendant la journée puis de reprendre les rotations figure dans les décisions métier **Q10 et tâche 22**, **mais le moteur actuel ne la calcule pas encore**. Le détail des temps, détours, files, coûts, émissions et tests attendus est décrit dans `docs/haute-normandie-et-ravitaillement.md`.

## Comparaison avec chronologie journalière (prototype PR #4)

La comparaison dispose de **tuiles par véhicule** avec les heures de courses et, sur option, le retour à vide et le plein dans la journée (**attente station = 0**). Les distances/durées de détour sont demandées au serveur de routage ; l’utilisateur doit choisir une station et saisir un débit de remplissage, sans valeur inventée. Le calcul est heuristique et limité à une ligne et une journée ; la tâche 22 reste ouverte pour l’optimisation, les contraintes réelles et les modes multi-stations. Lire `docs/rotations-pleins-tuiles-journalieres.md`.

## Stations automatiques et rotations (lot de comparaison 24/11/2026)

Le calcul journalier peut proposer un ravitaillement compatible de manière
**automatique**, sans exiger de station choisie sur la carte. Les tuiles affichent
les rotations et les pleins par véhicule ; une station H₂ ne peut pas servir un
véhicule gazole. Une valeur illustrative de 30 L/min est proposée pour le gazole
(et reste à vérifier), aucun temps d'attente en station n'est ajouté. Cette
présélection est bornée et **ne prouve pas un optimum global**. Consulter
`docs/optimisation-stations-rotations-comparaison.md` pour les critères, limites
et recette. Le logiciel demeure un prototype local, non prêt pour un service public.

## Bibliothèque indicative de véhicules (24/11/2026)

Dans **Véhicules**, 9 références issues du tableau fourni par l'utilisateur sont présentées avec leurs fourchettes HT et un comparatif partiel énergie + maintenance pour 100 km. Les véhicules doivent être **complétés et enregistrés explicitement** avant les simulations. BioGNV (kg) est pris en charge comme énergie, sans prix ni facteur CO₂e inventé. Voir `docs/catalogue-utilisateur-neuf-autocars.md`.
