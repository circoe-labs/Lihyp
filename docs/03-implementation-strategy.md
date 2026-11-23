# 03 — Stratégie d'implémentation

## Principe
Livrer un **vertical slice calculable et testable** avant d'empiler les niveaux avancés de fidélité. Tout mode choisi par l'utilisateur est cible produit mais ne doit pas être présenté comme fini avant tests. Éviter l'effet « 3 options × tous modules » implémenté superficiellement.

## Jalons
**J0 — cadrage** : architecture/contrats, questions bloquantes consignées; codebase, CI, fixtures.
**J1 — référentiels** : auth basique, pays/énergies, véhicules, stations, imports, historique. Chaque CRUD testé indépendamment.
**J2 — routes + baseline** : ORS et fake routage; scénario simplifié; trajet sur carte; calculs énergie/TCO/CO₂e; planification simple; résultats immuables.
**J3 — exploitation réaliste** : demande par créneau/départ, calendriers multi-jours, dépôts, repositionnement, recharge/refuel, temps opérationnels, matrices.
**J4 — optimisation** : variantes homogènes, catalogue, flotte mixte, réseau mutualisé, multicritères, quotas/timeout et diagnostic de faisabilité.
**J5 — restituabilité** : résultats table/fiches/dashboard, carte, planning, PDF, preuve de cohérence.
**J6 — sophistication** : profils de conso contextuels/essais, courbes de recharge/ports partagés, réglementation vérifiée, ACV conditionnelle, hardening production.

## Dépendances
Ne pas coder les algorithmes avant d'avoir des unités sûres, des tests déterministes et une définition du statut de résolution. Toute entrée venant d'API routage/énergie doit pouvoir être remplacée par un stub offline. Garder les snapshots immuables et calculs indépendants de l'état courant des catalogues.

## Conditions de passage
- J2 : scénario mono-ligne, un carburant, 1 jour, coût/émissions et itinéraire vérifiés par fixture.
- J3 : simulation 3 jours avec bilan énergie et réaffectation continue; aucune collision temporelle.
- J4 : mélange de variantes, gap/timeout, aucun trajet impossible déclaré faisable.
- J5 : PDF reprenant exactement les chiffres du snapshot; provenance visible.
- J6 : tests frontières réglementaires, infrastructures et performances; sauvegarde/restauration confirmées.

## Décisions réservées
Q24, gestion d'une demande impossible (refus entier ou service partiel), règles d'allocation fixe, origine et licence des jeux de données, contraintes réglementaires exactes et hébergement restent arbitrables; documenter choix provisoires.
