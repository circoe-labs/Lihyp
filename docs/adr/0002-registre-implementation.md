# ADR-0002 — Registre d'exécution / périmètre courant

**Date : 2026-11-20.** Le paquet initial ne contient aucun code source, seulement
les documents de transfert. Aucune donnée de station, prix ou facteur national
n'a été vérifiée pendant cette implémentation.

## Équipes de revue logiques

- Architecture & contrats : ADR, sécurité de frontières, types et politique de versions.
- Calcul & ordonnancement : invariants énergie, capacité, coût, CO2e et faisabilité.
- API & persistance : transactions, historique, audit, secrets, snapshots.
- Produit & restitution : libellés d'hypothèses et conformité des résultats/PDF.
- QA indépendante : tests négatifs, régression, limites et vérification documentaire.

Il s'agit de **passes de travail et de revue**, pas d'exécutions par des sous-agents
indépendants ; aucun outil de délégation de sous-agents n'est disponible ici.

## Séquence

1. Stabiliser contrats transverses et démarrage (00-03).
2. Protéger les catalogues, saisir les données sourcées et versions (04-09).
3. Réaliser un calcul de référence sur snapshot gelé (14-20), sans prétendre
   avoir accompli les modules avancés 21-25.
4. Brancher API de résultats et un PDF de prototype, distincts des critères
   finaux de 26-29.
5. Revoir les écarts avec `tests/`, `reports/` et `tasks/TODO.md`.

Les fonctionnalités non terminées sont conservées ouvertes, même lorsqu'un
prototype partiel démontre un sous-composant.
