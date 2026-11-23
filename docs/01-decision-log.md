# 01 — Journal des décisions confirmées

**Verrouillé = réponse explicite de l’utilisateur.** Les modalités de mise en œuvre en aval ne sont pas automatiquement verrouillées.

| Q | Décision verrouillée | Conséquence |
|---|---|---|
| 01 | Optimisation automatique des rotations | La demande, les plages horaires et contraintes pilotent un moteur qui établit planning et flotte. |
| 02 | Trois niveaux de définition de demande | Volume global, volume par créneau et demande par départ précis. |
| 03 | Trois modes de réseau | Ligne seule, plusieurs lignes indépendantes, ou réseau avec mutualisation interlignes. |
| 04 | Trois modes de flotte | Comparaison individuelle, catalogue entier, composition optimisée de flotte mixte. |
| 05 | Objectif configurable | TCO, CO2e, nombre de véhicules, combinaison pondérée; contraintes dures séparées des objectifs. |
| 06 | Trois niveaux de contraintes temporelles | Rapide, détaillé et réglementaire, avec règles applicables à vérifier. |
| 07 | Trois approches de consommation | Fixe, ajustée selon contexte, et issue de tests terrain; multi-énergie et auxiliaires. |
| 08 | Trois périmètres carbone | Émissions directes, du puits à la roue, et ACV avec limites et sources explicitement indiquées. |
| 09 | Trois périmètres TCO | Variable exploitation; TCO véhicule; TCO exploitation complet avec coûts partagés. |
| 10 | Trois politiques de ravitaillement | Automatique nécessaire, stations imposées, optimisation des arrêts. |
| 11 | Trois niveaux de recharge électrique | Rapide, courbes/limites techniques, infrastructures partagées/congestion. |
| 12 | Trois modes de dépôts | Sans dépôt, un dépôt, plusieurs dépôts avec repositionnements. |
| 13 | Période personnalisée | Dates début/fin, état inter-journées; pas de multiplication d’une journée type. |
| 14 | Trois modes de fréquentation | Constante, profil calendaire, détail par date/ligne/créneau avec import. |
| 15 | Catalogue véhicules polyvalent | Saisie, import Excel/CSV et bibliothèque de modèles versionnés. |
| 16 | Catalogue stations polyvalent | Saisie, import Excel/CSV/GeoJSON et synchronisation externe contrôlée. |
| 17 | Onglet Énergies par pays | Tarifs unitaires nationaux et facteurs CO2e par énergie et périmètre, indépendants des stations. |
| 18 | Valeurs préremplies et éditables | Valeurs nationales sourcées, modifiables, avec année de référence et snapshot. |
| 19 | Prix nationaux uniquement | Une énergie a un prix national applicable partout dans le pays; pas de tarifs par station. |
| 20 | Trois vues des résultats | Tableau comparatif, fiches par solution, dashboard avec carte/graphiques/planning. |
| 21 | Rapport PDF | Exporter un rapport d’étude PDF; ni Excel des résultats ni partage demandé comme fonction dédiée. |
| 22 | Application web | Navigateurs desktop, backend calcul, base persistante, cartographie. |
| 23 | Multiutilisateur droits identiques | Comptes individuels, catalogues partagés, audit des modifications; pas de rôles métier. |

## Non décidé
- Q24 sur visibilité, propriété et organisation des simulations : **non répondu**.
- Technologie de frontend/backend, hébergeur, SLA, charge concurrente, stratégie de sécurité opérationnelle, exigences légales détaillées.
- Formules contractuelles précises TCO, règle d’allocation de coûts fixes, valeurs carbone ACV, incertitudes et réglementation chauffeur applicable.

## Discipline des modifications
Toute variation par rapport à une décision Q1–Q23 exige un enregistrement dans ce journal avec date, motif, approbation du demandeur et effet sur tests de non-régression.

## Notes techniques provisoires (20 novembre 2026 — non verrouillées)

La réalisation de la tranche verticale choisit temporairement FastAPI/SQLite, un moteur mono-ligne synchrone, des snapshots immuables et l’accès aux scénarios réservé au propriétaire. **Aucun de ces choix ne tranche Q24, ne modifie Q1–Q23, ni ne valide une architecture de production.** Détails, alternatives et limites : `docs/adr/0001-architecture-technique-provisoire.md`, `docs/adr/0002-registre-implementation.md`.

**Approbation métier :** non demandée / non obtenue à ce stade. **Impact testable :** le seul statut de solution positive fourni est `feasible_not_proven`, des modes multi-jours et ACV sont refusés explicitement, et aucun tarif national officiel n’est inventé.
