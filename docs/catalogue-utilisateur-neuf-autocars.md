# Bibliothèque de neuf autocars — tableau utilisateur

**Références indicatives non vérifiées.** Source : tableau communiqué le 24 novembre 2026. Les fourchettes d'achat, d'énergie, de coût énergétique / 100 km et de maintenance préventive sont conservées en HT ; aucune fiche constructeur n'est certifiée.

## Périmètre

- Neuf fiches : deux diesel, deux BioGNV, trois électriques et deux hydrogène, visibles sous **Véhicules**.
- Un comparatif partiel **énergie + maintenance préventive pour 100 km** utilise uniquement les bornes présentes dans le tableau : énergie/100 km + 100 × maintenance/km.
- **Ce comparatif n'est pas un TCO** : amortissement, salaires, assurance et autres coûts sont exclus. Il n'est pas une simulation et ne calcule pas les émissions.
- Cliquer sur **Compléter cette fiche** préremplit uniquement les noms, l'énergie, la provenance et des médianes **modifiables** pour l'acquisition (sauf rétrofit) et la maintenance. Les places, la consommation/km et la capacité utile ne figurant pas dans le tableau, elles restent à renseigner et valider. Aucun véhicule n'est enregistré automatiquement.
- Le montant H₂ **rétrofit** est le **prix du kit + pose**, pas l'acquisition d'un autocar neuf : ce champ reste volontairement vide.
- Le code énergétique **BIOGNV (kg)** est désormais disponible. Prix national et facteurs d'émission doivent être explicitement sourcés dans Énergies par pays : les fourchettes du tableau ne les remplacent pas.

## Pour comparer

Enregistrer un tarif national et ses facteurs CO₂e par énergie, vérifier et renseigner les spécifications techniques manquantes, puis enregistrer les véhicules. Les snapshots historiques et les autres véhicules ne sont pas modifiés.

**Limite du planificateur :** le ravitaillement automatique BioGNV et la recharge électrique restent non disponibles. Les véhicules concernés peuvent être comparés sans arrêt quand leur autonomie suffit ; aucune station ou quantité d'énergie n'est inventée.

Le JSON de référence est `src/simco2/ui/vehicle-reference-catalog.json`. La dépendance Python `tzdata` est également ajoutée sur Windows pour reconnaître `Europe/Paris`.
