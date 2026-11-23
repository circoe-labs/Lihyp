/* Interface sans état persistant client : le token n'est gardé qu'en mémoire. */
(() => {
  'use strict';
  let token = '';
  let actor = null;
  let energies = [], vehicles = [], stations = [], scenarios = [], runs = [];
  let editingVehicleKey = null;
  const $ = (id) => document.getElementById(id);
  const esc = (x) => String(x ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const field = (form, key) => form.elements.namedItem(key).value;
  const message = (msg, isError=false) => {
    const box = $('feedback'); box.classList.remove('hidden');
    box.classList.toggle('error', isError); box.textContent = msg;
    box.scrollIntoView({behavior:'smooth',block:'nearest'});
  };
  async function api(url, options={}) {
    const h = {'Accept':'application/json', ...options.headers};
    if (token) h.Authorization = `Bearer ${token}`;
    if (options.body && !(options.body instanceof FormData)) h['Content-Type'] = 'application/json';
    const res = await fetch(url, {...options, headers:h});
    if (!res.ok) {
      let parsed = {};
      try { parsed = await res.json(); } catch(_) {}
      const parts = Array.isArray(parsed.detail) ? parsed.detail.map(e=>`${e.loc?.slice(-1)[0]||'champ'} : ${e.msg}`).join('; ') : (parsed.error?.message || parsed.detail || res.statusText);
      throw new Error(`${res.status} : ${parts}`);
    }
    if (options.raw) return res;
    return res.status === 204 ? null : res.json();
  }
  function show(view) {
    const titles = {overview:"Vue d'ensemble",energy:'Énergies par pays',vehicles:'Véhicules',stations:'Stations',
                    scenarios:'Simulations',results:'Résultats & PDF',routing:'Routage / API'};
    for (const el of document.querySelectorAll('.view')) el.classList.toggle('hidden', el.id !== `view-${view}`);
    for (const btn of document.querySelectorAll('.nav-item')) btn.classList.toggle('active',btn.dataset.view===view);
    $('page-title').textContent = titles[view];
    $('feedback').classList.add('hidden');
    if (view === 'routing') loadRouting();
    if (view === 'results') loadRuns();
    if (view === 'energy') loadEnergies();
    if (view === 'vehicles') loadVehicles();
    if (view === 'stations') loadStations();
    if (view === 'scenarios') loadScenarios();
  }
  function dataOf(form) { return Object.fromEntries(new FormData(form).entries()); }
  function table(el, columns, rows) {
    if (!rows.length) { el.innerHTML = '<div class="empty-state">Aucune donnée. Enregistrer une entrée pour commencer.</div>';return; }
    el.innerHTML = '<table><thead><tr>'+columns.map(c=>`<th>${esc(c)}</th>`).join('')+'</tr></thead><tbody>'+rows.join('')+'</tbody></table>';
  }
  async function bootstrap() {
    const data = await Promise.all([api('/energies'),api('/vehicles'),api('/scenarios'),api('/runs'),api('/stations')]);
    [energies,vehicles,scenarios,runs,stations]=data;
    $('stat-energies').textContent = energies.length;
    $('stat-vehicles').textContent = vehicles.length;
    $('stat-scenarios').textContent = scenarios.length;
    $('stat-runs').textContent = runs.length;
    fillScenarioSelects();
  }
  $('login-form').addEventListener('submit', async e=> {
    e.preventDefault();
    $('login-message').textContent='';
    const form = e.currentTarget;
    try {
      const {access_token,user} = await api('/auth/login', {method:'POST',body:JSON.stringify(dataOf(form))});
      token = access_token;actor = user;
      $('user-label').textContent = user.username;
      $('login').classList.add('hidden');$('shell').classList.remove('hidden');
      await bootstrap();
    } catch(error) {
      $('login-message').textContent = error.message;
      token='';$('shell').classList.add('hidden');$('login').classList.remove('hidden');
    }
  });
  $('logout-button').addEventListener('click',async()=>{
    try{await api('/auth/logout',{method:'POST'})}catch(_){}
    token='';actor=null;$('shell').classList.add('hidden');$('login').classList.remove('hidden');
    $('login-form').elements.namedItem('password').value='';
  });
  document.querySelectorAll('.nav-item').forEach(el=>el.addEventListener('click',()=>show(el.dataset.view)));
  document.querySelectorAll('[data-goto]').forEach(el=>el.addEventListener('click',()=>show(el.dataset.goto)));
  $('limitations-link').addEventListener('click',e=>{e.preventDefault();show('overview');document.querySelector('.quiet-panel').scrollIntoView({behavior:'smooth'});});

  async function loadEnergies(){
    try{energies=await api('/energies');renderEnergies();fillScenarioSelects();}catch(err){message(err.message,true)}
  }
  function renderEnergies(){
    table($('energy-table'), ['Énergie','Prix national','Facteurs','Version'],energies.map(e=>{
      const p=e.payload;
      return `<tr><td><strong>${esc(p.energy_code)}</strong><small>Non vérifié</small></td><td>${esc(p.price_per_unit)} EUR/${esc(p.unit)}</td><td><small>Direct : ${esc(p.factors.direct ?? '—')}</small><small>Puits-roue : ${esc(p.factors.well_to_wheel ?? '—')}</small></td><td>v${e.revision}<button class="table-action" data-energy-history="${esc(p.energy_code)}">Historique</button></td></tr>`;
    }));
    document.querySelectorAll('[data-energy-history]').forEach(b=>b.addEventListener('click',()=>loadEnergyHistory(b.dataset.energyHistory)));
  }
  async function loadEnergyHistory(code){
    try{const history=await api(`/energies/FR/${encodeURIComponent(code)}/versions`);
      $('energy-history').innerHTML=`<h4>Historique ${esc(code)}</h4><ul>${history.map(v=>`<li>v${v.revision} · ${esc(v.payload.price_per_unit)} EUR/${esc(v.payload.unit)} · ${esc(v.created_at)} · ${esc(v.payload.source)}</li>`).join('')}</ul>`;
    }catch(err){message(err.message,true)}
  }
  $('energy-form').addEventListener('submit',async e=>{
    e.preventDefault();const f=e.currentTarget,d=dataOf(f);
    const unit={DIESEL:'L',ELECTRIC:'kWh',H2:'kg'}[d.energy_code];
    const factors={};if(d.direct.trim())factors.direct=d.direct.trim();if(d.well_to_wheel.trim())factors.well_to_wheel=d.well_to_wheel.trim();
    const body={country_iso:d.country_iso,energy_code:d.energy_code,unit,price_per_unit:d.price_per_unit,
                factors,source:d.source,source_date:d.source_date,license:d.license,quality:'unverified'};
    try{const out=await api('/energies',{method:'POST',body:JSON.stringify(body)});
        await loadEnergies();message(`Version d'énergie ${out.payload.energy_code} v${out.revision} enregistrée (non vérifiée).`);
    }catch(err){message(err.message,true)}
  });
  $('reload-energy').addEventListener('click',loadEnergies);

  async function loadVehicles(){
    try{vehicles=await api('/vehicles');renderVehicles();fillScenarioSelects();}catch(err){message(err.message,true)}
  }
  function renderVehicles(){
    table($('vehicle-table'), ['Modèle','Places','Énergie','Version'],vehicles.map(v=>{
      const p=v.payload;
      return `<tr><td><strong>${esc(p.label)}</strong><small>${esc(p.manufacturer)} ${esc(p.model)}</small></td><td>${esc(p.seats)}</td><td>${esc(p.energy_code)}</td><td>v${v.revision}<button class="table-action" data-vehicle-edit="${esc(v.id)}">Réviser</button><button class="table-action" data-vehicle-history="${esc(v.vehicle_key)}">Historique</button></td></tr>`;
    }));
    document.querySelectorAll('[data-vehicle-edit]').forEach(b=>b.addEventListener('click',()=>editVehicle(b.dataset.vehicleEdit)));
    document.querySelectorAll('[data-vehicle-history]').forEach(b=>b.addEventListener('click',()=>loadVehicleHistory(b.dataset.vehicleHistory)));
  }
  async function loadVehicleHistory(key){
    try{const list=await api(`/vehicles/${encodeURIComponent(key)}/versions`);
      $('vehicle-history').innerHTML=`<h4>Versions de cette variante</h4><ul>${list.map(v=>`<li>v${v.revision} · ${esc(v.payload.label)} · ${esc(v.created_at)}</li>`).join('')}</ul>`;
    }catch(err){message(err.message,true)}
  }
  function editVehicle(id){
    const v=vehicles.find(v=>v.id===id);if(!v)return;
    editingVehicleKey=v.vehicle_key;
    const f=$('vehicle-form');
    for(const [k,val] of Object.entries(v.payload)){
      const input=f.elements.namedItem(k);if(input && typeof val!=='object')input.value=val;
    }
    $('vehicle-edit-label').textContent=`Nouvelle révision de ${v.payload.label} (v${v.revision}); l'ancien enregistrement restera accessible.`;
    $('vehicle-submit').textContent='Créer la révision';$('vehicle-cancel').classList.remove('hidden');
    f.scrollIntoView({behavior:'smooth'});
  }
  function resetVehicle(){editingVehicleKey=null;$('vehicle-form').reset();$('vehicle-submit').textContent='Créer la fiche';$('vehicle-cancel').classList.add('hidden');$('vehicle-edit-label').textContent='Nouveau véhicule — aucune donnée constructeur préchargée.';}
  $('vehicle-cancel').addEventListener('click',resetVehicle);
  $('vehicle-form').addEventListener('submit',async e=>{
    e.preventDefault();const d=dataOf(e.currentTarget);
    d.seats=Number(d.seats);d.life_years=Number(d.life_years);
    d.unit={DIESEL:'L',ELECTRIC:'kWh',H2:'kg'}[d.energy_code];
    d.kind='bus';d.quality='unverified';
    try{
      const path=editingVehicleKey ? `/vehicles/${encodeURIComponent(editingVehicleKey)}/versions`:'/vehicles';
      const out=await api(path,{method:'POST',body:JSON.stringify(d)});
      resetVehicle();await loadVehicles();message(`Fiche ${out.payload.label} v${out.revision} enregistrée.`);
    }catch(err){message(err.message,true)}
  });
  $('reload-vehicles').addEventListener('click',loadVehicles);

  async function loadStations(){
    try{stations=await api('/stations');table($('station-table'),['Station','Statut','Équipements'],stations.map(s=>
      `<tr><td><strong>${esc(s.payload.name)}</strong><small>${esc(s.payload.latitude)}, ${esc(s.payload.longitude)}</small></td><td>Non vérifiée</td><td>${s.payload.equipments.map(e=>`${esc(e.energy_code)} · ${esc(e.connector)} (${esc(e.ports)})`).join('<br>')}</td></tr>`));}
    catch(err){message(err.message,true)}
  }
  $('station-form').addEventListener('submit',async e=>{
    e.preventDefault();const d=dataOf(e.currentTarget);
    const body={name:d.name,longitude:Number(d.longitude),latitude:Number(d.latitude),
                access:d.access,operational_status:'unverified',confidence:'unverified',
                equipments:[{energy_code:d.energy_code,connector:d.connector,ports:Number(d.ports)}],
                source:d.source,observed_at:d.observed_at};
    try{await api('/stations',{method:'POST',body:JSON.stringify(body)});await loadStations();message('Station enregistrée comme non vérifiée.');}
    catch(err){message(err.message,true)}
  });

  function fillScenarioSelects(){
    const vs=$('scenario-vehicle'),es=$('scenario-energy');
    const oldv=vs.value,olde=es.value;
    vs.innerHTML=vehicles.length ? vehicles.map(v=>`<option value="${esc(v.id)}">${esc(v.payload.label)} · v${v.revision} · ${esc(v.payload.seats)} pl.</option>`).join(''):'<option value="">Créer d’abord un véhicule</option>';
    es.innerHTML=energies.length ? energies.map(e=>`<option value="${esc(e.id)}">${esc(e.payload.energy_code)} · v${e.revision} · ${esc(e.payload.price_per_unit)} EUR/${esc(e.payload.unit)}</option>`).join(''):'<option value="">Créer d’abord une énergie</option>';
    if(vehicles.some(v=>v.id===oldv))vs.value=oldv;
    if(energies.some(e=>e.id===olde))es.value=olde;
    matchEnergy();
  }
  function matchEnergy(){
    const vid=$('scenario-vehicle').value;
    const v=vehicles.find(v=>v.id===vid);
    if(!v)return;
    const current=energies.find(e=>e.id===$('scenario-energy').value);
    if(!current || current.payload.energy_code!==v.payload.energy_code){
      const match=energies.find(e=>e.payload.energy_code===v.payload.energy_code);
      if(match)$('scenario-energy').value=match.id;
    }
  }
  $('scenario-vehicle').addEventListener('change',matchEnergy);
  async function loadScenarios(){
    try{scenarios=await api('/scenarios');
      table($('scenario-table'),['Scénario','Date','Révision'],scenarios.map(s=>`<tr><td><strong>${esc(s.name)}</strong><small>${esc(s.id.slice(0,8))}</small></td><td>${esc(s.latest_revision.payload.start_date)}</td><td>v${s.latest_revision.revision}<button class="table-action" data-scenario-run="${esc(s.latest_revision.id)}">Calculer</button></td></tr>`));
      document.querySelectorAll('[data-scenario-run]').forEach(b=>b.addEventListener('click',()=>runScenario(b.dataset.scenarioRun)));
      $('stat-scenarios').textContent=scenarios.length;
    }catch(err){message(err.message,true)}
  }
  async function runScenario(revId){
    try{const run=await api('/runs',{method:'POST',body:JSON.stringify({scenario_revision_id:revId})});
      await loadRuns();show('results');showResult(run);
      message(`Exécution ${run.id.slice(0,8)} enregistrée : ${run.status}.`);
    }catch(err){message(err.message,true)}
  }
  $('scenario-form').addEventListener('submit',async e=>{
    e.preventDefault();const d=dataOf(e.currentTarget);
    if(!d.vehicle_version_id || !d.energy_version_id)return message('Renseigner les catalogues avant simulation.',true);
    const body={name:d.name,country_iso:'FR',start_date:d.start_date,end_date:d.start_date,timezone:'Europe/Paris',
      route:{origin:d.origin,destination:d.destination,distance_m:Number(d.distance_m),duration_s:Number(d.duration_s),provider:'manual',source:d.route_source},
      passengers:Number(d.passengers),window_start:d.window_start,window_end:d.window_end,
      max_vehicles:Number(d.max_vehicles),vehicle_version_id:d.vehicle_version_id,energy_version_id:d.energy_version_id,
      tco_scope:d.tco_scope,emission_scope:d.emission_scope,infrastructure_daily_eur:d.infrastructure_daily_eur};
    try{const sc=await api('/scenarios',{method:'POST',body:JSON.stringify(body)});
        await loadScenarios();await runScenario(sc.latest_revision.id);
    }catch(err){message(err.message,true)}
  });

  async function loadRuns(){
    try{runs=await api('/runs');
      table($('runs-table'),['Exécution','Statut','EUR','kgCO₂e','Actions'],runs.map(r=>{
        const t=r.result.totals||{};
        return `<tr><td><strong>${esc(r.snapshot.scenario.name)}</strong><small>${esc(r.created_at.slice(0,19))}</small></td><td>${esc(r.status)}</td><td>${esc(t.eur_total??'—')}</td><td>${esc(t.kgco2e_total??'—')}</td><td><button class="table-action" data-run-detail="${esc(r.id)}">Voir</button><button class="table-action" data-run-pdf="${esc(r.id)}">PDF</button></td></tr>`;
      }));
      document.querySelectorAll('[data-run-detail]').forEach(b=>b.addEventListener('click',()=>showResult(runs.find(r=>r.id===b.dataset.runDetail))));
      document.querySelectorAll('[data-run-pdf]').forEach(b=>b.addEventListener('click',()=>downloadPdf(b.dataset.runPdf)));
      $('stat-runs').textContent=runs.length;
    }catch(err){message(err.message,true)}
  }
  function showResult(run){
    if(!run)return;
    const e=$('result-detail'),r=run.result,t=r.totals;
    const head=`<div class="result-hero"><div><div class="eyebrow">EXÉCUTION GELÉE</div><h3>${esc(run.snapshot.scenario.name)}</h3><p>Statut : <strong>${esc(run.status)}</strong><br><small>SHA-256 ${esc(run.snapshot_sha256.slice(0,32))}…</small></p></div><button class="button primary" id="pdf-current">Rapport PDF ↓</button></div>`;
    if(!t){e.innerHTML=head+`<p class="warning-text">Aucun résultat calculé. ${esc((r.constraints||[]).map(x=>x.message).join(' • '))}</p>`;}
    else{
      const kpis=[['Coût TCO',`${t.eur_total} EUR`],['Émissions',`${t.kgco2e_total} kg CO₂e`],['Voyageurs servis',t.passengers_served],['Véhicules utilisés',t.vehicles_used]];
      e.innerHTML=head+`<div class="kpi-grid">${kpis.map(([n,v])=>`<div class="kpi"><small>${esc(n)}</small><strong>${esc(v)}</strong></div>`).join('')}</div><p><b>Énergie :</b> ${esc(t.energy_consumed)} ${esc(t.energy_unit)} · <b>Voyageurs-km :</b> ${esc(t.passenger_km)} · <b>EUR/voyageur :</b> ${esc(t.eur_per_passenger??'n/a')}</p><h3>Courses</h3><div class="table-wrap"><table><thead><tr><th>Course</th><th>Véhicule</th><th>Départ UTC</th><th>Voyageurs</th><th>Consommation</th></tr></thead><tbody>${r.trips.map(t=>`<tr><td>${esc(t.trip_id)}</td><td>${esc(t.vehicle_instance)}</td><td>${esc(t.depart_utc)}</td><td>${esc(t.passengers)}</td><td>${esc(t.energy_used)}</td></tr>`).join('')}</tbody></table></div><h3>Fiabilité et limites</h3><ul class="result-list">${(r.warnings||[]).map(w=>`<li>${esc(w)}</li>`).join('')}</ul>`;
    }
    e.classList.remove('hidden');$('pdf-current').addEventListener('click',()=>downloadPdf(run.id));
    e.scrollIntoView({behavior:'smooth',block:'start'});
  }
  async function downloadPdf(id){
    try{const res=await api(`/runs/${encodeURIComponent(id)}/report.pdf`,{raw:true});
      const blob=await res.blob();const url=URL.createObjectURL(blob);
      const a=document.createElement('a');a.href=url;a.download=`simulation-${id}.pdf`;
      document.body.appendChild(a);a.click();a.remove();
      setTimeout(()=>URL.revokeObjectURL(url),5000);
    }catch(err){message(err.message,true)}
  }
  $('reload-results').addEventListener('click',loadRuns);

  async function loadRouting(){
    try{const info=await api('/routing/status');$('routing-status').innerHTML=`<p>Fournisseur : <strong>${esc(info.provider)}</strong> · ${info.configured ? '<strong>Clé côté serveur configurée</strong>':'<span class="warning-text">Clé absente</span>'}</p>`;
    }catch(err){message(err.message,true)}
  }
  $('routing-form').addEventListener('submit',async e=>{
    e.preventDefault();const d=dataOf(e.currentTarget);
    try{const r=await api('/routing/preview',{method:'POST',body:JSON.stringify({origin:[Number(d.lon1),Number(d.lat1)],destination:[Number(d.lon2),Number(d.lat2)],profile:d.profile})});
      $('routing-answer').textContent=`Distance : ${r.distance_m} m\nDurée : ${r.duration_s} s\nProvider : ${r.provider}\nVersion : ${r.version}\nAvertissements : ${(r.restrictions||[]).join('; ')}`;
    }catch(err){message(err.message,true)}
  });
  for(const id of ['energy-form','station-form','scenario-form']){
    const input=$(id).elements.namedItem(id==='energy-form'?'source_date':id==='station-form'?'observed_at':'start_date');
    input.value=new Date().toISOString().slice(0,10);
  }
})();
