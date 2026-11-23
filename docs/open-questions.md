# Décisions ouvertes — ne pas inventer de réponse

| Priorité | Question | Hypothèse de travail possible, à marquer provisoire |
|---|---|---|
| Bloquant UX | Q24 : simulations visibles par tous, personnelles ou projets ? | Liste commune avec propriétaire identifiable, pas de partage granulaire, **provisoire** |
| Bloquant calcul | Définition d’une « rotation » : aller seul ou aller-retour ? | Segment orienté = course; une rotation est configurable et explicitée |
| Bloquant calcul | Demande globale sans horaires : horizon de service ou délai maximal acceptable ? | Répartir sur amplitude utilisateur explicitement saisie |
| Bloquant calcul | Service partiel admissible ? pénalité voyageurs non transportés ? | Exiger 100% servie, sinon `infeasible`; alternative configurable après arbitrage |
| Bloquant TCO | Clé ventilation fixes entre lignes mutualisées ? coût véhicule loué/disponible ? | Total sans double compte + clé heures d'utilisation, documentée |
| Important | ACV : portée exacte inclut-elle infrastructure et durée d'amortissement ? | ACV véhicule disponible seulement si données complètes; avertissement sinon |
| Important | Règles conducteurs : transport régulier/occasionnel, législation nationale/européenne, amplitude/pauses ? | Paramètres non réglementaires jusqu'à validation juridique |
| Important | Bornes / stations : nécessité des statuts temps réel, restrictions accès bus, réserve de charge ? | Référentiel statique horodaté, incertitude signalée |
| Important | Pays multiples au sein d’une route transfrontalière ? | Pays unique par scénario initial, parcours transfrontalier à cadrer |
| Important | Sources licences prix/facteurs/stations; dates de validité ? | Pipeline manuel curaté, provenance obligatoire |
| Important | Consommations multi-énergies simultanées (hybrides) : stratégie d'arbitrage ? | Modes d'usage saisis explicitement, pas d'optimisation chimie non spécifiée |
| Important | Nombre de sièges vs debout, accessibilité PMR, bagages et volume ? | Seats usable only tant que contraintes non définies |
| Exploitation | Hébergement, identité (SSO ?), nombre utilisateurs, rétention et sauvegardes ? | Web monolithe modulaire avec auth native temporaire |
| Exploitation | Budgets temps API ORS, restrictions de profiles bus, caching, politique fournisseur de secours ? | Un adaptateur ORS et fake, gestion erreur sans route fabriquée |
| UX | Maquettes/couleurs/branding et ordre exact des onglets ? | UX sobre à valider avant pixel polish |
| Tests | Jeu réel de référence Normandie et cas acceptés par métier ? | Cas synthétiques d'abord, validation terrain séparée |

Le développeur peut faire des choix techniques réversibles pour avancer mais doit conserver la liste ouverte, noter les hypothèses et demander validation avant de figer les choix métier qui modifient substantiellement les résultats.

## Arbitrages requis après le lot prototype (2026-11-20)

- **Q24 toujours ouverte.** Visibilité limitée au propriétaire **provisoirement** dans le code; cela ne constitue pas une réponse métier.
- Valider les sources nationales France/Normandie (tarifs, facteurs, licences, dates) avant d’activer le référentiel.
- Définir trajets retour, règles de rotation, dépôts et acceptabilité d’un service partiel avant les modules 20–24.
- Valider formules TCO (clés de partage/365 jours), périmètres ACV et législation opérateur avant modules 18, 19 et 25.
- Exiger un jeu métier de recette Normandie, profils bus compatibles, quotas ORS, et architecture de production.

Voir `reports/implementation-review.md` : aucune décision Q1–Q23 n’est modifiée.
