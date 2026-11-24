# Lot : choix automatique des stations, rotations et comparaison réactive

**Statut : prototype mono-ligne / une journée, sans preuve d'optimalité globale.**

## Comportement utilisateur

- Deux véhicules (ou plus, jusqu'à huit) et leur énergie nationale configurée sont requis pour une comparaison. Si les catalogues, le trajet, la saisie ou la session du devis de routage sont insuffisants, l'erreur apparaît **sous le bouton Comparer**, avec un message exploitable. Le bouton ne doit jamais échouer silencieusement.
- La case **Planifier les rotations et les pleins de la journée** est activée par défaut ; plage de service illustrative `08:00–18:00`, réglable dans les options avancées. Pour une comparaison simple sans rotation, décocher cette case.
- Le mode de ravitaillement initial est **Automatique** : pas besoin de sélectionner une station sur la carte. Les modes **Station imposée** et **Sans ravitaillement** restent accessibles pour les analyses avancées.
- Une station H₂ choisie pour des modèles exclusivement gazole est rejetée explicitement, y compris par l'API ; aucun plein incompatible n'est simulé. Si l'utilisateur demande expressément « automatique », une ancienne sélection manuelle n'est pas imposée par accident.
- Le débit diesel initial `30 L/min` est **une hypothèse de démonstration non vérifiée, à modifier**. Le débit H₂ initial est `0 kg/min` (donc aucun plein H₂ calculable sans hypothèse explicite). Temps d'attente à la station : **toujours 0 minute** ; le temps de manipulation est configurable.

## Recherche de station et contrôle physique

1. Le trajet de voyageurs est reçu d'un devis de routage serveur **lié à l'utilisateur**, avec sa provenance ; son retour inverse est demandé au fournisseur (aucune distance miroir inventée).
2. Si une solution a besoin de plusieurs courses et qu'un débit positif existe pour son carburant, le serveur charge des candidats depuis le répertoire H₂ source et/ou le flux DGCCRF existant. Pour le gazole, seulement **trois pages de 100** sont inspectées au maximum. Si la source est indisponible, aucun enregistrement fictif n'est ajouté.
3. Les stations doivent annoncer une énergie **compatible**. Les coordonnées servent seulement à présélectionner au maximum **quatre stations** par énergie et trajet, puis le fournisseur calcule **séparément** le détour destination → station et station → origine. Un itinéraire de station non calculable est écarté.
4. Pour chaque autocar réutilisé, le moteur essaie d'abord un retour à vide direct **sans plein** lorsque l'énergie suffit, puis les stations routées si un plein est nécessaire. Il vérifie énergie restante avant la station, réserve, capacité au départ de station, durée de détour, durée de remplissage, manipulation, et achèvement de la course suivante avant la fin du service.
5. La station choisie dans le résultat est celle produisant **l'arrivée la plus tôt** parmi les candidats admissibles du modèle. La réutilisation d'un autocar existant est privilégiée ; ce mode heuristique **ne minimise pas de manière prouvée le TCO ni le nombre de véhicules**. La comparaison affiche séparément les coûts et CO₂e des solutions homogènes faisables et signale le coût le plus faible parmi les seuls cas calculés.
6. Chaque exécution fige dans son snapshot les trajets routés, stations candidates, station utilisée, débits, période, énergie et modèle. Les résultats historiques et leurs empreintes SHA-256 restent immuables.

## Résultats attendus

- Le tableau affiche la faisabilité, les véhicules mobilisés, les coûts, l'énergie et les émissions, puis des **tuiles par solution** avec le total de courses réalisées.
- Dans chaque tuile, un déroulement par véhicule détaille **course avec voyageurs**, **trajet à vide**, **détour vers station**, **plein**, **manipulation**, **retour à la ligne**, heures et durées, et le **nom de la station** utilisée.
- Afficher séparément l'amplitude écoulée et les heures-véhicules cumulées, ainsi que le nombre de pleins. Aucune file d'attente fictive.
- Si le planificateur ne trouve pas de solution dans les bornes retenues, le résultat est **non résolu** et explique les limites ; pas de conclusion d'impossibilité ou de preuve d'optimalité fabriquée.

## Limites et risques

- **Stations non exhaustives** : les premières 300 entrées DGCCRF ne couvrent pas nécessairement la zone pertinente ; recherche parmi quatre stations au plus par carburant. Un « meilleur » choix est local au panel candidat, **pas au répertoire complet**.
- Données de station non certifiées pour autocars, horaires et ouvertures non intégrés au modèle. Le profil de routage bus ne suffit pas à certifier un passage ; contrôle opérateur obligatoire.
- L'hypothèse de disponibilité immédiate signifie zéro attente, mais **ne certifie pas qu'une station est réellement libre**.
- Pas de recharge électrique non linéaire, pauses réglementaires, dépôt, flotte mixte optimisée, planification multijours ni optimisation garantie.
- Le prix de l'énergie est national ; aucun prix par station ne participe aux comparaisons (Q19).
- Le routage et la découverte de stations restent dépendants de services externes ; cas d'erreur transparents. Un devis initial expiré doit être recalculé.

## Vérifications

`python -m pytest -q` : recherche compatible, aucun plein inventé en cas de débit nul ou de source absente, comparaison de plusieurs modèles, confidentialité et snapshot, choix entre stations de détours routés différents, rejet H₂ pour diesel, immutabilité des résultats.

`PYTHONPATH=src python tests/browser_smoke.py` : parcours de connexion, calcul de route, comparaison, sélection H₂ incompatible, station imposée gazole, tuiles journalières, sauvegarde, interface FR/EN et tracé de secours.

`node --check src/simco2/ui/app.js` et `python -m compileall -q src` : syntaxe.
