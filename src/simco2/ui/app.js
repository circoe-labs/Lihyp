/* SimCO2 : interface bilingue. Le jeton reste exclusivement en mémoire. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char =>
    ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const text = (value) => String(value ?? '');
  const dictionary = {
    fr: {
      loginKicker:'SIMULATEUR DE TRANSPORT · PROTOTYPE', loginIntro:"Estimez le coût et les émissions d'une ligne de transport avec un itinéraire calculé.",
      username:'Identifiant',password:'Mot de passe',signIn:'Se connecter',loginHelp:"Compte créé par l'administrateur du service. En local : python -m simco2.cli create-user.",
      brandSubtitle:'Transport & climat',navTitle:'SIMULER ET EXPLORER',navSimulations:'Simulations',navStations:'Stations en Normandie',
      settings:'PARAMÈTRES',navVehicles:'Véhicules',navEnergy:'Énergies par pays',prototypeNotice:'Prototype : une ligne et une journée. Planning avec détours et pleins facultatif, sans optimisation garantie.',
      logout:'Déconnexion',topKicker:'SIMULATION DE TRANSPORT',localPrototype:'Prototype',uncertified:'Données de calcul non certifiées.',
      globalNotice:'Les prix et facteurs CO₂ sont des hypothèses à renseigner. Les stations répertoriées sont indicatives.',
      scenarioKicker:'NOUVELLE ÉTUDE',scenarioTitle:'Comparer plusieurs véhicules',scenarioIntro:'Un même trajet et une même demande pour comparer les coûts, les émissions et la faisabilité des solutions.',
      stepRoute:'Itinéraire et voyageurs',scenarioName:'Nom de la simulation',date:'Date',passengerCount:'Nombre de voyageurs',
      origin:'Départ',destination:'Arrivée',originExample:'Ville ou adresse en France',destinationExample:'Ville ou adresse en France',
      calculateRoute:"Calculer l'itinéraire",routeNotReady:'Distance et durée calculées automatiquement',
      mapUnavailable:'Carte indisponible hors ligne. Les lieux et distances restent affichés.',routingMapNotice:'Trajet estimatif, accès autocar non garanti',
      stepVehicle:'Solutions à comparer',vehicle:'Véhicule',energy:'Énergie et tarif',advancedSettings:'Options avancées (facultatif)',
      windowStart:'Départs de',windowEnd:'à',maxVehicles:'Véhicules disponibles',tcoScope:'Périmètre coût',tcoVariable:'Exploitation variable',
      tcoVehicle:'TCO véhicule',tcoComplete:'TCO exploitation partiel',co2Scope:'Périmètre émissions',co2Direct:'Direct',co2Wtw:'Puits à la roue',
      infrastructureCost:'Infrastructure EUR/jour',runSimulation:'Comparer les véhicules',
      oneWayWarning:'Planning journalier activé par défaut. Étude indicative : restrictions autocars, pauses réglementaires et disponibilité des stations à vérifier.',
      mySimulations:'Mes simulations',myResults:'Résultats précédents',stationKicker:'RÉFÉRENTIELS GÉOGRAPHIQUES',
      stationTitle:'Stations en Normandie',stationIntro:'Stations hydrogène répertoriées et stations essence/gazole issues de la DGCCRF. Informations indicatives, sans garantie d’accès pour les autocars.',
      refresh:'Actualiser',filterType:'Afficher',filterAll:'Toutes les stations',filterH2:'Hydrogène H₂',filterFuel:'Essence / gazole',
      filterManual:'Ajoutées manuellement',mapInfo:'Localisations déclarées dans les sources',moreStations:'Charger davantage de stations essence',
      stationCaution:"Liste indicative : une station H₂ destinée aux véhicules légers n'est pas automatiquement compatible avec un autocar. Disponibilité et accès à confirmer auprès de l'exploitant.",
      addStation:'Ajouter une station manuellement (avancé)',stationName:'Nom de la station',longitude:'Longitude',latitude:'Latitude',
      access:'Accès',publicDeclared:'Public (déclaré)',private:'Privé',restricted:'Restreint',pump:'Pompe / connecteur',ports:'Nombre de points',
      source:'Source / méthode',sourceHint:'Document ou relevé',sourceDate:'Date de source',saveStation:'Enregistrer la station non vérifiée',
      vehicleIntro:'Créer un modèle de véhicule utilisé par les simulations. Les valeurs doivent être justifiées par une source.',
      referenceLibraryTitle:'Bibliothèque indicative — 9 références',referenceLibraryHelp:'Fourchettes HT communiquées par l’utilisateur, sans vérification constructeur. Complétez les caractéristiques nécessaires au calcul avant d’enregistrer une fiche.',referenceLibraryBadge:'À vérifier',
      referencePrice:'Acquisition / opération HT',referenceEnergyPrice:'Énergie HT',referenceEnergy100:'Coût énergie / 100 km HT',referenceMaintenance:'Maintenance préventive HT / km',referenceUse:'Compléter cette fiche',
      referenceSource:'Source : tableau utilisateur non vérifié (24/11/2026)',referenceComplete:'Renseignez places, consommation par km et capacité utile. Les médianes des fourchettes de coût sont de simples hypothèses modifiables. Aucun prix d’énergie national n’est ajouté.',referenceRetrofit:'Kit et pose seulement, pas prix du véhicule complet.',referenceCompareTitle:'Comparaison indicative des coûts sur 100 km',referencePartialCost:'Énergie + maintenance / 100 km HT',referencePartialWarning:'Comparatif partiel hors salaires, amortissement, assurance, autres coûts et CO₂e. Ce ne sont pas des résultats de simulation.',referenceMissingEnergy:'Avant de comparer, configurez cette énergie et son facteur CO₂e dans Énergies par pays.',
      vehicleFormTitle:'Fiche véhicule',vehicleUnverified:'Données constructeur non préchargées : valeurs à vérifier.',
      modelName:'Nom de variante',modelExample:'Autocar diesel A',manufacturer:'Constructeur',model:'Modèle',seats:'Places utiles',
      diesel:'Gazole (L)',electric:'Électricité (kWh)',hydrogen:'Hydrogène (kg)',biognv:'BioGNV (kg)',consumptionKm:'Consommation / km',
      consumptionHour:'Consommation / h',capacity:'Réservoir / batterie utile',reserve:'Réserve',advancedVehicle:'Coûts avancés (facultatif)',
      maintenance:'Maintenance EUR/km',labor:'Personnel EUR/h',purchase:'Acquisition EUR',residual:'Valeur résiduelle EUR',
      life:'Durée de vie (ans)',insurance:'Assurance EUR/an',saveVehicle:'Enregistrer le véhicule',cancel:'Annuler',
      vehicleCatalog:'Solutions de transport',energyIntro:"Un prix national par énergie, avec des facteurs d’émissions et leurs sources. Aucun tarif par station.",
      energyFormTitle:'Prix et facteurs d’émission',energyUnverified:'Les valeurs ne sont pas préremplies : les sources nationales et les périmètres doivent être validés.',
      country:'Pays',france:'France (FR)',nationalPrice:'Prix national EUR/unité',directFactor:'Facteur direct kgCO₂e/unité',
      wtwFactor:'Facteur puits-roue kgCO₂e/unité',optional:'facultatif',license:'Licence / droit de réutilisation',
      saveEnergy:'Enregistrer',savedEnergies:'Énergies enregistrées',fuelSourceLink:'Source officielle des prix à la pompe (DGCCRF)',
      noData:'Aucune donnée. Commencez par créer une fiche.',unverified:'Non vérifié',revision:'Version',history:'Historique',
      revise:'Modifier',view:'Voir',run:'Calculer',routeReady:'Itinéraire calculé',routeLoading:'Calcul de la route en cours…',
      routeRequired:"Calculez d'abord l'itinéraire pour obtenir une distance et une durée réelles.",
      routeStale:'Les lieux ont changé : recalculez l’itinéraire.',routeKilometers:'Distance routière',routeDuration:'Temps de route',
      demoRouting:'Démonstration OSRM : disponibilité non garantie, gabarit autocar non pris en compte.',
      routeSource:'Source du routage',configureCatalogs:'Avant de simuler, ajoutez une énergie et un véhicule dans les paramètres.',
      configureEnergy:"Créer l'énergie",configureVehicle:'Créer le véhicule',selectVehicle:'Créez un véhicule',
      selectEnergy:'Créez une énergie',seatsShort:'places',runSaved:'Simulation enregistrée',resultTitle:'Résultat de la simulation',
      status:'Statut',estimatedTco:'Coût estimé',emissions:'Émissions CO₂e',served:'Voyageurs transportés',vehiclesUsed:'Véhicules utilisés',
      energyConsumed:'Énergie consommée',passengerKm:'Voyageurs-km',tripList:'Courses',trip:'Course',departureUTC:'Départ UTC',
      passengers:'Voyageurs',consumption:'Consommation',technicalLimits:'Hypothèses et limites',
      noResult:'Aucun résultat disponible pour cette configuration.',downloadPDF:'Télécharger le PDF',
      energyPrice:'Prix national',factors:'Facteurs',direct:'Direct',wtw:'Puits-roue',energyHistory:'Historique de l’énergie',
      modelLabel:'Modèle',createdVersion:'Enregistrement effectué',savedUnverified:'Station ajoutée (non vérifiée).',
      pastRuns:'Exécutions',when:'Date',actions:'Actions',hydrogenBadge:'Hydrogène',fuelBadge:'Station-service',manualBadge:'Manuelle',
      reportedOpen:'Signalée ouverte',reportedListed:'Référencée',sourceLink:'Voir la source',
      h2Disclaimer:'Véhicules légers / utilitaires recensés : autocars non confirmés',fuelDisclaimer:'Prix individuels volontairement masqués',
      fuelUnavailable:'Le répertoire officiel des carburants est momentanément inaccessible. Les stations H₂ restent visibles.',
      fuelPartial:'Stations essence/gazole chargées par lots : cette carte ne constitue pas un inventaire exhaustif.',
      recordedLocations:'stations visibles',stationData:'Données',reportNotOptimal:'Optimisation non prouvée',
      infoRequired:'Renseignez les catalogues avant la simulation.',pdfError:'Le PDF n’a pas pu être téléchargé.',
      failure:'Échec',loadError:'Impossible de charger les données',editVehicle:`Modification du véhicule : les anciennes simulations restent inchangées.`,
      status_feasible_not_proven:'Faisable, optimum non prouvé',status_infeasible_proven:'Non réalisable',
      status_invalid_input:'Données invalides',status_provider_error:'Service de routage indisponible',
      routeExternalNotice:'Distance et temps issus du fournisseur de routage, enregistrés avec la simulation.',
      engineInFrench:'Certains diagnostics techniques sont conservés en français pour la traçabilité.',
      demoBadge:'EXEMPLE FICTIF', demoName:'Autocar diesel de démonstration', demoMake:'Aucun constructeur',
      demoModel:'Autocar générique', demoSource:'Jeu de données synthétique de démonstration, sans validation constructeur.',
      demoDescription:'Pour illustrer les solutions possibles : données non vérifiées, à remplacer avant toute étude réelle.',
      addDemo:'Ajouter cet exemple', demoAdded:'Autocar de démonstration ajouté au catalogue (valeurs fictives).',
      availableSeats:'Places', consumption100:'Consommation / 100 km', tankSize:'Capacité utile',
      selectForScenario:'Choisir pour simuler', vehicleSource:'Provenance', savedVehicle:'Enregistré',
      internalHistoryNote:'Les anciens calculs conservent leurs données, même après modification.',
      energyHistoryNote:'Une modification du tarif n’altère pas les simulations déjà réalisées.',
      addEnergy:'Ajouter une énergie', editEnergy:'Modifier une énergie', removeEnergy:'Retirer du catalogue',
      archiveEnergyConfirm:'Retirer cette énergie du catalogue actif ? Les simulations précédentes resteront inchangées.',
      archivedEnergy:'Énergie retirée du catalogue. Les anciennes simulations sont conservées.',
      petrolBadge:'Essence',dieselBadge:'Gazole',stationListTitle:'Stations',
      stationEnergy:'Énergies disponibles',stationPressure:'Pression annoncée',stationAvailability:'Disponibilité',
      stationCompatibility:'Accès autocar',stationUnknown:'À confirmer',stationSource:'Source',
      stationDetailsTitle:'Informations sur la station',stationChoose:'Afficher les détails',
      stationNoPrice:'Aucun prix par station affiché.',stationNoData:'Aucune station pour ces filtres.',
      stationArea:'Secteur',upperNormandy:'Haute-Normandie (Eure 27, Seine-Maritime 76)',
      allNormandy:'Toute la Normandie (5 départements)',stationLastUpdate:'Dernier relevé carburant déclaré',
      stationHeavyLane:'Piste poids lourds déclarée',station24h:'Automate 24 h déclaré',
      stationYes:'Oui',stationNo:'Non précisé',stationServices:'Services déclarés',

      dayPlanToggle:'Planifier les rotations et les pleins de la journée (prototype)',
      dayPlanNotice:'Trajets retour routés séparément. La fin de plage devient la fin du service. Aucune attente à la station.',
      selectedRefuelStation:'Station imposée :',noRefuelStation:'Aucune station imposée.',
      stationPolicy:'Politique de ravitaillement',stationAuto:'Automatique : station compatible si un plein est nécessaire',
      stationImposed:'Station imposée (avancé)',stationNone:'Aucun plein pendant la journée',
      stationRequired:'Choisissez une station pour le mode imposé, ou revenez au mode automatique.',
      stationIncompatible:'La station imposée ne distribue pas les énergies des véhicules sélectionnés. Choisissez le mode automatique.',
      browseRefuelStations:'Choisir une station sur la carte',clearRefuelStation:'Effacer la sélection',
      useForRefuel:'Choisir pour le planning',stationChosen:'Station retenue pour le planning journalier.',
      dieselRate:'Débit gazole (L/min, hypothèse non vérifiée)',hydrogenRate:'Débit hydrogène (kg/min, à fournir)',
      handlingTime:'Manipulation (minutes)',refuelNoQueue:'Attente à la station : 0 min. Le débit gazole 30 L/min est une hypothèse de démonstration, à vérifier ; 0 interdit un plein.',
      dayTileTitle:'Journée par solution de véhicule',dayService:'Course avec voyageurs',
      dayDeadhead:'Retour à vide',dayDetour:'Détour vers station',dayRefuel:'Ravitaillement',
      dayHandling:'Manipulation',dayWaiting:'Attente en station',dayTimeTotal:'Amplitude du service',
      dayVehicleTime:'Heures-véhicules cumulées',dayFuelStops:'Pleins',dayVehicleNumber:'Autocar',
      dayRotations:'Rotations réalisées',bestIndicative:'Coût le plus faible parmi les cas calculés (non optimal garanti)',
      stationAutoExplanation:'Recherche automatique par énergie et temps de détour. Échantillon non exhaustif, accès autocars non vérifié.',
      stationSearchLimits:'Limites de la recherche de stations',
      dayPlanUnverified:'Planning indicatif : pauses, restrictions autocars et disponibilité des stations non vérifiées.',
      dayBasicNotice:'Mode simple : une course par véhicule, sans rotation ni ravitaillement.',
      dayNoSchedule:'Aucun planning réalisable calculé pour cette solution.',
      status_no_solution_found:'Non résolu (pas de preuve d’impossibilité)',
      dayRefuelGuide:'Station imposée : seuls les véhicules compatibles pourront y faire le plein. Le mode automatique est recommandé.',
      navRouting:'API de routage',compareHint:'Sélectionnez au moins deux véhicules. L’énergie et le prix national sont associés automatiquement.',
      selectAtLeastTwo:'Sélectionnez au moins deux véhicules différents à comparer.',
      compareNeedCatalog:'Pour comparer, ajoutez au moins deux véhicules avec une énergie configurée dans Paramètres.',
      compareNeedRoute:'Calculez d’abord l’itinéraire : la distance et le tracé seront utilisés pour la comparaison.',
      compareInvalidField:'Vérifiez ce champ avant la comparaison : ',
      compareRunning:'Comparaison en cours…',compareFailed:'Comparaison impossible : ',
      compareDone:'Comparaison enregistrée et affichée ci-dessous.',
      routeSketchNotice:'Tracé schématique issu du calcul routier. Fond de carte interactif indisponible dans ce navigateur.',
      routeSketchNoData:'Tracé indisponible : la géométrie de l’itinéraire est absente.',

      missingEnergyOption:'Énergie non configurée',compareResultsTitle:'Comparaison des solutions',
      myComparisons:'Comparaisons enregistrées',previousRuns:'Anciennes simulations individuelles',
      compareVehicle:'Véhicule',compareEnergy:'Énergie',compareCost:'Coût total',compareEmissions:'Émissions CO₂e',
      comparePerPassenger:'CO₂e / voyageur',compareConsumption:'Consommation',compareFeasibility:'Faisabilité',
      comparePdf:'Rapport PDF',compareMissing:'Non calculable',compareReadOnly:'Cas indépendants : aucune flotte mixte ni optimisation garantie.',
      compareSameInputs:'Même trajet, même demande, même date et mêmes périmètres pour chaque véhicule.',
      compareStatus:'Faisable (optimum non prouvé)',compareUnavailable:'Aucune comparaison enregistrée.',
      routeMapTitle:'Carte de l’itinéraire',routeMapHint:'Itinéraire calculé',routingSettingsTitle:'API de routage',
      routingSettingsIntro:'Configurez le service de calcul des distances et temps. Les clés restent côté serveur.',
      routingPanelTitle:'Calcul d’itinéraire bus et camion',
      routingPanelHelp:'Geoapify propose bus, camion 22 t et camion lourd 40 t ; les restrictions locales restent à confirmer.',
      providerLabel:'Fournisseur',profileLabel:'Profil',endpointLabel:'Adresse du service',
      geoKeyStatus:'Clé Geoapify',orsKeyStatus:'Clé ORS',save:'Enregistrer',
      routingCaution:'Les profils ne garantissent pas la conformité des dimensions, du gabarit et des accès autocars.',
      geoapifyKeyTitle:'Geoapify — bus / camion',geoapifyKeyDesc:'Bus par défaut ; camion 22 t et 40 t en option.',
      orsKeyTitle:'openrouteservice — alternative',orsKeyDesc:'Profil routage poids lourd ; limitations à vérifier.',
      apiKeyLabel:'Clé API (conservée localement sur le serveur)',saveKey:'Enregistrer la clé',removeKey:'Supprimer la clé',
      getGeoapifyKey:'Obtenir une clé Geoapify',getOrsKey:'Obtenir une clé ORS',
      routingOperatorNotice:'La modification des clés est réservée à l’exploitant connecté en local. Sur un serveur public, utiliser des secrets d’environnement.',
      routingTestTitle:'Tester un itinéraire',routingTestHint:'Exemple de test : quais à Lyon. Coordonnées : longitude, latitude.',
      testStart:'Départ (longitude, latitude)',testEnd:'Arrivée (longitude, latitude)',testRouting:'Tester le routage',
      routingSecurityNote:'Les clés ne sont jamais renvoyées par l’API et ne figurent ni dans les devis ni dans les résultats.',
      routingReady:'Configuré (non testé)',routingNotReady:'À configurer',keySaved:'Clé enregistrée côté serveur',keyMissing:'Clé absente',
      localOnly:'Opération accessible uniquement en local',providerSaved:'Paramètres enregistrés',
      keyRemoved:'Clé supprimée',testRouteResult:'Résultat du test',profileBus:'Autocar / bus',
      profileTruck:'Camion standard · 22 t',profileHeavy:'Camion lourd · 40 t',profileHgv:'Poids lourd (ORS)',
      profileCar:'Voiture / démo',
    },
    en: {
      loginKicker:'PASSENGER TRANSPORT SIMULATOR · PROTOTYPE',loginIntro:'Estimate costs and emissions for a passenger route using computed road distances.',
      username:'Username',password:'Password',signIn:'Sign in',loginHelp:'An account is created by the service administrator. Locally: python -m simco2.cli create-user.',
      brandSubtitle:'Transport & climate',navTitle:'SIMULATE AND EXPLORE',navSimulations:'Simulations',navStations:'Stations in Normandy',
      settings:'SETTINGS',navVehicles:'Vehicles',navEnergy:'Energy by country',prototypeNotice:'Prototype: one line, one day. Optional indicative scheduling with refuelling, no certified optimization.',
      logout:'Sign out',topKicker:'TRANSPORT SIMULATION',localPrototype:'Prototype',uncertified:'Calculation data is not certified.',
      globalNotice:'Energy prices and CO₂ factors must be provided as assumptions. Listed stations are for reference only.',
      scenarioKicker:'NEW STUDY',scenarioTitle:'Compare transport options',scenarioIntro:'Compare costs, emissions and feasibility of several vehicles on the same route and passenger demand.',
      stepRoute:'Route and passengers',scenarioName:'Simulation name',date:'Date',passengerCount:'Passengers',
      origin:'Origin',destination:'Destination',originExample:'City or address in France',destinationExample:'City or address in France',
      calculateRoute:'Calculate route',routeNotReady:'Distance and duration are computed automatically',
      mapUnavailable:'Map unavailable offline. Route locations and figures are still shown.',routingMapNotice:'Estimated route; coach access not guaranteed',
      stepVehicle:'Options to compare',vehicle:'Vehicle',energy:'Energy and price',advancedSettings:'Advanced options (optional)',
      windowStart:'Departures from',windowEnd:'until',maxVehicles:'Available vehicles',tcoScope:'Cost scope',tcoVariable:'Variable operating cost',
      tcoVehicle:'Vehicle TCO',tcoComplete:'Partial operating TCO',co2Scope:'Emissions scope',co2Direct:'Direct',co2Wtw:'Well-to-wheel',
      infrastructureCost:'Infrastructure EUR/day',runSimulation:'Compare vehicles',
      oneWayWarning:'Daily scheduling enabled by default. Indicative study: coach restrictions, legal breaks and station availability require verification.',
      mySimulations:'My simulations',myResults:'Previous results',stationKicker:'LOCATION DIRECTORY',
      stationTitle:'Stations in Normandy',stationIntro:'Listed hydrogen stations and official petrol/diesel stations from DGCCRF. Indicative information; coach access is not guaranteed.',
      refresh:'Refresh',filterType:'Show',filterAll:'All stations',filterH2:'Hydrogen H₂',filterFuel:'Petrol / diesel',
      filterManual:'Manually added',mapInfo:'Locations as published by data sources',moreStations:'Load more petrol stations',
      stationCaution:'Caution: a hydrogen station for light vehicles is not automatically compatible with a coach. Check availability and access with the operator.',
      addStation:'Add a station manually (advanced)',stationName:'Station name',longitude:'Longitude',latitude:'Latitude',
      access:'Access',publicDeclared:'Public (declared)',private:'Private',restricted:'Restricted',pump:'Pump / connector',ports:'Number of outlets',
      source:'Source / methodology',sourceHint:'Document or observation',sourceDate:'Source date',saveStation:'Save as unverified station',
      vehicleIntro:'Create a vehicle model for use in simulations. Values should be backed by a source.',
      referenceLibraryTitle:'Indicative library — 9 references',referenceLibraryHelp:'User-supplied VAT-excluded ranges, unverified by manufacturers. Complete the required technical values before saving.',referenceLibraryBadge:'Unverified',
      referencePrice:'Purchase / operation (excl. VAT)',referenceEnergyPrice:'Energy price (excl. VAT)',referenceEnergy100:'Energy cost / 100 km (excl. VAT)',referenceMaintenance:'Preventive maintenance / km (excl. VAT)',referenceUse:'Complete this vehicle',
      referenceSource:'Source: unverified user table (24 Nov 2026)',referenceComplete:'Enter seats, consumption per km and usable capacity. Midpoints of cost ranges are editable assumptions. No national energy price is added.',referenceRetrofit:'Conversion kit and installation only, not a complete vehicle price.',referenceCompareTitle:'Indicative comparison of costs over 100 km',referencePartialCost:'Energy + maintenance / 100 km, excl. VAT',referencePartialWarning:'Partial comparison excluding staff, depreciation, insurance, other costs and CO₂e. Not simulated results.',referenceMissingEnergy:'Configure this energy type and its CO₂e factor in Energy by country before comparing.',
      vehicleFormTitle:'Vehicle details',vehicleUnverified:'No manufacturer data preloaded: values require validation.',
      modelName:'Variant name',modelExample:'Diesel coach A',manufacturer:'Manufacturer',model:'Model',seats:'Usable seats',
      diesel:'Diesel (L)',electric:'Electricity (kWh)',hydrogen:'Hydrogen (kg)',biognv:'Bio-CNG (kg)',consumptionKm:'Consumption / km',
      consumptionHour:'Consumption / hour',capacity:'Usable tank / battery capacity',reserve:'Reserve',advancedVehicle:'Advanced costs (optional)',
      maintenance:'Maintenance EUR/km',labor:'Staff EUR/hour',purchase:'Purchase price EUR',residual:'Residual value EUR',
      life:'Lifetime (years)',insurance:'Insurance EUR/year',saveVehicle:'Save vehicle',cancel:'Cancel',
      vehicleCatalog:'Transport options',energyIntro:'One national price per energy type, with sourced emission factors. No station pricing.',
      energyFormTitle:'Price and emission factors',energyUnverified:'Values are not preloaded: national sources and emission boundaries must be validated.',
      country:'Country',france:'France (FR)',nationalPrice:'National price EUR/unit',directFactor:'Direct factor kgCO₂e/unit',
      wtwFactor:'Well-to-wheel factor kgCO₂e/unit',optional:'optional',license:'Licence / reuse rights',
      saveEnergy:'Save',savedEnergies:'Saved energies',fuelSourceLink:'Official fuel pump-price source (DGCCRF)',
      noData:'No data yet. Create an entry to begin.',unverified:'Unverified',revision:'Version',history:'History',
      revise:'Edit',view:'View',run:'Run',routeReady:'Route calculated',routeLoading:'Calculating road route…',
      routeRequired:'Calculate the route first to get a real distance and duration.',
      routeStale:'The places changed: calculate the route again.',routeKilometers:'Road distance',routeDuration:'Travel time',
      demoRouting:'OSRM demo: uptime not guaranteed; coach size restrictions not applied.',
      routeSource:'Routing source',configureCatalogs:'Before simulating, add an energy source and a vehicle in Settings.',
      configureEnergy:'Set up energy',configureVehicle:'Set up vehicle',selectVehicle:'Add a vehicle',
      selectEnergy:'Add an energy source',seatsShort:'seats',runSaved:'Simulation saved',resultTitle:'Simulation result',
      status:'Status',estimatedTco:'Estimated cost',emissions:'CO₂e emissions',served:'Passengers served',vehiclesUsed:'Vehicles used',
      energyConsumed:'Energy used',passengerKm:'Passenger-km',tripList:'Trips',trip:'Trip',departureUTC:'Departure UTC',
      passengers:'Passengers',consumption:'Consumption',technicalLimits:'Assumptions and limitations',
      noResult:'No results available for this setup.',downloadPDF:'Download PDF',
      energyPrice:'National price',factors:'Factors',direct:'Direct',wtw:'Well-to-wheel',energyHistory:'Energy version history',
      modelLabel:'Model',createdVersion:'Saved successfully',savedUnverified:'Station added (unverified).',
      pastRuns:'Runs',when:'Date',actions:'Actions',hydrogenBadge:'Hydrogen',fuelBadge:'Filling station',manualBadge:'Manual',
      reportedOpen:'Reported open',reportedListed:'Listed',sourceLink:'View source',
      h2Disclaimer:'Light/utility vehicles listed; coach compatibility not confirmed',fuelDisclaimer:'Per-station prices deliberately hidden',
      fuelUnavailable:'Official petrol station feed is temporarily unavailable. Hydrogen stations remain visible.',
      fuelPartial:'Petrol/diesel stations are loaded in batches: this map is not a complete inventory.',
      recordedLocations:'stations shown',stationData:'Data',reportNotOptimal:'Optimality not proven',
      infoRequired:'Configure the catalogues before running a simulation.',pdfError:'Could not download the PDF.',
      failure:'Failure',loadError:'Could not load data',editVehicle:'Edit this vehicle. Past simulation results will remain unchanged.',
      status_feasible_not_proven:'Feasible; optimality not proven',status_infeasible_proven:'Infeasible',
      status_invalid_input:'Invalid input',status_provider_error:'Routing service unavailable',
      routeExternalNotice:'Distance and duration are supplied by the routing provider and saved with this simulation.',
      engineInFrench:'Some technical diagnostics are kept in French for traceability.',
      demoBadge:'ILLUSTRATIVE EXAMPLE', demoName:'Demo diesel coach', demoMake:'No manufacturer',
      demoModel:'Generic coach', demoSource:'Synthetic demonstration fixture, not validated by any manufacturer.',
      demoDescription:'Shows how a solution is presented. Values are unverified and must be replaced for real studies.',
      addDemo:'Add this example', demoAdded:'Demo coach added to catalogue (illustrative figures).',
      availableSeats:'Seats', consumption100:'Consumption / 100 km', tankSize:'Usable capacity',
      selectForScenario:'Use in simulation', vehicleSource:'Data source', savedVehicle:'Saved',
      internalHistoryNote:'Previous simulations keep their original values after edits.',
      energyHistoryNote:'Changing a price never alters previously saved simulations.',
      addEnergy:'Add energy', editEnergy:'Edit energy', removeEnergy:'Remove from catalogue',
      archiveEnergyConfirm:'Remove this energy from the active catalogue? Earlier simulations will remain unchanged.',
      archivedEnergy:'Energy removed from the catalogue. Historical simulations are preserved.',
      petrolBadge:'Petrol',dieselBadge:'Diesel',stationListTitle:'Stations',
      stationEnergy:'Available fuels',stationPressure:'Reported pressure',stationAvailability:'Availability',
      stationCompatibility:'Coach access',stationUnknown:'To be confirmed',stationSource:'Source',
      stationDetailsTitle:'Station information',stationChoose:'Show details',
      stationNoPrice:'No individual station prices displayed.',stationNoData:'No stations match these filters.',
      stationArea:'Area',upperNormandy:'Upper Normandy (Eure 27, Seine-Maritime 76)',
      allNormandy:'All Normandy (5 departments)',stationLastUpdate:'Latest reported fuel observation',
      stationHeavyLane:'Reported heavy vehicle lane',station24h:'Reported 24h pump',
      stationYes:'Yes',stationNo:'Not specified',stationServices:'Reported services',

      dayPlanToggle:'Schedule daily rotations and refuelling (prototype)',
      dayPlanNotice:'Reverse legs are separately routed. End time means service completion. No station waiting time.',
      selectedRefuelStation:'Required station:',noRefuelStation:'No required station.',
      stationPolicy:'Refuelling policy',stationAuto:'Automatic: compatible station if refuelling is needed',
      stationImposed:'Required station (advanced)',stationNone:'No refuelling during the day',
      stationRequired:'Choose a station for required-station mode, or switch to automatic.',
      stationIncompatible:'The required station does not supply any selected vehicle energy. Use automatic mode.',
      browseRefuelStations:'Choose a station on the map',clearRefuelStation:'Clear selection',
      useForRefuel:'Use for day schedule',stationChosen:'Station selected for the daily schedule.',
      dieselRate:'Diesel pump flow (L/min, unverified assumption)',hydrogenRate:'Hydrogen flow (kg/min, required)',
      handlingTime:'Handling time (minutes)',refuelNoQueue:'Station waiting: 0 min. Diesel flow 30 L/min is an illustrative assumption to verify; 0 disables refuelling.',
      dayTileTitle:'Daily schedule by vehicle solution',dayService:'Passenger service',
      dayDeadhead:'Empty return trip',dayDetour:'Detour to filling station',dayRefuel:'Refuelling',
      dayHandling:'Handling',dayWaiting:'Waiting at station',dayTimeTotal:'Service elapsed time',
      dayVehicleTime:'Total vehicle-hours',dayFuelStops:'Fuel stops',dayVehicleNumber:'Coach',
      dayRotations:'Trips completed',bestIndicative:'Lowest cost among calculated cases (not proven optimal)',
      stationAutoExplanation:'Automatic search by fuel and routed detour time. Non-exhaustive sample, coach access unverified.',
      stationSearchLimits:'Station search limitations',
      dayPlanUnverified:'Indicative plan: breaks, bus access and filling station availability not verified.',
      dayBasicNotice:'Basic mode: one trip per vehicle, no rotations or refuelling.',
      dayNoSchedule:'No feasible schedule found for this option.',
      status_no_solution_found:'Unresolved (not proven infeasible)',
      dayRefuelGuide:'Required station: only compatible vehicles can refuel here. Automatic mode is recommended.',
      navRouting:'Routing API',compareHint:'Select at least two vehicles. Energy type and national price are matched automatically.',
      selectAtLeastTwo:'Select at least two different vehicles for the comparison.',
      compareNeedCatalog:'To compare options, add at least two vehicles with configured energy types in Settings.',
      compareNeedRoute:'Calculate the route first: distance and geometry are used for the comparison.',
      compareInvalidField:'Check this field before comparing: ',
      compareRunning:'Calculating comparison…',compareFailed:'Cannot compare: ',
      compareDone:'Comparison saved and displayed below.',
      routeSketchNotice:'Schematic of the calculated road route. Interactive base map is unavailable in this browser.',
      routeSketchNoData:'Route shape unavailable: routing geometry is missing.',

      missingEnergyOption:'Energy not configured',compareResultsTitle:'Transport options comparison',
      myComparisons:'Saved comparisons',previousRuns:'Previous individual simulations',
      compareVehicle:'Vehicle',compareEnergy:'Energy',compareCost:'Total cost',compareEmissions:'CO₂e emissions',
      comparePerPassenger:'CO₂e / passenger',compareConsumption:'Consumption',compareFeasibility:'Feasibility',
      comparePdf:'PDF report',compareMissing:'Not calculated',compareReadOnly:'Independent cases only: no mixed fleet and no certified optimization.',
      compareSameInputs:'Same route, passenger demand, date and calculation boundaries for every vehicle.',
      compareStatus:'Feasible (optimum not proven)',compareUnavailable:'No comparison saved yet.',
      routeMapTitle:'Route map',routeMapHint:'Calculated itinerary',routingSettingsTitle:'Routing API',
      routingSettingsIntro:'Configure routing for road distance and travel time. API keys remain on the server.',
      routingPanelTitle:'Bus and truck routing',
      routingPanelHelp:'Geoapify offers bus, 22t truck and 40t heavy truck profiles; local restrictions still require verification.',
      providerLabel:'Provider',profileLabel:'Profile',endpointLabel:'Service endpoint',
      geoKeyStatus:'Geoapify key',orsKeyStatus:'ORS key',save:'Save',
      routingCaution:'These profiles do not guarantee the coach’s dimensions, clearance or actual road access.',
      geoapifyKeyTitle:'Geoapify — bus / truck',geoapifyKeyDesc:'Bus by default; optional 22t and 40t truck profiles.',
      orsKeyTitle:'openrouteservice — alternative',orsKeyDesc:'Heavy goods profile; restrictions must be checked.',
      apiKeyLabel:'API key (stored locally on server)',saveKey:'Save key',removeKey:'Remove key',
      getGeoapifyKey:'Get a Geoapify key',getOrsKey:'Get an ORS key',
      routingOperatorNotice:'Only the operator logged in locally can edit keys. Use environment secrets on a public server.',
      routingTestTitle:'Test route',routingTestHint:'Test example: Lyon river quays. Coordinates in longitude, latitude order.',
      testStart:'Start (longitude, latitude)',testEnd:'End (longitude, latitude)',testRouting:'Test routing',
      routingSecurityNote:'Keys are never returned by the API or included in route quotes or simulation results.',
      routingReady:'Configured (not tested)',routingNotReady:'Not configured',keySaved:'Key saved on server',keyMissing:'No key',
      localOnly:'Only available on the local server',providerSaved:'Settings saved',
      keyRemoved:'Key removed',testRouteResult:'Test result',profileBus:'Coach / bus',
      profileTruck:'Standard truck · 22 t',profileHeavy:'Heavy truck · 40 t',profileHgv:'Heavy goods vehicle (ORS)',
      profileCar:'Car / demo',
    },
  };
  let language = 'fr';
  try { if (localStorage.getItem('simco2_language') === 'en') language = 'en'; } catch (_) {}
  const t = (key) => dictionary[language][key] ?? dictionary.fr[key] ?? key;
  let token = '', actor = null, currentQuote = null, currentRoute = null, currentRun = null;
  let comparisons = [], currentComparison = null, selectedVehicleIds = new Set(), routingConfig = null;
  let comparisonSelectionInitialized = false;
  let plannedStation = null;
  let energies = [], vehicles = [], customStations = [], h2Stations = [], fuelStations = [], scenarios = [], runs = [];
  let fuelPage = null, stationLoading = false, editingVehicleKey = null, energyHistoryCode = null;
  let routeMap = null, stationsMap = null, routeDrawings = [], stationDrawings = [];
  const field = (form, key) => form.elements.namedItem(key).value;
  const dataOf = (form) => Object.fromEntries(new FormData(form).entries());
  const routeTime = (seconds) => `${Math.floor(seconds / 3600) ? `${Math.floor(seconds / 3600)} h ` : ''}${Math.ceil(seconds % 3600 / 60)} min`;
  const number = (value, digits=1) => new Intl.NumberFormat(language, {maximumFractionDigits:digits}).format(Number(value));
  const safeUrl = s => /^https:\/\/[\w.-]+\//.test(s || '') ? s : null;

  function message(msg, isError=false) {
    const box = $('feedback'); box.classList.remove('hidden');
    box.classList.toggle('error', isError); box.textContent = msg;
  }
  function compareNotice(text, isError=true) {
    const node = $('compare-inline-notice');
    if (!node) return;
    node.textContent = text || '';
    node.classList.toggle('hidden', !text);
    node.classList.toggle('error', !!text && isError);
    node.classList.toggle('success', !!text && !isError);
  }
  function compareProblem(text) {
    compareNotice(text,true);
    // Always show validation next to the submit button, not at the page top.
    $('compare-inline-notice').scrollIntoView({block:'nearest',behavior:'smooth'});
  }
  async function api(url, options={}) {
    const h = {'Accept':'application/json', ...options.headers};
    if (token) h.Authorization = `Bearer ${token}`;
    if (options.body && !(options.body instanceof FormData)) h['Content-Type'] = 'application/json';
    const res = await fetch(url, {...options, headers:h});
    if (!res.ok) {
      let parsed = {};
      try { parsed = await res.json(); } catch (_) {}
      const desc = Array.isArray(parsed.detail)
        ? parsed.detail.map(e => `${e.loc?.slice(-1)[0] || 'field'}: ${e.msg}`).join('; ')
        : (parsed.error?.message || parsed.detail || res.statusText);
      throw new Error(`${res.status} · ${desc}`);
    }
    if (options.raw) return res;
    return res.status === 204 ? null : res.json();
  }
  function applyLanguage() {
    document.documentElement.lang = language;
    document.title = `SimCO₂ — ${t('navSimulations')}`;
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
    $('language-toggle').textContent = language === 'fr' ? 'EN' : 'FR';
    $('language-toggle').setAttribute('aria-label', language === 'fr' ? 'Switch to English' : 'Passer en français');
    if ($('day-station-name')) updatePlannedStation();
    const active = document.querySelector('.nav-item.active');
    $('page-title').textContent = t({scenarios:'navSimulations',stations:'navStations',vehicles:'navVehicles',energy:'navEnergy',routing:'navRouting'}[active?.dataset.view] || 'navSimulations');
    renderEnergies();
    if (energyEditingCode) $('energy-editor-title').textContent=t('editEnergy');
    renderVehicles(); renderReferenceLibrary(); renderScenarios(); renderRuns(); renderStations();
    fillScenarioSelects();
    if (currentRoute) renderRouteSummary(currentRoute);
    if (currentRun) showResult(currentRun, false);
    if (currentComparison) showComparison(currentComparison, false);
    renderRoutingConfig();
  }
  $('language-toggle').addEventListener('click', () => {
    language = language === 'fr' ? 'en' : 'fr';
    try { localStorage.setItem('simco2_language', language); } catch (_) {}
    applyLanguage();
  });

  function show(view) {
    for (const el of document.querySelectorAll('.view')) el.classList.toggle('hidden', el.id !== `view-${view}`);
    for (const el of document.querySelectorAll('.nav-item')) el.classList.toggle('active', el.dataset.view === view);
    $('page-title').textContent = t({scenarios:'navSimulations',stations:'navStations',vehicles:'navVehicles',energy:'navEnergy',routing:'navRouting'}[view]);
    $('feedback').classList.add('hidden');
    if (view === 'energy') loadEnergies();
    if (view === 'vehicles') { loadVehicles(); if(!referenceEntries.length) loadReferenceLibrary(); }
    if (view === 'stations') loadStations();
    if (view === 'scenarios') { loadScenarios(); loadRuns(); loadComparisons(); }
    if (view === 'routing') loadRoutingConfig();
    // Leaflet ne sait pas mesurer une carte initialisée dans une section masquée.
    requestAnimationFrame(() => {
      if (view === 'stations') stationsMap?.invalidateSize({pan:false});
      if (view === 'scenarios' && !$('route-map').classList.contains('hidden'))
        routeMap?.invalidateSize({pan:false});
    });
  }
  document.querySelectorAll('.nav-item').forEach(el => el.addEventListener('click', () => show(el.dataset.view)));
  document.addEventListener('click', event => {
    const link = event.target.closest('[data-goto]');
    if (link) { event.preventDefault(); show(link.dataset.goto); }
  });
  function table(el, columns, rows) {
    el.innerHTML = rows.length
      ? `<table><thead><tr>${columns.map(c => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table>`
      : `<div class="empty-state">${esc(t('noData'))}</div>`;
  }

  $('login-form').addEventListener('submit', async event => {
    event.preventDefault(); $('login-message').textContent = '';
    try {
      const response = await api('/auth/login', {method:'POST', body:JSON.stringify(dataOf(event.currentTarget))});
      token = response.access_token; actor = response.user;
      $('user-label').textContent = actor.username;
      $('login').classList.add('hidden'); $('shell').classList.remove('hidden');
      const [e,v,s,r,custom] = await Promise.all([
        api('/energies'),api('/vehicles'),api('/scenarios'),api('/runs'),api('/stations')]);
      [energies,vehicles,scenarios,runs,customStations] = [e,v,s,r,custom];
      fillScenarioSelects(); show('scenarios'); applyLanguage();
    } catch (error) {
      $('login-message').textContent = error.message;
      token = ''; $('shell').classList.add('hidden'); $('login').classList.remove('hidden');
    }
  });
  $('logout-button').addEventListener('click', async () => {
    try { await api('/auth/logout', {method:'POST'}); } catch (_) {}
    token = ''; actor = null; currentQuote = null; currentRoute = null;
    $('shell').classList.add('hidden'); $('login').classList.remove('hidden');
    $('login-form').elements.namedItem('password').value = '';
  });

  async function loadEnergies() {
    try { energies = await api('/energies'); renderEnergies(); fillScenarioSelects(); }
    catch (error) { message(error.message, true); }
  }
  let energyEditingCode = null;
  function energyName(code) {
    return t(({DIESEL:'diesel',ELECTRIC:'electric',H2:'hydrogen',BIOGNV:'biognv'})[code] || 'energy');
  }
  function closeEnergyEditor() {
    $('energy-editor').classList.add('hidden');
    $('add-energy').setAttribute('aria-expanded','false');
    energyEditingCode = null;
    $('energy-code').disabled = false;
  }
  function openEnergyEditor(version=null) {
    const form=$('energy-form'); form.reset();
    energyEditingCode=version?.payload.energy_code || null;
    const today = new Date().toISOString().slice(0,10);
    form.elements.namedItem('source_date').value=today;
    form.elements.namedItem('country_iso').value=$('energy-country-filter').value;
    if (version) {
      const p=version.payload;
      for (const key of ['country_iso','energy_code','price_per_unit','source','source_date','license'])
        form.elements.namedItem(key).value=p[key] ?? '';
      form.elements.namedItem('direct').value=p.factors?.direct ?? '';
      form.elements.namedItem('well_to_wheel').value=p.factors?.well_to_wheel ?? '';
    }
    $('energy-code').disabled=!!version;
    $('energy-editor-title').textContent=t(version?'editEnergy':'energyFormTitle');
    $('energy-editor').classList.remove('hidden');
    $('add-energy').setAttribute('aria-expanded','true');
    $('energy-editor').scrollIntoView({block:'nearest'});
    form.elements.namedItem('price_per_unit').focus();
  }
  $('add-energy').addEventListener('click',()=>{
    if (!$('energy-editor').classList.contains('hidden')) closeEnergyEditor();
    else openEnergyEditor();
  });
  $('close-energy').addEventListener('click',closeEnergyEditor);
  function renderEnergies() {
    if (!$('energy-table')) return;
    const rows=energies.filter(e=>e.payload.country_iso===$('energy-country-filter').value).map(e=> {
      const p=e.payload,code=p.energy_code,unit=esc(p.unit);
      const icon=({DIESEL:'⛽',ELECTRIC:'⚡',H2:'H₂',BIOGNV:'♻'})[code]||'◉';
      const srcUrl=safeUrl(p.source);
      const source=srcUrl?`<a href="${esc(srcUrl)}" rel="noopener" target="_blank">${esc(p.source)}</a>`:esc(p.source);
      return `<tr><td><span class="energy-name"><span class="energy-icon" aria-hidden="true">${icon}</span><span><strong>${esc(energyName(code))}</strong><small>${esc(t('unverified'))} · ${unit}</small></span></span></td>
        <td><strong>${esc(number(Number(p.price_per_unit),2))}</strong> EUR/${unit}</td>
        <td>${esc(p.factors.direct??'—')}</td><td>${esc(p.factors.well_to_wheel??'—')}</td>
        <td>${source}<small>${esc(p.source_date)}</small></td>
        <td><div class="energy-action-row"><button type="button" class="table-action" data-energy-edit="${esc(code)}">✎ ${esc(t('revise'))}</button>
        <button type="button" class="table-action" data-energy-remove="${esc(code)}">× ${esc(t('removeEnergy'))}</button>
        <button type="button" class="table-action" data-energy-history="${esc(code)}">${esc(t('history'))}</button></div></td></tr>`;
    });
    table($('energy-table'),[t('energy'),t('energyPrice'),t('directFactor'),t('wtwFactor'),t('source'),t('actions')],rows);
    document.querySelectorAll('[data-energy-history]').forEach(b=>b.addEventListener('click',()=>loadEnergyHistory(b.dataset.energyHistory)));
    document.querySelectorAll('[data-energy-edit]').forEach(b=>b.addEventListener('click',()=>{
      const v=energies.find(v=>v.payload.energy_code===b.dataset.energyEdit);
      if(v)openEnergyEditor(v);
    }));
    document.querySelectorAll('[data-energy-remove]').forEach(b=>b.addEventListener('click',async()=>{
      const code=b.dataset.energyRemove;
      if(!window.confirm(t('archiveEnergyConfirm')))return;
      try{
        await api(`/energies/${encodeURIComponent($('energy-country-filter').value)}/${encodeURIComponent(code)}/archive`,{method:'POST'});
        closeEnergyEditor();await loadEnergies();message(t('archivedEnergy'));
      }catch(error){message(error.message,true);}
    }));
  }
  $('energy-country-filter').addEventListener('change',renderEnergies);
  async function loadEnergyHistory(code) {
    energyHistoryCode = code;
    try {
      const versions = await api(`/energies/${encodeURIComponent($('energy-country-filter').value)}/${encodeURIComponent(code)}/versions`);
      $('energy-history').innerHTML = `<h4>${esc(t('energyHistory'))} ${esc(code)}</h4><p>${esc(t('energyHistoryNote'))}</p><ul>${versions.map(v =>
        `<li>v${v.revision} · ${esc(v.payload.price_per_unit)} EUR/${esc(v.payload.unit)} · ${esc(v.payload.source)} · ${esc(v.created_at)}</li>`).join('')}</ul>`;
    } catch (error) { message(error.message, true); }
  }
  $('energy-form').addEventListener('submit', async event => {
    event.preventDefault(); const d=dataOf(event.currentTarget), factors = {};
    if (d.direct.trim()) factors.direct = d.direct.trim();
    if (d.well_to_wheel.trim()) factors.well_to_wheel = d.well_to_wheel.trim();
    d.energy_code = energyEditingCode || d.energy_code;
    const unit = {DIESEL:'L',ELECTRIC:'kWh',H2:'kg',BIOGNV:'kg'}[d.energy_code];
    try {
      await api('/energies', {method:'POST', body:JSON.stringify({country_iso:d.country_iso,
        energy_code:d.energy_code,unit,price_per_unit:d.price_per_unit, factors, source:d.source,
        source_date:d.source_date,license:d.license,quality:'unverified'})});
      closeEnergyEditor(); await loadEnergies(); message(t('createdVersion'));
    } catch(error) { message(error.message, true); }
  });
  $('reload-energy').addEventListener('click', loadEnergies);

  async function loadVehicles() {
    try { vehicles = await api('/vehicles'); renderVehicles(); fillScenarioSelects(); }
    catch(error) { message(error.message, true); }
  }
  // Clearly labelled synthetic example. It is a preview, not a manufacturer specification
  // and is only stored after the user clicks the button (never on an implicit GET/login).
  function demoCoach() {
    return {
      label:t('demoName'), manufacturer:t('demoMake'), model:t('demoModel'),
      kind:'bus', seats:50, energy_code:'DIESEL', unit:'L',
      consumption_per_km:'0.2', consumption_per_hour:'0', usable_capacity:'100', reserve:'5',
      maintenance_eur_per_km:'0', labor_eur_per_h:'0', purchase_eur:'0', residual_eur:'0',
      life_years:10, insurance_eur_year:'0', connectors:[],
      source:t('demoSource'), quality:'unverified',
    };
  }

  // Reference values are not complete vehicle specifications or national energy prices.
  // Fetching these cards never inserts vehicles or changes energy prices in the database.
  let referenceEntries = [];
  function referenceRange(values, suffix='') {
    return `${number(values[0],2)} – ${number(values[1],2)}${suffix}`;
  }
  function renderReferenceLibrary() {
    const node=$('reference-library'); if(!node || !referenceEntries.length) return;
    node.innerHTML=referenceEntries.map(e=>`<article class="reference-card">
      <div class="reference-card-top"><span class="solution-badge">${esc(t('referenceLibraryBadge'))}</span>
      <span class="solution-energy">${esc(energyName(e.energy_code))}</span></div>
      <h4>${esc(e.label)}</h4><p class="small muted">${esc(e.model)}</p>
      <dl class="reference-facts">
        <div><dt>${esc(t('referencePrice'))}</dt><dd>${esc(referenceRange(e.purchase_eur_ht,' €'))}</dd></div>
        <div><dt>${esc(t('referenceEnergyPrice'))}</dt><dd>${esc(referenceRange(e.price_per_energy_eur_ht,' €'))}/${esc(e.unit)}</dd></div>
        <div><dt>${esc(t('referenceEnergy100'))}</dt><dd>${esc(referenceRange(e.energy_cost_100km_eur_ht,' €'))}</dd></div>
        <div><dt>${esc(t('referenceMaintenance'))}</dt><dd>${esc(referenceRange(e.maintenance_eur_per_km_ht,' €'))}</dd></div>
      </dl>
      ${e.purchase_scope==='retrofit_kit_installation'?`<p class="small warning-text">${esc(t('referenceRetrofit'))}</p>`:''}
      <button type="button" class="button outline" data-prefill-reference="${esc(e.id)}">${esc(t('referenceUse'))}</button>
    </article>`).join('');
    const costRows=referenceEntries.map(e=>{
      const low=e.energy_cost_100km_eur_ht[0]+100*e.maintenance_eur_per_km_ht[0];
      const high=e.energy_cost_100km_eur_ht[1]+100*e.maintenance_eur_per_km_ht[1];
      return `<tr><td>${esc(e.label)}<small>${esc(e.model)}</small></td><td>${esc(energyName(e.energy_code))}</td><td><strong>${esc(referenceRange([low,high],' €'))}</strong></td></tr>`;
    });
    const table=document.createElement('section');table.className='reference-comparison';
    table.innerHTML=`<h4>${esc(t('referenceCompareTitle'))}</h4><p class="small muted">${esc(t('referencePartialWarning'))}</p>
      <div class="table-wrap"><table><thead><tr><th>${esc(t('modelLabel'))}</th><th>${esc(t('energy'))}</th><th>${esc(t('referencePartialCost'))}</th></tr></thead>
      <tbody>${costRows.join('')}</tbody></table></div>`;
    node.after(table);
    document.querySelectorAll('.reference-comparison').forEach(el=>{if(el!==table)el.remove();});
    node.querySelectorAll('[data-prefill-reference]').forEach(b=>b.addEventListener('click',()=>{
      const e=referenceEntries.find(e=>e.id===b.dataset.prefillReference);if(e)prefillReference(e);
    }));
  }
  function prefillReference(e) {
    resetVehicle();
    const form=$('vehicle-form');
    // Empty values deliberately prevent fabricated manufacturer specifications.
    const values={label:e.label,manufacturer:e.manufacturer,model:e.model,energy_code:e.energy_code,
      seats:'',consumption_per_km:'',consumption_per_hour:'0',usable_capacity:'',reserve:'0',
      maintenance_eur_per_km:String((e.maintenance_eur_per_km_ht[0]+e.maintenance_eur_per_km_ht[1])/2),
      purchase_eur:e.purchase_scope==='vehicle'?String((e.purchase_eur_ht[0]+e.purchase_eur_ht[1])/2):'',
      source:t('referenceSource')+' — '+e.model+'; '+e.id+'; prix/maintenance : hypothèses médianes à vérifier.'};
    for(const [key,value] of Object.entries(values)){
      const input=form.elements.namedItem(key); if(input)input.value=value;
    }
    form.querySelector('details.advanced-settings').open=true;
    const note=$('reference-form-note');note.classList.remove('hidden');
    note.textContent=t('referenceComplete')+' '+(e.purchase_scope==='retrofit_kit_installation'?t('referenceRetrofit')+' ':'')+
      (energies.some(x=>x.payload.energy_code===e.energy_code)?'':t('referenceMissingEnergy'));
    form.scrollIntoView({behavior:'smooth',block:'start'});
    form.elements.namedItem('seats').focus({preventScroll:true});
  }
  async function loadReferenceLibrary(){
    try{
      const response=await fetch('/assets/vehicle-reference-catalog.json');
      if(!response.ok)throw new Error(String(response.status));
      const data=await response.json();
      referenceEntries=Array.isArray(data.entries)?data.entries:[];
      renderReferenceLibrary();
    }catch(_){$('reference-library').textContent=t('loadError');}
  }
  function solutionCard(p, vehicle=null) {
    const isDemo = !vehicle;
    const key = isDemo ? '' : esc(vehicle.id);
    const energyName = t(({DIESEL:'diesel', ELECTRIC:'electric', H2:'hydrogen', BIOGNV:'biognv'})[p.energy_code] || 'energy');
    const c100 = number(Number(p.consumption_per_km) * 100, 1);
    const badge = isDemo ? t('demoBadge') : t('unverified');
    const specs = [
      [t('availableSeats'), `${esc(p.seats)}`],
      [t('consumption100'), `${esc(c100)} ${esc(p.unit)}/100 km`],
      [t('tankSize'), `${esc(p.usable_capacity)} ${esc(p.unit)}`],
    ];
    const actions = isDemo
      ? `<button type="button" class="button primary" id="add-demo-vehicle">${esc(t('addDemo'))}</button>`
      : `<button type="button" class="button primary" data-vehicle-simulate="${key}">${esc(t('selectForScenario'))}</button>
         <button type="button" class="button outline" data-vehicle-edit="${key}">${esc(t('revise'))}</button>
         <button type="button" class="table-action" data-vehicle-history="${esc(vehicle.vehicle_key)}">${esc(t('history'))}</button>`;
    return `<article class="solution-card${isDemo ? ' solution-demo' : ''}">
       <header class="solution-header"><div><span class="solution-badge">${esc(badge)}</span>
         <h4>${esc(p.label)}</h4><p class="small muted">${esc(p.manufacturer)} · ${esc(p.model)}</p></div>
         <span class="solution-energy">${esc(energyName)}</span></header>
       ${isDemo ? `<p class="solution-description">${esc(t('demoDescription'))}</p>` : ''}
       <div class="solution-specs">${specs.map(([label,value]) =>
         `<div><small>${esc(label)}</small><strong>${value}</strong></div>`).join('')}</div>
       <p class="solution-source"><strong>${esc(t('vehicleSource'))} :</strong> ${esc(p.source)}</p>
       <div class="solution-actions">${actions}</div>
     </article>`;
  }
  function renderVehicles() {
    const node = $('vehicle-table');
    node.classList.add('solution-list');
    node.innerHTML = vehicles.length
      ? vehicles.map(v => solutionCard(v.payload, v)).join('')
      : solutionCard(demoCoach());
    const addDemo = $('add-demo-vehicle');
    if (addDemo) addDemo.addEventListener('click', async () => {
      addDemo.disabled = true;
      try {
        await api('/vehicles', {method:'POST', body:JSON.stringify(demoCoach())});
        await loadVehicles(); message(t('demoAdded'));
      } catch (error) { message(error.message, true); addDemo.disabled = false; }
    });
    document.querySelectorAll('[data-vehicle-simulate]').forEach(b => b.addEventListener('click', () => {
      selectedVehicleIds.add(b.dataset.vehicleSimulate);
      show('scenarios'); fillScenarioSelects();
    }));
    document.querySelectorAll('[data-vehicle-edit]').forEach(b =>
      b.addEventListener('click', () => editVehicle(b.dataset.vehicleEdit)));
    document.querySelectorAll('[data-vehicle-history]').forEach(b => b.addEventListener('click', async () => {
      try {
        const vs = await api(`/vehicles/${encodeURIComponent(b.dataset.vehicleHistory)}/versions`);
        $('vehicle-history').innerHTML = `<p>${esc(t('internalHistoryNote'))}</p><ul>${vs.map(v =>
          `<li>v${v.revision} · ${esc(v.payload.label)} · ${esc(v.created_at)}</li>`).join('')}</ul>`;
      } catch (error) { message(error.message, true); }
    }));
  }

  function editVehicle(id) {
    $('reference-form-note').classList.add('hidden');
    const v = vehicles.find(v => v.id === id); if (!v) return;
    editingVehicleKey = v.vehicle_key;
    const form = $('vehicle-form');
    for (const [key,value] of Object.entries(v.payload)) {
      const input = form.elements.namedItem(key);
      if (input && typeof value !== 'object') input.value = value;
    }
    $('vehicle-edit-label').textContent = t('editVehicle');
    $('vehicle-cancel').classList.remove('hidden');
    form.scrollIntoView({behavior:'smooth'});
  }
  function resetVehicle() {
    $('reference-form-note').classList.add('hidden');
    editingVehicleKey = null; $('vehicle-form').reset();
    $('vehicle-edit-label').textContent = t('vehicleUnverified');
    $('vehicle-cancel').classList.add('hidden');
  }
  $('vehicle-cancel').addEventListener('click', resetVehicle);
  $('vehicle-form').addEventListener('submit', async event => {
    event.preventDefault(); const d = dataOf(event.currentTarget);
    d.seats = Number(d.seats); d.life_years = Number(d.life_years);
    d.unit = {DIESEL:'L',ELECTRIC:'kWh',H2:'kg',BIOGNV:'kg'}[d.energy_code];
    d.kind = 'bus'; d.quality = 'unverified';
    try {
      const path = editingVehicleKey ? `/vehicles/${encodeURIComponent(editingVehicleKey)}/versions` : '/vehicles';
      await api(path,{method:'POST',body:JSON.stringify(d)});
      resetVehicle(); await loadVehicles(); message(t('createdVersion'));
    } catch(error) {message(error.message,true);}
  });
  $('reload-vehicles').addEventListener('click',loadVehicles);

  function fillScenarioSelects() {
    const list = $('vehicle-compare-options');
    if (!list) return;
    selectedVehicleIds = new Set([...selectedVehicleIds].filter(id => vehicles.some(v => v.id === id)));
    const eligibleForDefault = vehicles.filter(v => energies.some(e => e.payload.energy_code === v.payload.energy_code));
    if (!comparisonSelectionInitialized && eligibleForDefault.length >= 2) {
      eligibleForDefault.slice(0,2).forEach(v => selectedVehicleIds.add(v.id));
      comparisonSelectionInitialized = true;
    }
    list.innerHTML = vehicles.map(v => {
      const e = energies.find(e => e.payload.energy_code === v.payload.energy_code);
      const missing = !e;
      return `<label class="compare-option${missing ? ' compare-option-unavailable' : ''}">
        <input type="checkbox" class="compare-vehicle-checkbox" value="${esc(v.id)}" ${selectedVehicleIds.has(v.id)?'checked':''} ${missing?'disabled':''} />
        <span><strong>${esc(v.payload.label)}</strong><small>${esc(v.payload.seats)} ${esc(t('seatsShort'))} · ${esc(t(({DIESEL:'diesel',ELECTRIC:'electric',H2:'hydrogen',BIOGNV:'biognv'})[v.payload.energy_code] || 'energy'))} · ${missing?esc(t('missingEnergyOption')):esc(e.payload.price_per_unit)+' EUR/'+esc(e.payload.unit)}</small></span>
      </label>`;
    }).join('') || `<p class="empty-state">${esc(t('selectVehicle'))}</p>`;
    list.querySelectorAll('.compare-vehicle-checkbox').forEach(el => el.addEventListener('change', () => {
      if (el.checked) selectedVehicleIds.add(el.value); else selectedVehicleIds.delete(el.value);
    }));
    const eligible = vehicles.filter(v => energies.some(e => e.payload.energy_code === v.payload.energy_code));
    const needed = eligible.length < 2;
    $('catalogue-notice').classList.toggle('hidden', !needed);
    if (needed) $('catalogue-notice').innerHTML = `${esc(t('configureCatalogs'))} <button type="button" class="table-action" data-goto="energy">${esc(t('configureEnergy'))}</button> · <button type="button" class="table-action" data-goto="vehicles">${esc(t('configureVehicle'))}</button>`;
    if (needed && !$('comparison-results').classList.contains('hidden')) return;
    if (needed) compareNotice(t('compareNeedCatalog'));
  }

  function invalidateRoute() {
    currentQuote = null; currentRoute = null;
    $('route-summary').classList.add('hidden');
    if (routeMap) { routeDrawings.forEach(layer => routeMap.removeLayer(layer)); routeDrawings = []; }
    $('route-map-sketch').replaceChildren();
    $('route-map-sketch').classList.add('hidden');
    $('route-map-fallback').classList.add('hidden');
    $('route-status').textContent = t('routeStale');
  }
  $('route-origin').addEventListener('input', invalidateRoute);
  $('route-destination').addEventListener('input', invalidateRoute);
  function renderRouteSummary(route) {
    const node = $('route-summary');
    const km = number(route.distance_m / 1000, 1);
    node.innerHTML = `<strong>${esc(t('routeKilometers'))} : ${esc(km)} km</strong> · <strong>${esc(t('routeDuration'))} : ${esc(routeTime(route.duration_s))}</strong><p>${esc(route.origin)} → ${esc(route.destination)}</p><p class="small muted">${esc(t('routeSource'))}: ${esc(route.provider)} · ${esc(t('routeExternalNotice'))}</p>`;
    if(route.provider === 'osrm_demo') node.innerHTML += `<p class="small warning-text">${esc(t('demoRouting'))}</p>`;
    node.classList.remove('hidden');
  }
  // Map tiles are always clipped by locally served CSS, even if unpkg's CSS is
  // blocked while its JS is available. Observe the size to handle hidden tabs,
  // resize and the narrow desktop/mobile layouts without letting tiles escape.
  const mapObserver = typeof ResizeObserver === 'function'
    ? new ResizeObserver(entries => {
        for (const entry of entries) {
          const map = entry.target.id === 'route-map' ? routeMap : stationsMap;
          if (map && entry.target.offsetWidth && entry.target.offsetHeight)
            requestAnimationFrame(() => map.invalidateSize({pan:false}));
        }
      }) : null;
  function ensureMap(mapId) {
    if (typeof window.L === 'undefined') return null;
    const node = $(mapId);
    if (!node || !node.offsetWidth || !node.offsetHeight) return null;
    try {
      const map = window.L.map(mapId, {scrollWheelZoom:false});
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom:18, attribution:'© OpenStreetMap contributors', crossOrigin:true,
      }).addTo(map);
      mapObserver?.observe(node);
      return map;
    } catch (error) {
      // An unavailable or partially initialized mapping library must never
      // break the rest of the form or mask buttons with loose tile layers.
      node.replaceChildren();
      return null;
    }
  }
  function drawRouteSketch(route) {
    // Draw the actual returned GeoJSON shape without claiming an online basemap.
    // This also works when a browser/proxy blocks the Leaflet CDN.
    const host = $('route-map-sketch');
    host.replaceChildren();
    $('route-map').classList.add('hidden');
    host.classList.remove('hidden');
    $('route-map-fallback').classList.remove('hidden');
    $('route-map-fallback').textContent = t('routeSketchNotice');
    const raw = route.geometry?.type === 'LineString' ? route.geometry.coordinates : [];
    const coords = (raw || []).filter(p=>Array.isArray(p) && p.length>=2 &&
       Number.isFinite(Number(p[0])) && Number.isFinite(Number(p[1])) &&
       Math.abs(Number(p[0]))<=180 && Math.abs(Number(p[1]))<=90);
    if (coords.length < 2) {
      $('route-map-fallback').textContent = t('routeSketchNoData');
      return;
    }
    const NS = 'http://www.w3.org/2000/svg', W = 840, H = 380;
    const svg = document.createElementNS(NS,'svg');
    svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
    svg.setAttribute('role','presentation');
    svg.setAttribute('preserveAspectRatio','xMidYMid meet');
    svg.classList.add('route-sketch-svg');
    const rad = Math.PI/180, lat0 = coords.reduce((sum,p)=>sum+Number(p[1]),0)/coords.length;
    const sx = Math.max(.05,Math.cos(lat0*rad));
    const ll = coords.map(p=>[Number(p[0])*sx, -Number(p[1])]);
    const xMin = Math.min(...ll.map(p=>p[0])), xMax = Math.max(...ll.map(p=>p[0]));
    const yMin = Math.min(...ll.map(p=>p[1])), yMax = Math.max(...ll.map(p=>p[1]));
    const dx = Math.max(0.00001,xMax-xMin), dy = Math.max(0.00001,yMax-yMin);
    const scale = Math.min((W-140)/dx,(H-112)/dy);
    const xOff = (W-dx*scale)/2, yOff = (H-dy*scale)/2;
    const xy = ([x,y])=>[xOff+(x-xMin)*scale,yOff+(y-yMin)*scale];
    const pathData = ll.filter((_,i)=>i===0 || i===ll.length-1 || i%Math.max(1,Math.ceil(ll.length/1000))===0)
      .map((p,i)=>`${i?'L':'M'}${xy(p).map(n=>n.toFixed(1)).join(',')}`).join(' ');
    const add = (parent,tag,attrs,text) => {
      const el=document.createElementNS(NS,tag);
      for(const [key,value] of Object.entries(attrs)) el.setAttribute(key,String(value));
      if(text!==undefined) el.textContent=String(text);
      parent.appendChild(el);return el;
    };
    add(svg,'rect',{width:W,height:H,fill:'#edf5f5'});
    for(let x=70;x<W;x+=70)add(svg,'line',{x1:x,y1:0,x2:x,y2:H,stroke:'#d7e7e8','stroke-width':1});
    for(let y=65;y<H;y+=65)add(svg,'line',{x1:0,y1:y,x2:W,y2:y,stroke:'#d7e7e8','stroke-width':1});
    add(svg,'path',{d:pathData,fill:'none',stroke:'#fff','stroke-width':11,'stroke-linejoin':'round','stroke-linecap':'round'});
    add(svg,'path',{d:pathData,fill:'none',stroke:'#087e8b','stroke-width':6,'stroke-linejoin':'round','stroke-linecap':'round'});
    for(const [p,label,color] of [[ll[0],route.origin,'#138879'],[ll[ll.length-1],route.destination,'#ce6d32']]) {
      const [x,y]=xy(p);add(svg,'circle',{cx:x,cy:y,r:10,fill:color,stroke:'#fff','stroke-width':3});
      add(svg,'text',{x:x+14,y:y-13,fill:'#183244','font-size':17,'font-weight':'700',stroke:'#fff','stroke-width':4,'paint-order':'stroke'},label);
    }
    host.appendChild(svg);
  }
  function showRouteMap(route) {
    if (!route.geometry || route.geometry.type!=='LineString') {
      drawRouteSketch(route);
      return;
    }
    // A previous schematic may have hidden the Leaflet container. Reveal it before measuring.
    $('route-map').classList.remove('hidden');
    if (!routeMap) routeMap = ensureMap('route-map');
    if (!routeMap) { drawRouteSketch(route); return; }
    try {
      $('route-map-sketch').classList.add('hidden');
      $('route-map-fallback').classList.add('hidden');
      $('route-map').classList.remove('hidden');
      routeDrawings.forEach(layer => routeMap.removeLayer(layer));routeDrawings=[];
      const geometry=route.geometry;
      const feature=window.L.geoJSON(geometry,{style:{color:'#0b7f8b',weight:5}}).addTo(routeMap);
      routeDrawings.push(feature);
      for (const [i,[point,label]] of [[route.origin_coordinates,route.origin],[route.destination_coordinates,route.destination]].entries()) {
        if (!point || point.length<2) continue;
        routeDrawings.push(window.L.circleMarker([point[1],point[0]], {
          radius:8,color:'#fff',weight:3,
          fillColor:i===0?'#087e8b':'#ca8137',fillOpacity:1,
        }).bindPopup(esc(label)).addTo(routeMap));
      }
      requestAnimationFrame(()=>{
        if(!routeMap || $('view-scenarios').classList.contains('hidden'))return;
        routeMap.invalidateSize({pan:false});
        const bounds=feature.getBounds();
        if(bounds.isValid())routeMap.fitBounds(bounds.pad(0.14));
      });
    } catch (error) {
      // A mapping rendering issue must never turn a computed route into a blank panel.
      console.warn('Route drawing failed, displaying a geometry-only fallback');
      drawRouteSketch(route);
    }
  }

  $('calculate-route').addEventListener('click',async () => {
    const origin = field($('scenario-form'), 'origin').trim();
    const destination = field($('scenario-form'), 'destination').trim();
    if(origin.length < 2 || destination.length < 2) return message(t('routeRequired'),true);
    invalidateRoute();
    const btn = $('calculate-route'); btn.disabled = true;
    $('route-status').textContent = t('routeLoading');
    try {
      const response = await api('/routing/resolve',{method:'POST',body:JSON.stringify({
        origin,destination,
      })});
      currentQuote = response.quote_id; currentRoute = response.route;
      $('route-status').textContent = t('routeReady');
      renderRouteSummary(currentRoute); showRouteMap(currentRoute);
    } catch(error) { $('route-status').textContent = error.message; message(error.message,true); }
    finally { btn.disabled = false; }
  });

  async function loadScenarios() {
    try { scenarios = await api('/scenarios'); renderScenarios(); }
    catch(error) {message(error.message,true);}
  }
  function renderScenarios() {
    table($('scenario-table'),[t('scenarioName'),t('date'),t('actions')],scenarios.map(s =>
      `<tr><td><strong>${esc(s.name)}</strong></td><td>${esc(s.latest_revision.payload.start_date)}</td><td><button class="table-action" data-scenario-run="${esc(s.latest_revision.id)}">${esc(t('run'))}</button></td></tr>`));
    document.querySelectorAll('[data-scenario-run]').forEach(b => b.addEventListener('click',()=>runScenario(b.dataset.scenarioRun)));
  }
  async function runScenario(revisionId) {
    try {
      const run = await api('/runs',{method:'POST',body:JSON.stringify({scenario_revision_id:revisionId})});
      await loadRuns(); show('scenarios'); showResult(run);
      message(t('runSaved'));
    } catch(error) {message(error.message,true);}
  }
  async function loadComparisons() {
    try { comparisons = await api('/comparisons'); renderComparisonHistory(); }
    catch (error) { message(error.message, true); }
  }
  function renderComparisonHistory() {
    const el = $('comparison-history');
    if (!el) return;
    el.innerHTML = comparisons.length ? comparisons.map(c =>
      `<button type="button" class="comparison-link" data-comparison="${esc(c.id)}"><strong>${esc(c.name)}</strong><small>${esc(c.count)} ${esc(t('vehicle'))} · ${esc(c.created_at.slice(0,10))}</small></button>`).join('')
      : `<p class="empty-state">${esc(t('compareUnavailable'))}</p>`;
    el.querySelectorAll('[data-comparison]').forEach(el => el.addEventListener('click',async()=>{
      try { const data = await api(`/comparisons/${encodeURIComponent(el.dataset.comparison)}`);
        show('scenarios'); showComparison(data); }
      catch(err) { message(err.message,true); }
    }));
  }
  function showComparison(comparison, scroll=true) {
    currentComparison = comparison;
    const root = $('comparison-results');
    const shared = comparison.shared;
    const headers = ['compareVehicle','compareEnergy','compareFeasibility','vehiclesUsed','compareCost','compareEmissions','comparePerPassenger','compareConsumption','comparePdf'];
    // Cost-based indicative selection among the *feasible computed cases*.
    // Neither this ranking nor the day heuristic proves a global optimum.
    const feasible = comparison.entries.filter(e=>e.result.status==='feasible_not_proven'
      && e.result.totals && Number.isFinite(Number(e.result.totals.eur_total)));
    feasible.sort((a,b)=>Number(a.result.totals.eur_total)-Number(b.result.totals.eur_total)
      || Number(a.result.totals.vehicles_used)-Number(b.result.totals.vehicles_used));
    const cheapest = feasible.length ? feasible[0].run_id : null;
    root.innerHTML = `<div class="result-hero"><div><div class="eyebrow">${esc(t('compareResultsTitle'))}</div><h3>${esc(comparison.name)}</h3>
      <p>${esc(shared.route.origin)} → ${esc(shared.route.destination)} · ${esc(number(shared.route.distance_m/1000,1))} km · ${esc(shared.passengers)} ${esc(t('passengers'))}</p>
      <p class="small muted">${esc(t('compareSameInputs'))} SHA-256 ${esc(comparison.shared_sha256.slice(0,16))}…</p></div></div>
      <div class="table-wrap comparison-table"><table><thead><tr>${headers.map(key=>`<th>${esc(t(key))}</th>`).join('')}</tr></thead><tbody>
      ${comparison.entries.map(entry=>{
        const result=entry.result, total=result.totals, vehicle=entry.vehicle_version.payload, energy=entry.energy_version.payload;
        const valid = !!total && result.status==='feasible_not_proven';
        const detail=valid?t('compareStatus'):t(`status_${result.status}`);
        const warn=!valid?`<small>${esc((result.constraints||[]).map(x=>translatedEngineMessage(x.message)).join(' · '))}</small>`:'';
        return `<tr><td><strong>${esc(vehicle.label)}</strong><small>${esc(vehicle.seats)} ${esc(t('seatsShort'))}</small>${cheapest===entry.run_id?`<small class="compare-good">${esc(t('bestIndicative'))}</small>`:''}</td>
          <td>${esc(energy.energy_code)}<small>${esc(energy.price_per_unit)} EUR/${esc(energy.unit)}</small></td>
          <td><span class="${valid?'compare-good':'compare-bad'}">${esc(detail)}</span>${warn}</td>
          <td>${valid?esc(total.vehicles_used):'—'}</td>
          <td>${valid?esc(number(total.eur_total,2))+' €':'—'}</td>
          <td>${valid && total.kgco2e_total!==null?esc(number(total.kgco2e_total,2))+' kg':'—'}</td>
          <td>${valid && total.kgco2e_per_passenger!==null?esc(number(total.kgco2e_per_passenger,3))+' kg':'—'}</td>
          <td>${valid?esc(number(total.energy_consumed,2))+' '+esc(total.energy_unit):'—'}</td>
          <td><button type="button" class="button outline" data-compare-pdf="${esc(entry.run_id)}">PDF</button></td></tr>`;
      }).join('')}</tbody></table></div>
      <p class="small warning-text">${esc(t('compareReadOnly'))}</p>${scheduleTiles(comparison)}`;
    if (shared.day_plan && shared.day_station_policy === 'automatic') {
      const notes = (shared.day_station_search_warnings || []).filter(Boolean);
      root.insertAdjacentHTML('beforeend', `<p class="small muted">${esc(t('stationAutoExplanation'))}</p>`+
        (notes.length ? `<details class="small"><summary>${esc(t('stationSearchLimits'))}</summary><ul>`+
          notes.map(n=>`<li>${esc(n)}</li>`).join('')+`</ul></details>` : ''));
    }
    root.classList.remove('hidden'); $('result-detail').classList.add('hidden');
    root.querySelectorAll('[data-compare-pdf]').forEach(b=>b.addEventListener('click',()=>downloadPdf(b.dataset.comparePdf)));
    if (scroll) root.scrollIntoView({behavior:'smooth',block:'start'});
  }
  function selectedStationData(s) {
    return {id:String(s.id),name:String(s.name),longitude:Number(s.longitude),
      latitude:Number(s.latitude),energy_codes:(s.energy_codes||[]).map(e=>e==='Gazole'?'DIESEL':e),
      source:String(s.source||'Selected from user directory')};
  }
  function updatePlannedStation() {
    const label = $('day-station-name');
    if (label) label.textContent = plannedStation ? plannedStation.name : t('noRefuelStation');
  }
  function updateStationPolicy() {
    $('day-station-manual').classList.toggle('hidden', $('station-policy').value !== 'imposed');
  }
  $('station-policy').addEventListener('change', updateStationPolicy);
  $('day-plan-enabled').addEventListener('change', () => {
    $('day-plan-details').classList.toggle('hidden', !$('day-plan-enabled').checked);
  });
  $('day-plan-select-station').addEventListener('click', () => {
    show('stations'); message(t('dayRefuelGuide'));
  });
  $('day-plan-remove-station').addEventListener('click', () => {
    plannedStation = null; $('station-policy').value='automatic';
    updatePlannedStation(); updateStationPolicy();
  });
  function timelineRows(entry) {
    const result = entry.result;
    if(Array.isArray(result.vehicles) && result.vehicles.length) return result.vehicles;
    // Historic/simple simulations: a single passenger run per coach, not a fabricated rotation.
    const buckets = new Map();
    for(const trip of (result.trips || [])) {
      if (!buckets.has(trip.vehicle_instance)) buckets.set(trip.vehicle_instance, []);
      const begin = Date.parse(trip.depart_utc), end = Date.parse(trip.arrive_utc);
      buckets.get(trip.vehicle_instance).push({kind:'service',start_utc:trip.depart_utc,
        end_utc:trip.arrive_utc,duration_s:String((end-begin)/1000),
        distance_m:trip.distance_m,energy_used:trip.energy_used});
    }
    return [...buckets].map(([vehicle_instance,events])=>({vehicle_instance,events,
      active_duration_s:String(events.reduce((sum,e)=>sum+Number(e.duration_s||0),0))}));
  }
  function eventLabel(kind) {
    return t(({service:'dayService',deadhead_return:'dayDeadhead',station_detour:'dayDetour',
      refuel:'dayRefuel',handling:'dayHandling'})[kind]||'dayService');
  }
  function localTime(iso) {
    const date = new Date(iso);
    return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat(language==='fr'?'fr-FR':'en-GB',
      {hour:'2-digit',minute:'2-digit',timeZone:'Europe/Paris'}).format(date);
  }
  function scheduleTiles(comparison) {
    const isPlan = !!comparison.shared.day_plan;
    return `<div class="day-solution-section"><h3>${esc(t('dayTileTitle'))}</h3>
      <p class="small warning-text">${esc(t(isPlan?'dayPlanUnverified':'dayBasicNotice'))}</p>
      <div class="day-solutions">${comparison.entries.map(entry=>{
        const result = entry.result, total=result.totals, vehicle=entry.vehicle_version.payload;
        const buses=timelineRows(entry);
        const allEvents=buses.flatMap(bus=>bus.events||[]);
        const firstTime=Math.min(...allEvents.map(e=>Date.parse(e.start_utc)));
        const lastTime=Math.max(...allEvents.map(e=>Date.parse(e.end_utc)));
        const simpleElapsed=allEvents.length ? (lastTime-firstTime)/1000 : 0;
        const simpleVehicleTime=allEvents.reduce((sum,e)=>sum+Number(e.duration_s||0),0);
        return `<article class="day-solution-card">
          <div class="day-solution-head"><div><h4>${esc(vehicle.label)}</h4>
          <small>${esc(vehicle.seats)} ${esc(t('seatsShort'))} · ${esc(vehicle.energy_code)}</small></div>
          <strong class="${total?'compare-good':'compare-bad'}">${esc(total?t('compareStatus'):(t('status_'+result.status)))}</strong></div>
          ${total?`<div class="day-solution-metrics">
            <div><small>${esc(t('dayTimeTotal'))}</small><strong>${esc(routeTime(Number(total.duration_elapsed_s??simpleElapsed)))}</strong></div>
            <div><small>${esc(t('dayVehicleTime'))}</small><strong>${esc(routeTime(Number(total.duration_vehicle_s??simpleVehicleTime)))}</strong></div>
            <div><small>${esc(t('dayFuelStops'))}</small><strong>${esc(total.refuel_count||0)}</strong></div>
            <div><small>${esc(t('dayRotations'))}</small><strong>${esc(total.trips||0)}</strong></div>
            <div><small>${esc(t('compareCost'))}</small><strong>${esc(number(total.eur_total,2))} €</strong></div>
            <div><small>${esc(t('compareEmissions'))}</small><strong>${total.kgco2e_total===null?'—':esc(number(total.kgco2e_total,2))+' kg'}</strong></div>
          </div>
          ${buses.map((bus,i)=>`<details class="day-bus" ${i===0?'open':''}><summary>${esc(t('dayVehicleNumber'))} ${esc(bus.vehicle_instance)} · ${esc(routeTime(Number(bus.active_duration_s)))} · ${esc((bus.events||[]).filter(e=>e.kind==='service').length)} ${esc(t('dayRotations').toLowerCase())}</summary>
           <ol class="day-events">${(bus.events||[]).map(e=>`<li>
             <span class="day-event-time">${esc(localTime(e.start_utc))} – ${esc(localTime(e.end_utc))}</span>
             <div><strong>${esc(eventLabel(e.kind))}</strong><small>${esc(routeTime(Number(e.duration_s)))}`+
                `${Number(e.distance_m)?' · '+esc(number(Number(e.distance_m)/1000,1))+' km':''}`+
                `${e.kind==='refuel'?' · +'+esc(number(e.energy_added,2))+' '+esc(vehicle.unit):''}`+
                `${e.station_name?' · '+esc(e.station_name):''}</small></div>
             </li>`).join('')}</ol></details>`).join('')}
          ${isPlan?`<p class="small muted">${esc(t('dayWaiting'))}: <strong>0 min</strong></p>`:''}`
          :`<p class="warning-text">${esc(t('dayNoSchedule'))} ${esc((result.constraints||[]).map(c=>translatedEngineMessage(c.message)).join(' · '))}</p>`}
          <button type="button" class="button outline" data-compare-pdf="${esc(entry.run_id)}">${esc(t('downloadPDF'))}</button>
        </article>`;
      }).join('')}</div></div>`;
  }
  function selectedComparableIds() {
    return [...selectedVehicleIds].filter(id => {
      const v=vehicles.find(v=>v.id===id);
      return v && energies.some(e=>e.payload.energy_code===v.payload.energy_code);
    });
  }
  function comparePreflight() {
    if (selectedComparableIds().length<2) {
      compareProblem(t('compareNeedCatalog'));
      return false;
    }
    if (!currentQuote) {
      compareProblem(t('compareNeedRoute'));
      return false;
    }
    if ($('day-plan-enabled').checked && $('station-policy').value==='imposed') {
      if (!plannedStation) { compareProblem(t('stationRequired')); return false; }
      const fuels=new Set(plannedStation.energy_codes);
      const chosen=selectedComparableIds().map(id=>vehicles.find(v=>v.id===id)?.payload.energy_code);
      if (!chosen.some(x=>fuels.has(x))) { compareProblem(t('stationIncompatible')); return false; }
    }
    const form=$('scenario-form');
    const invalid=form.querySelector(':invalid');
    if (invalid) {
      const details=invalid.closest('details');
      if (details)details.open=true;
      const label=invalid.closest('label')?.querySelector('span')?.textContent || invalid.name;
      compareProblem(t('compareInvalidField')+label);
      return false;
    }
    compareNotice('');
    return true;
  }
  $('scenario-submit').addEventListener('click', event=>{
    if(!comparePreflight())event.preventDefault();
  });
  $('scenario-form').addEventListener('invalid', event=>{
    const details=event.target.closest('details');
    if(details)details.open=true;
    const label=event.target.closest('label')?.querySelector('span')?.textContent || event.target.name;
    compareProblem(t('compareInvalidField')+label);
  },true);
  $('scenario-form').addEventListener('submit', async event => {
    event.preventDefault(); const d = dataOf(event.currentTarget);
    if (!comparePreflight()) return;
    const ids=selectedComparableIds();
    const body={name:d.name,route_quote_id:currentQuote,vehicle_version_ids:ids,
      country_iso:'FR',start_date:d.start_date,passengers:Number(d.passengers),
      window_start:d.window_start,window_end:d.window_end,max_vehicles:Number(d.max_vehicles),
      tco_scope:d.tco_scope,emission_scope:d.emission_scope,infrastructure_daily_eur:d.infrastructure_daily_eur,
      day_plan:$('day-plan-enabled').checked};
    if(body.day_plan) {
      body.station_policy=$('station-policy').value;
      body.refuel_station=body.station_policy==='imposed' ? plannedStation : null;
      body.diesel_flow_l_per_min=String(d.diesel_flow_l_per_min||'0').replace(',','.');
      body.hydrogen_flow_kg_per_min=String(d.hydrogen_flow_kg_per_min||'0').replace(',','.');
      body.handling_minutes=String(d.handling_minutes||'0').replace(',','.');
    }
    const btn=$('scenario-submit'); btn.disabled=true;
    compareNotice(t('compareRunning'),false);
    try {
      const result=await api('/comparisons',{method:'POST',body:JSON.stringify(body)});
      showComparison(result);
      compareNotice(t('compareDone'),false);
      await loadComparisons(); await loadScenarios(); await loadRuns();
      message(t('runSaved'));
    } catch(err) { compareProblem(t('compareFailed')+err.message); }
    finally { btn.disabled=false; }
  });

  async function loadRuns() {
    try { runs = await api('/runs'); renderRuns(); }
    catch(error) {message(error.message,true);}
  }
  function renderRuns() {
    table($('runs-table'),[t('scenarioName'),t('estimatedTco'),t('actions')],runs.map(r => {
      const totals = r.result.totals || {};
      return `<tr><td>${esc(r.snapshot.scenario.name)}<small>${esc(r.created_at.slice(0,10))}</small></td><td>${esc(totals.eur_total ?? '—')} €</td><td><button class="table-action" data-run-detail="${esc(r.id)}">${esc(t('view'))}</button> <button class="table-action" data-run-pdf="${esc(r.id)}">PDF</button></td></tr>`;
    }));
    document.querySelectorAll('[data-run-detail]').forEach(b => b.addEventListener('click',()=>{
      show('scenarios'); showResult(runs.find(r=>r.id===b.dataset.runDetail));
    }));
    document.querySelectorAll('[data-run-pdf]').forEach(b => b.addEventListener('click',()=>downloadPdf(b.dataset.runPdf)));
  }
  // Les avertissements de calcul sont conservés in extenso pour l'audit ;
  // les libellés courants sont traduits dans la langue de l'utilisateur.
  const engineMessages = {
    'PROTOTYPE : monoligne, 1 jour, aucune réutilisation de véhicule.':'Prototype: one route, one day, no vehicle reuse.',
    'Aucun détour, retour dépôt, temps de pause ou recharge pris en charge.':'No detours, return to depot, driver rest or charging included.',
    "Aucune minimisation du coût n'est prouvée : affectation baseline seulement.":'Cost minimization is not proven: baseline assignment only.',
    'Tarifs et facteurs sont des hypothèses non vérifiées ; pas des données nationales officielles.':'Prices and factors are unverified assumptions; not official national values.',
    'Données de véhicule non vérifiées.':'Vehicle data is unverified.',
    "TCO complet limité aux postes saisis, sans coût d'exploitation non paramétré.":'Full TCO limited to entered costs; other costs excluded.',
    "Distance/durée déclarées par l'utilisateur, non vérifiées par routage.":'User-provided route distance and duration not validated by routing.',
    "Données de véhicule non vérifiées.":'Vehicle data is unverified.',
  };
  function translatedEngineMessage(s) { return language === 'en' ? (engineMessages[s] || s) : s; }
  function showResult(run, scroll=true) {
    if(!run) return;
    currentRun = run;
    const node = $('result-detail'), result = run.result, totals = result.totals;
    const header = `<div class="result-hero"><div><div class="eyebrow">${esc(t('resultTitle'))}</div><h3>${esc(run.snapshot.scenario.name)}</h3><p>${esc(t('status'))}: <strong>${esc(t(`status_${run.status}`) === `status_${run.status}` ? run.status : t(`status_${run.status}`))}</strong><br><small>SHA-256 ${esc(run.snapshot_sha256.slice(0,24))}…</small></p></div><button type="button" class="button primary" id="pdf-current">${esc(t('downloadPDF'))} ↓</button></div>`;
    if (!totals) {
      node.innerHTML = header + `<p class="warning-text">${esc(t('noResult'))} ${esc((result.constraints||[]).map(x=>translatedEngineMessage(x.message)).join(' · '))}</p>`;
    } else {
      const indicators = [[t('estimatedTco'),`${totals.eur_total} EUR`],[t('emissions'),`${totals.kgco2e_total} kg CO₂e`],
        [t('served'),totals.passengers_served],[t('vehiclesUsed'),totals.vehicles_used]];
      node.innerHTML = header + `<div class="kpi-grid">${indicators.map(([k,v])=>`<div class="kpi"><small>${esc(k)}</small><strong>${esc(v)}</strong></div>`).join('')}</div>
        <p>${esc(t('energyConsumed'))}: ${esc(totals.energy_consumed)} ${esc(totals.energy_unit)} · ${esc(t('passengerKm'))}: ${esc(totals.passenger_km)}</p>
        <h3>${esc(t('tripList'))}</h3><div class="table-wrap"><table><thead><tr>${[t('trip'),t('vehicle'),t('departureUTC'),t('passengers'),t('consumption')].map(s=>`<th>${esc(s)}</th>`).join('')}</tr></thead><tbody>
        ${(result.trips || []).map(trip=>`<tr><td>${esc(trip.trip_id)}</td><td>${esc(trip.vehicle_instance)}</td><td>${esc(trip.depart_utc)}</td><td>${esc(trip.passengers)}</td><td>${esc(trip.energy_used)}</td></tr>`).join('')}</tbody></table></div>
        <h3>${esc(t('technicalLimits'))}</h3><ul class="result-list">${(result.warnings || []).map(s=>`<li>${esc(translatedEngineMessage(s))}</li>`).join('')}</ul>`;
      if (language === 'en' && (result.warnings || []).some(s=>!engineMessages[s])) node.innerHTML += `<p class="small muted">${esc(t('engineInFrench'))}</p>`;
    }
    node.classList.remove('hidden'); $('pdf-current').addEventListener('click',()=>downloadPdf(run.id));
    if (scroll) node.scrollIntoView({behavior:'smooth',block:'start'});
  }
  async function downloadPdf(id) {
    try {
      const response = await api(`/runs/${encodeURIComponent(id)}/report.pdf?lang=${language}`,{raw:true});
      const blob = await response.blob(), url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download=`simulation-${id}.pdf`;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(()=>URL.revokeObjectURL(url),5000);
    } catch(error) { message(`${t('pdfError')} ${error.message}`,true); }
  }

  function normalizeManualStation(station) {
    const p = station.payload;
    return {id:station.id,name:p.name,city:'',address:'',longitude:Number(p.longitude),
      latitude:Number(p.latitude),category:'manual',energy_codes:p.equipments.map(e=>e.energy_code),
      operational_status:'unverified',source:p.source,notice:t('stationCaution')};
  }
  // First 100 places become visible immediately, then automatically fetch the other
  // pages for the selected department scope. The page counter always refers to loaded
  // data, never an invented region-wide number. Keep the manual load-more fallback.
  async function loadStations() {
    if (stationLoading) return;
    stationLoading = true;
    const area = $('station-area').value;
    try {
      const [manual,data] = await Promise.all([
        api('/stations'), api(`/stations/discovery?area=${encodeURIComponent(area)}&offset=0&limit=100`),
      ]);
      customStations=manual; h2Stations=data.hydrogen;
      fuelStations=data.fuel.stations; fuelPage=data.fuel;
      stationSelection=null;$('station-details').classList.add('hidden');
      renderStations();
      let pages=0;
      while (fuelPage.has_more && !fuelPage.unavailable && pages<9 && $('station-area').value===area) {
        const nextOffset=fuelPage.offset+fuelPage.limit;
        const next=await api(`/stations/discovery?area=${encodeURIComponent(area)}&offset=${nextOffset}&limit=100`);
        if (next.fuel.unavailable) { fuelPage={...fuelPage,unavailable:true};break; }
        fuelStations.push(...next.fuel.stations);fuelPage=next.fuel;pages++;
        renderStations();
      }
      renderStations();
    } catch(error) { message(error.message,true); }
    finally {
      stationLoading=false;
      if ($('station-area').value!==area) loadStations();
    }
  }
  $('reload-stations').addEventListener('click',loadStations);
  $('station-area').addEventListener('change',()=>loadStations());
  for(const id of ['station-filter-h2','station-filter-petrol','station-filter-diesel','station-filter-manual'])
    $(id).addEventListener('change',renderStations);
  $('more-stations').addEventListener('click',async () => {
    if (!fuelPage?.has_more || stationLoading) return;
    stationLoading=true;
    try {
      const offset=fuelPage.offset+fuelPage.limit;
      const area=$('station-area').value;
      const data=await api(`/stations/discovery?area=${encodeURIComponent(area)}&offset=${offset}&limit=100`);
      if (data.fuel.unavailable) fuelPage={...fuelPage,unavailable:true};
      else { fuelStations.push(...data.fuel.stations);fuelPage=data.fuel; }
      renderStations();
    } catch(error) { message(error.message,true); }
    finally { stationLoading=false; }
  });
  const petrolCodes=new Set(['SP95','SP98','E10','E85','GPLc']);
  let stationSelection=null;
  let stationMarkers=new Map();
  function stationHasDiesel(s){return s.category==='fuel' && (s.energy_codes||[]).includes('Gazole');}
  function stationHasPetrol(s){return s.category==='fuel' && (s.energy_codes||[]).some(x=>petrolCodes.has(x));}
  function stationVisible(s) {
    if(s.category==='hydrogen') return $('station-filter-h2').checked;
    if(s.category==='manual') return $('station-filter-manual').checked;
    if(s.category!=='fuel')return false;
    const fuels=s.energy_codes||[];
    // Unknown fuel categories are shown when either fuel filter is enabled, not invented as both.
    if(!fuels.length) return false; // Never present an unknown fuel as petrol or diesel.
    return ($('station-filter-petrol').checked&&stationHasPetrol(s))||
      ($('station-filter-diesel').checked&&stationHasDiesel(s));
  }
  function stationType(s) {
    if(s.category==='hydrogen')return t('hydrogenBadge');
    if(s.category==='manual')return t('manualBadge');
    const kinds=[];
    if(stationHasPetrol(s))kinds.push(t('petrolBadge'));
    if(stationHasDiesel(s))kinds.push(t('dieselBadge'));
    return kinds.join(' / ') || t('fuelBadge');
  }
  function stationPopupHtml(s) {
    const url=safeUrl(s.source);
    const fuelList=(s.energy_codes||[]).join(', ') || t('stationUnknown');
    const pressure=s.category==='hydrogen'&&s.pressure_bar?`<p><strong>${esc(t('stationPressure'))}:</strong> ${esc(s.pressure_bar)} bar</p>`:'';
    const lane=s.category==='fuel'&&s.heavy_vehicle_lane_reported
      ? `<p><strong>${esc(t('stationHeavyLane'))}:</strong> ${esc(t('stationYes'))}</p>` : '';
    const pump=s.category==='fuel'&&s.automatic_24h_reported
      ? `<p><strong>${esc(t('station24h'))}:</strong> ${esc(t('stationYes'))}</p>` : '';
    const update=s.source_updated_at?`<p><strong>${esc(t('stationLastUpdate'))}:</strong> ${esc(s.source_updated_at)}</p>`:'';
    const services=Array.isArray(s.fuel_services)&&s.fuel_services.length
      ? `<p><strong>${esc(t('stationServices'))}:</strong> ${esc(s.fuel_services.join(', '))}</p>` : '';
    return `<div class="station-popup"><strong>${esc(s.name)}</strong>
      <p>${esc(s.address||s.city||t('stationUnknown'))}</p>
      <p><strong>${esc(t('stationEnergy'))}:</strong> ${esc(fuelList)}</p>${pressure}${lane}${pump}${update}${services}
      <p><strong>${esc(t('stationCompatibility'))}:</strong> ${esc(t('stationUnknown'))}</p>
      <p class="small">${esc(t('stationNoPrice'))}</p>
      ${url?`<a href="${esc(url)}" target="_blank" rel="noopener">${esc(t('sourceLink'))} ↗</a>`:esc(s.source||'')}
      </div>`;
  }
  function baseMarkerRadius(marker) {
    return marker.options.stationBaseRadius || 6;
  }
  function emphasizeMarker(id, openPopup=true) {
    const marker=stationMarkers.get(id);
    if (!marker) return;
    marker.setRadius(baseMarkerRadius(marker)*1.7);
    marker.setStyle({weight:4,fillOpacity:1});
    marker.bringToFront();
    if(openPopup) marker.openPopup();
  }
  function restoreMarker(id) {
    const marker=stationMarkers.get(id);
    if (!marker || id===stationSelection) return;
    marker.setRadius(baseMarkerRadius(marker));
    marker.setStyle({weight:2,fillOpacity:.8});
    marker.closePopup();
  }
  function selectStation(id, openMap=true) {
    const previous=stationSelection;
    stationSelection=id;
    if(previous && previous!==id) {
      // A previously selected marker is no longer sticky after choosing another.
      stationSelection=null;restoreMarker(previous);stationSelection=id;
    }
    const s=[...h2Stations,...fuelStations,...customStations.map(normalizeManualStation)].find(x=>x.id===id);
    if(!s)return;
    document.querySelectorAll('[data-station-id]').forEach(el=>el.classList.toggle('active',el.dataset.stationId===id));
    $('station-details').innerHTML=`<h4>${esc(t('stationDetailsTitle'))}</h4>${stationPopupHtml(s)}
      <button type="button" class="button outline" id="use-station-day-plan">${esc(t('useForRefuel'))}</button>`;
    $('station-details').classList.remove('hidden');
    $('use-station-day-plan').addEventListener('click', () => {
      plannedStation=selectedStationData(s); updatePlannedStation();
      $('day-plan-enabled').checked=true; $('day-plan-details').classList.remove('hidden');
      $('station-policy').value='imposed'; updateStationPolicy();
      show('scenarios'); message(t('stationChosen'));
    });
    const marker=stationMarkers.get(id);
    if(marker) {
      if (openMap&&stationsMap) stationsMap.panTo(marker.getLatLng());
      emphasizeMarker(id,true);
    }
  }
  function renderStations() {
    if (!$('station-list')) return;
    const all=[...h2Stations,...fuelStations,...customStations.map(normalizeManualStation)];
    const filtered=all.filter(stationVisible);
    $('station-count-h2').textContent=`(${all.filter(s=>s.category==='hydrogen').length})`;
    $('station-count-petrol').textContent=`(${all.filter(stationHasPetrol).length})`;
    $('station-count-diesel').textContent=`(${all.filter(stationHasDiesel).length})`;
    $('station-count-manual').textContent=`(${all.filter(s=>s.category==='manual').length})`;
    $('station-counter').textContent=`${filtered.length} ${t('recordedLocations')}`;
    $('station-list-count').textContent=filtered.length;
    $('station-data-status').textContent= fuelPage?.unavailable ? t('fuelUnavailable') :
      fuelPage?.has_more ? `${t('fuelPartial')} ${fuelStations.length}/${fuelPage.total}` : '';
    $('more-stations').classList.toggle('hidden',!fuelPage?.has_more ||
      (!$('station-filter-petrol').checked&&!$('station-filter-diesel').checked));
    $('station-list').innerHTML=filtered.map(s=>`<button type="button" class="station-card${s.id===stationSelection?' active':''}" data-station-id="${esc(s.id)}" aria-label="${esc(t('stationChoose'))}: ${esc(s.name)}">
        <span class="station-type ${esc(s.category)}">${esc(stationType(s))}</span>
        <strong>${esc(s.name)}</strong><small>${esc(s.address||s.city||t('stationUnknown'))}</small>
        <small>${esc(s.category==='hydrogen'?t('h2Disclaimer'):s.category==='fuel'?t('fuelDisclaimer'):t('unverified'))}</small>
      </button>`).join('') || `<div class="empty-state">${esc(t('stationNoData'))}</div>`;
    for(const b of $('station-list').querySelectorAll('[data-station-id]')) {
      b.addEventListener('click',()=>selectStation(b.dataset.stationId));
      b.addEventListener('mouseenter',()=>emphasizeMarker(b.dataset.stationId,true));
      b.addEventListener('mouseleave',()=>restoreMarker(b.dataset.stationId));
      b.addEventListener('focus',()=>emphasizeMarker(b.dataset.stationId,true));
      b.addEventListener('blur',()=>restoreMarker(b.dataset.stationId));
    }
    if(stationSelection&&!filtered.some(s=>s.id===stationSelection)){
      stationSelection=null;$('station-details').classList.add('hidden');
    }else if(stationSelection)selectStation(stationSelection,false);
    if ($('view-stations').classList.contains('hidden')) return;
    if(!stationsMap) stationsMap=ensureMap('station-map');
    $('station-map-fallback').classList.toggle('hidden',!!stationsMap);
    $('station-map').classList.toggle('hidden', !stationsMap);
    if(!stationsMap) return;
    stationDrawings.forEach(layer=>stationsMap.removeLayer(layer));stationDrawings=[];stationMarkers.clear();
    const positions=[];
    for(const s of filtered) {
      if(!Number.isFinite(Number(s.latitude)) || !Number.isFinite(Number(s.longitude))) continue;
      const point=[Number(s.latitude), Number(s.longitude)];
      const radius=s.category==='hydrogen'?8:6;
      const marker=window.L.circleMarker(point,{radius,stationBaseRadius:radius,
        color:s.category==='hydrogen'?'#087e8b':s.category==='fuel'?'#248455':'#586577',weight:2,fillOpacity:.8})
        .bindPopup(stationPopupHtml(s))
        .on('mouseover',()=>emphasizeMarker(s.id,true))
        .on('mouseout',()=>restoreMarker(s.id))
        .on('click',()=>selectStation(s.id,false))
        .addTo(stationsMap);
      stationDrawings.push(marker);stationMarkers.set(s.id,marker);positions.push(point);
    }
    if (stationSelection) emphasizeMarker(stationSelection,false);
    requestAnimationFrame(() => {
      if (!stationsMap || $('view-stations').classList.contains('hidden')) return;
      stationsMap.invalidateSize({pan:false});
      if (positions.length) stationsMap.fitBounds(window.L.latLngBounds(positions).pad(0.1),{maxZoom:11});
      else stationsMap.setView([49.12,0.25],7);
    });
  }
  $('station-form').addEventListener('submit',async event => {
    event.preventDefault();const d=dataOf(event.currentTarget);
    const payload={name:d.name,longitude:Number(d.longitude),latitude:Number(d.latitude),access:d.access,
      operational_status:'unverified',confidence:'unverified',equipments:[{energy_code:d.energy_code,connector:d.connector,ports:Number(d.ports)}],
      source:d.source,observed_at:d.observed_at};
    try { await api('/stations',{method:'POST',body:JSON.stringify(payload)});
      await loadStations();message(t('savedUnverified')); }
    catch(error) {message(error.message,true);}
  });

  const routingProfiles = {
    geoapify:[['bus','profileBus'],['truck','profileTruck'],['heavy_truck','profileHeavy']],
    ors:[['driving-hgv','profileHgv'],['driving-car','profileCar']],
    osrm_demo:[['driving-car','profileCar']],
  };
  function routingProfileOptions() {
    const provider = $('routing-provider').value;
    const previous = $('routing-profile').value;
    $('routing-profile').innerHTML = (routingProfiles[provider] || []).map(([v,label]) =>
      `<option value="${esc(v)}">${esc(t(label))}</option>`).join('');
    if ((routingProfiles[provider] || []).some(([v]) => v === previous)) $('routing-profile').value = previous;
  }
  $('routing-provider').addEventListener('change',routingProfileOptions);
  async function loadRoutingConfig() {
    try { routingConfig = await api('/routing/config'); renderRoutingConfig(); }
    catch(error) {message(error.message,true);}
  }
  function renderRoutingConfig() {
    if (!routingConfig) return;
    const p = routingConfig;
    $('routing-provider-label').textContent = p.provider;
    $('routing-profile-label').textContent = p.profile || '—';
    $('routing-endpoint-label').textContent = p.endpoint || '—';
    $('routing-geo-status').textContent = p.configured.geoapify ? t('keySaved') : t('keyMissing');
    $('routing-ors-status').textContent = p.configured.ors ? t('keySaved') : t('keyMissing');
    $('routing-availability').textContent = p.available ? t('routingReady') : t('routingNotReady');
    $('routing-config-form').classList.toggle('hidden',!p.modifiable);
    $('routing-key-controls').classList.toggle('hidden',!p.operator);
    $('routing-operator-notice').classList.toggle('hidden',!!p.operator);
    if (p.provider in routingProfiles) {
      $('routing-provider').value=p.provider;
      routingProfileOptions(); $('routing-profile').value=p.profile;
    }
  }
  $('reload-routing').addEventListener('click',loadRoutingConfig);
  $('routing-config-form').addEventListener('submit',async event=>{
    event.preventDefault();
    try { routingConfig=await api('/routing/config',{method:'POST',body:JSON.stringify(dataOf(event.currentTarget))});
      renderRoutingConfig();message(t('providerSaved'));
    } catch(error) {message(error.message,true);}
  });
  for (const provider of ['geoapify','ors']) {
    $(`${provider}-key-form`).addEventListener('submit',async event=>{
      event.preventDefault(); const input=event.currentTarget.elements.namedItem('key');
      const key=input.value;input.value='';
      try { routingConfig=await api('/routing/keys',{method:'POST',body:JSON.stringify({provider,key})});
        renderRoutingConfig();message(t('keySaved'));
      } catch(error) {message(error.message,true);}
    });
    $(`remove-${provider}-key`).addEventListener('click',async()=>{
      try { routingConfig=await api(`/routing/keys/${provider}`,{method:'DELETE'});
        renderRoutingConfig();message(t('keyRemoved'));
      } catch(error) {message(error.message,true);}
    });
  }
  $('routing-test-form').addEventListener('submit',async event=>{
    event.preventDefault();const data=dataOf(event.currentTarget);
    const coord=value=>value.split(',').map(v=>Number(v.trim()));
    const origin=coord(data.origin),destination=coord(data.destination);
    if(origin.length!==2 || destination.length!==2 || ![...origin,...destination].every(Number.isFinite))
      return message('Invalid coordinates',true);
    try { const result=await api('/routing/test',{method:'POST',body:JSON.stringify({origin,destination})});
      $('routing-test-result').textContent=`${t('testRouteResult')} · ${number(Number(result.distance_m)/1000,1)} km · ${routeTime(Number(result.duration_s))} · ${result.provider} (${result.profile})`;
    } catch(error) {$('routing-test-result').textContent=error.message;}
  });

  const today=new Date(); const localDate=`${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
  $('scenario-form').elements.namedItem('start_date').value=localDate;
  $('energy-form').elements.namedItem('source_date').value=localDate;
  $('station-form').elements.namedItem('observed_at').value=localDate;
  applyLanguage();
})();
