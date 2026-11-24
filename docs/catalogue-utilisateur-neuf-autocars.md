# Bibliothèque de neuf autocars — tableau utilisateur

**Références indicatives non vérifiées.** Source : tableau communiqué le 24 novembre 2026. Les fourchettes d'achat, d'énergie, de coût énergétique / 100 km et de maintenance préventive sont conservées en HT ; aucune fiche constructeur n'est certifiée.

## Périmètre

- Neuf fiches : deux diesel, deux BioGNV, trois électriques et deux hydrogène, visibles sous **Véhicules**.
- Un comparatif partiel **énergie + maintenance préventive pour 100 km** utilise uniquement les bornes présentes dans le tableau : énergie/100 km + 100 × maintenance/km.
- **Ce comparatif n'est pas un TCO** : amortissement, salaires, assurance et autres coûts sont exclus. Il n'est pas une simulation et ne calcule pas les émissions.
- Les neuf références intègrent aussi les **valeurs techniques du second tableau utilisateur du 24/11/2026** : places utiles, consommation/km et /h, capacités utiles, réserves et sources déclarées. Ces éléments restent **non vérifiés**, même lorsqu'une fiche constructeur est citée. Le bouton **Ajouter au catalogue** enregistre une référence sur action explicite ; **Vérifier / modifier** ouvre le formulaire prérempli. Aucune création automatique de tarif national ni de facteur CO₂e.
- Le montant H₂ **rétrofit** est le **prix du kit + pose**, pas l'acquisition d'un autocar neuf : ce champ reste volontairement vide.
- Le code énergétique **BIOGNV (kg)** est désormais disponible. Prix national et facteurs d'émission doivent être explicitement sourcés dans Énergies par pays : les fourchettes du tableau ne les remplacent pas.

## Pour comparer

Configurer un tarif national et des facteurs CO₂e par énergie, puis utiliser **Ajouter au catalogue**. Les neuf véhicules deviennent sélectionnables dans Simulations après configuration de leur énergie. Les snapshots historiques et les autres véhicules ne sont pas modifiés.

**Limite du planificateur :** le ravitaillement automatique BioGNV et la recharge électrique restent non disponibles. Les véhicules concernés peuvent être comparés sans arrêt quand leur autonomie suffit ; aucune station ou quantité d'énergie n'est inventée.

Le JSON de référence est `src/simco2/ui/vehicle-reference-catalog.json`. La dépendance Python `tzdata` est également ajoutée sur Windows pour reconnaître `Europe/Paris`.

## Précautions sur les données techniques et les coûts

Les capacités utiles, indications brutes et pressions sont reprises sans conversion ni validation indépendante. Pour le rétrofit H₂, les 380–430 k€ correspondent au kit et à la pose, non au prix d'un autocar complet ; le prix du véhicule n'est pas connu et l'ajout rapide utilise `purchase_eur=0` comme valeur technique manquante, **pas comme coût réel**. Les postes salaire, assurance, valeur résiduelle et durée de vie constructeur ne sont pas fournis : les valeurs par défaut du logiciel ne doivent pas être considérées comme vérifiées. La recharge électrique et le ravitaillement automatique BioGNV restent limités dans le moteur de planification.
