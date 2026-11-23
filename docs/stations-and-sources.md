# Stations initiales Normandie / sources

## Stratégie de constitution
Créer un catalogue initial depuis données publiques géolocalisées, avec validation de licence, date d'accès et champs. Données de recharge IRVE françaises (data.gouv.fr), réseaux GNV, hydrogène et annuaires d'exploitants; les droits de republication, formats, mise à jour, complétude et compatibilités bus doivent être vérifiés. OpenRouteService sert au calcul de routes, **pas** de source fiable universelle de stations.

## Exemples de candidats évoqués durant le cadrage — NON VALIDÉS
- Évreux/Le Vieil-Évreux : infrastructure hydrogène du réseau EAS-HyMob à confirmer (statut réel, pression, accès, quantité).
- Sotteville-lès-Rouen : station GNV à confirmer (accès et débit) ; éventuelle recharge électrique à vérifier.
- Mondeville, Giberville et Bretteville-sur-Odon : infrastructures de recharge à identifier par opérateur, prise, puissance, accès véhicules lourds, disponibilité.

**Ne pas transformer ces mentions en enregistrements « actifs » sans vérification terrain/documentaire.** Couverture diesel, GPL, gaz, H₂ et électrique à établir. L'infrastructure peut être implantée hors trajet, d'où nécessité du détour calculé par routage.

## Champs import essentiels
`source_id`, `station_name`, coordonnées WGS84, `energy_code`, connecteur/pression, puissance ou débit, nombre de points de distribution, horaires, accès public/privé, gabarit accessible, statut, origine, `observed_at`, `last_verified_at`, `confidence`, provenance/licence. **Pas de prix par station** (Q19).

## Facteurs et prix
Les valeurs nationales doivent être sourcées et associées au millésime (ADEME/Base Empreinte pour la France lorsqu'applicable). Le facteur « direct » électrique peut être nul à l'échappement mais le facteur amont et ACV dépendent du mix et de la définition; H₂ dépend du mode de production. Ne pas utiliser de facteur international générique sans identifier le pays et le périmètre.
