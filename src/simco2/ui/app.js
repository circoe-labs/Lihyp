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
      settings:'PARAMÈTRES',navVehicles:'Véhicules',navEnergy:'Énergies par pays',prototypeNotice:'Prototype : 1 ligne, 1 jour, sans trajets retour ni ravitaillement. Les résultats ne sont pas un optimum prouvé.',
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
      oneWayWarning:'Calcul sur un trajet simple sans retour ni réemploi de véhicules. Le routage ne certifie pas les restrictions autocars.',
      mySimulations:'Mes simulations',myResults:'Résultats précédents',stationKicker:'RÉFÉRENTIELS GÉOGRAPHIQUES',
      stationTitle:'Stations en Normandie',stationIntro:'Stations hydrogène répertoriées et stations essence/gazole issues de la DGCCRF. Informations indicatives, sans garantie d’accès pour les autocars.',
      refresh:'Actualiser',filterType:'Afficher',filterAll:'Toutes les stations',filterH2:'Hydrogène H₂',filterFuel:'Essence / gazole',
      filterManual:'Ajoutées manuellement',mapInfo:'Localisations déclarées dans les sources',moreStations:'Charger davantage de stations essence',
      stationCaution:"Liste indicative : une station H₂ destinée aux véhicules légers n'est pas automatiquement compatible avec un autocar. Disponibilité et accès à confirmer auprès de l'exploitant.",
      addStation:'Ajouter une station manuellement (avancé)',stationName:'Nom de la station',longitude:'Longitude',latitude:'Latitude',
      access:'Accès',publicDeclared:'Public (déclaré)',private:'Privé',restricted:'Restreint',pump:'Pompe / connecteur',ports:'Nombre de points',
      source:'Source / méthode',sourceHint:'Document ou relevé',sourceDate:'Date de source',saveStation:'Enregistrer la station non vérifiée',
      vehicleIntro:'Créer un modèle de véhicule utilisé par les simulations. Les valeurs doivent être justifiées par une source.',
      vehicleFormTitle:'Fiche véhicule',vehicleUnverified:'Données constructeur non préchargées : valeurs à vérifier.',
      modelName:'Nom de variante',modelExample:'Autocar diesel A',manufacturer:'Constructeur',model:'Modèle',seats:'Places utiles',
      diesel:'Gazole (L)',electric:'Électricité (kWh)',hydrogen:'Hydrogène (kg)',consumptionKm:'Consommation / km',
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
      navRouting:'API de routage',compareHint:'Sélectionnez au moins deux véhicules. L’énergie et le prix national sont associés automatiquement.',
      selectAtLeastTwo:'Sélectionnez au moins deux véhicules différents à comparer.',
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
      settings:'SETTINGS',navVehicles:'Vehicles',navEnergy:'Energy by country',prototypeNotice:'Prototype: one route, one day, no return trips or refuelling. Results are not proven optimal.',
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
      oneWayWarning:'One-way calculation without vehicle reuse or return journeys. Routing does not certify coach road restrictions.',
      mySimulations:'My simulations',myResults:'Previous results',stationKicker:'LOCATION DIRECTORY',
      stationTitle:'Stations in Normandy',stationIntro:'Listed hydrogen stations and official petrol/diesel stations from DGCCRF. Indicative information; coach access is not guaranteed.',
      refresh:'Refresh',filterType:'Show',filterAll:'All stations',filterH2:'Hydrogen H₂',filterFuel:'Petrol / diesel',
      filterManual:'Manually added',mapInfo:'Locations as published by data sources',moreStations:'Load more petrol stations',
      stationCaution:'Caution: a hydrogen station for light vehicles is not automatically compatible with a coach. Check availability and access with the operator.',
      addStation:'Add a station manually (advanced)',stationName:'Station name',longitude:'Longitude',latitude:'Latitude',
      access:'Access',publicDeclared:'Public (declared)',private:'Private',restricted:'Restricted',pump:'Pump / connector',ports:'Number of outlets',
      source:'Source / methodology',sourceHint:'Document or observation',sourceDate:'Source date',saveStation:'Save as unverified station',
      vehicleIntro:'Create a vehicle model for use in simulations. Values should be backed by a source.',
      vehicleFormTitle:'Vehicle details',vehicleUnverified:'No manufacturer data preloaded: values require validation.',
      modelName:'Variant name',modelExample:'Diesel coach A',manufacturer:'Manufacturer',model:'Model',seats:'Usable seats',
      diesel:'Diesel (L)',electric:'Electricity (kWh)',hydrogen:'Hydrogen (kg)',consumptionKm:'Consumption / km',
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
      navRouting:'Routing API',compareHint:'Select at least two vehicles. Energy type and national price are matched automatically.',
      selectAtLeastTwo:'Select at least two different vehicles for the comparison.',
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
    const active = document.querySelector('.nav-item.active');
    $('page-title').textContent = t({scenarios:'navSimulations',stations:'navStations',vehicles:'navVehicles',energy:'navEnergy',routing:'navRouting'}[active?.dataset.view] || 'navSimulations');
    renderEnergies(); renderVehicles(); renderScenarios(); renderRuns(); renderStations();
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
    if (view === 'vehicles') loadVehicles();
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
  function renderEnergies() {
    if (!$('energy-table')) return;
    table($('energy-table'),[t('energy'),t('energyPrice'),t('factors'),t('actions')],energies.map(e => {
      const p = e.payload;
      return `<tr><td><strong>${esc(p.energy_code)}</strong><small>${esc(t('unverified'))}</small></td><td>${esc(p.price_per_unit)} EUR/${esc(p.unit)}</td><td>${esc(t('direct'))}: ${esc(p.factors.direct ?? '—')}<br>${esc(t('wtw'))}: ${esc(p.factors.well_to_wheel ?? '—')}</td><td><button class="table-action" data-energy-history="${esc(p.energy_code)}">${esc(t('history'))}</button></td></tr>`;
    }));
    document.querySelectorAll('[data-energy-history]').forEach(b => b.addEventListener('click', () => loadEnergyHistory(b.dataset.energyHistory)));
  }
  async function loadEnergyHistory(code) {
    energyHistoryCode = code;
    try {
      const versions = await api(`/energies/FR/${encodeURIComponent(code)}/versions`);
      $('energy-history').innerHTML = `<h4>${esc(t('energyHistory'))} ${esc(code)}</h4><p>${esc(t('energyHistoryNote'))}</p><ul>${versions.map(v =>
        `<li>v${v.revision} · ${esc(v.payload.price_per_unit)} EUR/${esc(v.payload.unit)} · ${esc(v.payload.source)} · ${esc(v.created_at)}</li>`).join('')}</ul>`;
    } catch (error) { message(error.message, true); }
  }
  $('energy-form').addEventListener('submit', async event => {
    event.preventDefault(); const d = dataOf(event.currentTarget), factors = {};
    if (d.direct.trim()) factors.direct = d.direct.trim();
    if (d.well_to_wheel.trim()) factors.well_to_wheel = d.well_to_wheel.trim();
    const unit = {DIESEL:'L',ELECTRIC:'kWh',H2:'kg'}[d.energy_code];
    try {
      await api('/energies', {method:'POST', body:JSON.stringify({country_iso:d.country_iso,
        energy_code:d.energy_code,unit,price_per_unit:d.price_per_unit, factors, source:d.source,
        source_date:d.source_date,license:d.license,quality:'unverified'})});
      await loadEnergies(); message(t('createdVersion'));
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
  function solutionCard(p, vehicle=null) {
    const isDemo = !vehicle;
    const key = isDemo ? '' : esc(vehicle.id);
    const energyName = t(({DIESEL:'diesel', ELECTRIC:'electric', H2:'hydrogen'})[p.energy_code] || 'diesel');
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
    editingVehicleKey = null; $('vehicle-form').reset();
    $('vehicle-edit-label').textContent = t('vehicleUnverified');
    $('vehicle-cancel').classList.add('hidden');
  }
  $('vehicle-cancel').addEventListener('click', resetVehicle);
  $('vehicle-form').addEventListener('submit', async event => {
    event.preventDefault(); const d = dataOf(event.currentTarget);
    d.seats = Number(d.seats); d.life_years = Number(d.life_years);
    d.unit = {DIESEL:'L',ELECTRIC:'kWh',H2:'kg'}[d.energy_code];
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
        <span><strong>${esc(v.payload.label)}</strong><small>${esc(v.payload.seats)} ${esc(t('seatsShort'))} · ${esc(t(({DIESEL:'diesel',ELECTRIC:'electric',H2:'hydrogen'})[v.payload.energy_code] || 'diesel'))} · ${missing?esc(t('missingEnergyOption')):esc(e.payload.price_per_unit)+' EUR/'+esc(e.payload.unit)}</small></span>
      </label>`;
    }).join('') || `<p class="empty-state">${esc(t('selectVehicle'))}</p>`;
    list.querySelectorAll('.compare-vehicle-checkbox').forEach(el => el.addEventListener('change', () => {
      if (el.checked) selectedVehicleIds.add(el.value); else selectedVehicleIds.delete(el.value);
    }));
    const eligible = vehicles.filter(v => energies.some(e => e.payload.energy_code === v.payload.energy_code));
    const needed = eligible.length < 2;
    $('catalogue-notice').classList.toggle('hidden', !needed);
    if (needed) $('catalogue-notice').innerHTML = `${esc(t('configureCatalogs'))} <button type="button" class="table-action" data-goto="energy">${esc(t('configureEnergy'))}</button> · <button type="button" class="table-action" data-goto="vehicles">${esc(t('configureVehicle'))}</button>`;
  }

  function invalidateRoute() {
    currentQuote = null; currentRoute = null;
    $('route-summary').classList.add('hidden');
    if (routeMap) { routeDrawings.forEach(layer => routeMap.removeLayer(layer)); routeDrawings = []; }
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
  function showRouteMap(route) {
    if (!routeMap) routeMap = ensureMap('route-map');
    $('route-map-fallback').classList.toggle('hidden', !!routeMap);
    $('route-map').classList.toggle('hidden', !routeMap);
    if (!routeMap) return;
    routeDrawings.forEach(layer => routeMap.removeLayer(layer)); routeDrawings = [];
    const start = route.origin_coordinates, end = route.destination_coordinates;
    if (!start || !end || !route.geometry) return;
    const feature = window.L.geoJSON(route.geometry, {style:{color:'#0b7f8b',weight:5}}).addTo(routeMap);
    routeDrawings.push(feature);
    for (const [i,[point,label]] of [[start,route.origin],[end,route.destination]].entries()) {
      // SVG dots avoid external marker-image requests when the CDN is restricted.
      routeDrawings.push(window.L.circleMarker([point[1],point[0]], {
        radius:8, color:'#fff', weight:3,
        fillColor:i === 0 ? '#087e8b' : '#ca8137', fillOpacity:1,
      }).bindPopup(esc(label)).addTo(routeMap));
    }
    // Let the browser finish showing the container before measuring its pixels.
    requestAnimationFrame(() => {
      if (!routeMap || $('view-scenarios').classList.contains('hidden')) return;
      routeMap.invalidateSize({pan:false});
      const bounds = feature.getBounds();
      if(bounds.isValid()) routeMap.fitBounds(bounds.pad(0.14));
    });
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
    root.innerHTML = `<div class="result-hero"><div><div class="eyebrow">${esc(t('compareResultsTitle'))}</div><h3>${esc(comparison.name)}</h3>
      <p>${esc(shared.route.origin)} → ${esc(shared.route.destination)} · ${esc(number(shared.route.distance_m/1000,1))} km · ${esc(shared.passengers)} ${esc(t('passengers'))}</p>
      <p class="small muted">${esc(t('compareSameInputs'))} SHA-256 ${esc(comparison.shared_sha256.slice(0,16))}…</p></div></div>
      <div class="table-wrap comparison-table"><table><thead><tr>${headers.map(key=>`<th>${esc(t(key))}</th>`).join('')}</tr></thead><tbody>
      ${comparison.entries.map(entry=>{
        const result=entry.result, total=result.totals, vehicle=entry.vehicle_version.payload, energy=entry.energy_version.payload;
        const valid = !!total && result.status==='feasible_not_proven';
        const detail=valid?t('compareStatus'):t(`status_${result.status}`);
        const warn=!valid?`<small>${esc((result.constraints||[]).map(x=>translatedEngineMessage(x.message)).join(' · '))}</small>`:'';
        return `<tr><td><strong>${esc(vehicle.label)}</strong><small>${esc(vehicle.seats)} ${esc(t('seatsShort'))}</small></td>
          <td>${esc(energy.energy_code)}<small>${esc(energy.price_per_unit)} EUR/${esc(energy.unit)}</small></td>
          <td><span class="${valid?'compare-good':'compare-bad'}">${esc(detail)}</span>${warn}</td>
          <td>${valid?esc(total.vehicles_used):'—'}</td>
          <td>${valid?esc(number(total.eur_total,2))+' €':'—'}</td>
          <td>${valid && total.kgco2e_total!==null?esc(number(total.kgco2e_total,2))+' kg':'—'}</td>
          <td>${valid && total.kgco2e_per_passenger!==null?esc(number(total.kgco2e_per_passenger,3))+' kg':'—'}</td>
          <td>${valid?esc(number(total.energy_consumed,2))+' '+esc(total.energy_unit):'—'}</td>
          <td><button type="button" class="button outline" data-compare-pdf="${esc(entry.run_id)}">PDF</button></td></tr>`;
      }).join('')}</tbody></table></div>
      <p class="small warning-text">${esc(t('compareReadOnly'))}</p>`;
    root.classList.remove('hidden'); $('result-detail').classList.add('hidden');
    root.querySelectorAll('[data-compare-pdf]').forEach(b=>b.addEventListener('click',()=>downloadPdf(b.dataset.comparePdf)));
    if (scroll) root.scrollIntoView({behavior:'smooth',block:'start'});
  }
  $('scenario-form').addEventListener('submit', async event => {
    event.preventDefault(); const d = dataOf(event.currentTarget);
    const ids = [...selectedVehicleIds].filter(id => {
      const v=vehicles.find(v=>v.id===id);return v && energies.some(e=>e.payload.energy_code===v.payload.energy_code);
    });
    if (ids.length < 2) return message(t('selectAtLeastTwo'),true);
    if (!currentQuote) return message(t('routeRequired'),true);
    const body={name:d.name,route_quote_id:currentQuote,vehicle_version_ids:ids,
      country_iso:'FR',start_date:d.start_date,passengers:Number(d.passengers),
      window_start:d.window_start,window_end:d.window_end,max_vehicles:Number(d.max_vehicles),
      tco_scope:d.tco_scope,emission_scope:d.emission_scope,infrastructure_daily_eur:d.infrastructure_daily_eur};
    const btn=$('scenario-submit'); btn.disabled=true;
    try {
      const result=await api('/comparisons',{method:'POST',body:JSON.stringify(body)});
      showComparison(result); await loadComparisons(); await loadScenarios(); await loadRuns();
      message(t('runSaved'));
    } catch(err) { message(err.message,true); }
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
  async function loadStations() {
    if (stationLoading) return;
    stationLoading = true;
    try {
      const [manual,data] = await Promise.all([api('/stations'),api('/stations/discovery?offset=0&limit=100')]);
      customStations=manual; h2Stations=data.hydrogen; fuelStations=data.fuel.stations;fuelPage=data.fuel;
      renderStations();
    } catch(error) { message(error.message,true); }
    finally {stationLoading=false;}
  }
  $('reload-stations').addEventListener('click',loadStations);
  $('station-filter').addEventListener('change',renderStations);
  $('more-stations').addEventListener('click',async () => {
    if (!fuelPage?.has_more || stationLoading) return;
    stationLoading=true;
    try {
      const offset=fuelPage.offset + fuelPage.limit;
      const data=await api(`/stations/discovery?offset=${offset}&limit=100`);
      fuelStations.push(...data.fuel.stations); fuelPage=data.fuel;
      renderStations();
    } catch(error) { message(error.message,true); }
    finally { stationLoading=false; }
  });
  function renderStations() {
    if (!$('station-list')) return;
    const filter=$('station-filter').value;
    const all=[...h2Stations,...fuelStations,...customStations.map(normalizeManualStation)];
    const filtered=all.filter(s=>filter==='all' ||
      (filter==='h2' && s.category==='hydrogen') ||
      (filter==='fuel' && s.category==='fuel') ||
      (filter==='manual' && s.category==='manual'));
    $('station-counter').textContent=`${filtered.length} ${t('recordedLocations')}`;
    $('station-data-status').textContent= fuelPage?.unavailable ? t('fuelUnavailable') :
      fuelPage?.has_more ? `${t('fuelPartial')} ${fuelStations.length}/${fuelPage.total}` : '';
    $('more-stations').classList.toggle('hidden',!fuelPage?.has_more || filter==='h2' || filter==='manual');
    $('station-list').innerHTML=filtered.map(s=> {
      const label = t(s.category==='hydrogen'?'hydrogenBadge':s.category==='fuel'?'fuelBadge':'manualBadge');
      const verified = s.category==='hydrogen' ? `${t('reportedOpen')} · ${esc(s.pressure_bar)} bar` : t('reportedListed');
      const url=safeUrl(s.source);
      return `<div class="station-card"><div><span class="station-type ${esc(s.category)}">${esc(label)}</span><strong>${esc(s.name)}</strong><small>${esc(s.address||`${s.latitude}, ${s.longitude}`)}</small><small>${esc(verified)}</small><small>${esc(s.category==='hydrogen'?t('h2Disclaimer'):s.category==='fuel'?t('fuelDisclaimer'):t('unverified'))}</small></div>${url?`<a href="${esc(url)}" target="_blank" rel="noopener" class="subtle-link">${esc(t('sourceLink'))} ↗</a>`:''}</div>`;
    }).join('') || `<div class="empty-state">${esc(t('noData'))}</div>`;
    if ($('view-stations').classList.contains('hidden')) return;
    if(!stationsMap) stationsMap=ensureMap('station-map');
    $('station-map-fallback').classList.toggle('hidden',!!stationsMap);
    $('station-map').classList.toggle('hidden', !stationsMap);
    if(!stationsMap) return;
    stationDrawings.forEach(layer=>stationsMap.removeLayer(layer));stationDrawings=[];
    const positions=[];
    for(const s of filtered) {
      if(!Number.isFinite(Number(s.latitude)) || !Number.isFinite(Number(s.longitude))) continue;
      const point=[Number(s.latitude), Number(s.longitude)];
      const marker=window.L.circleMarker(point,{radius:7,color:s.category==='hydrogen'?'#087e8b':s.category==='fuel'?'#d08a30':'#586577',weight:2,fillOpacity:.8})
        .bindPopup(`<strong>${esc(s.name)}</strong><br>${esc(s.address)}`)
        .addTo(stationsMap);
      stationDrawings.push(marker); positions.push(point);
    }
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
