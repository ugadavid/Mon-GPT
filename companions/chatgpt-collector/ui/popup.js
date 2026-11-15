/* Orchestration de popup adaptée du flux MJ Collector : onglet/message, storage
 * onChanged, scan, copie, Blob, confirmation. Présentation et métier séparés. */
(function () {
  'use strict';
  const Core = CollectorCore, Adapter = ChatGPTAdapter, View = CollectorPresentation;
  const $ = id => document.getElementById(id);
  const inputs = [...document.querySelectorAll('input[name="collectionMode"]')];
  let state = null, page = null, tabId = null, busy = false;
  function status(message, error = false) { $('status').textContent = message; $('status').classList.toggle('error', error); }
  async function request(message) {
    const result = await chrome.runtime.sendMessage({ channel: 'mon-gpt-collector-v2', ...message });
    if (!result?.ok) throw Error(result?.error || 'Le collecteur ne répond pas.');
    return result;
  }
  function render() {
    if (!state) return;
    const records = Core.recent(state), count = records.length, scan = state.lastScan;
    const entities = Object.values(state.entities), namedCount = entities.filter(p => p.name !== null).length;
    document.body.classList.toggle('has-projects', entities.length > 0);
    $('projectsSection').hidden = entities.length === 0;
    $('projectsSummary').textContent = `${entities.length} · ${namedCount} nommé(s) · ${entities.length - namedCount} sans nom`;
    $('projectList').title = entities.length > 50 ? 'Les 50 premiers projets sont affichés ; le JSON les contient tous.' : '';
    View.renderEntities(document, $('projectList'), entities);
    $('total').textContent = count.toLocaleString('fr-FR');
    $('newCount').textContent = scan ? '+' + scan.newCount : '—';
    $('scanSummary').textContent = scan ? `${scan.existingCount} déjà connue(s) · ${scan.kind === 'manual' ? 'dernier scan' : 'dernier relevé auto'}` : 'Pas encore de scan';
    const mode = View.MODES[state.mode];
    $('modeName').textContent = mode.name;
    $('modeHelp').textContent = mode.description;
    for (const input of inputs) { input.checked = input.value === state.mode; input.disabled = busy; }
    $('scanButton').disabled = busy || !page?.ok;
    for (const id of ['copyButton', 'txtButton']) $(id).disabled = busy || count === 0;
    for (const id of ['jsonButton', 'clearButton']) $(id).disabled = busy || (count === 0 && entities.length === 0);
    $('recentCount').textContent = count > 50 ? '50 sur ' + count : String(count);
    View.renderList(document, $('conversationList'), records, entities.length ? { emptyHeading: 'Aucune discussion observée', emptyText: 'Le JSON inclut les projets, même sans discussion.' } : { emptyText: 'Ouvrez ChatGPT, puis scannez les liens présents dans sa barre latérale.' });
    $('capacity').hidden = count < 1000;
    $('capacity').textContent = `${count.toLocaleString('fr-FR')} / 5 000 observations. Pensez à exporter vos liens ; aucun effacement automatique.`;
    $('pageStatus').classList.toggle('ready', Boolean(page?.ok));
    $('pageStatus').textContent = page?.ok ? (state.mode === 'manual' ? 'Onglet ChatGPT prêt · collecte auto suspendue' : 'Onglet ChatGPT prêt · ' + mode.name.toLowerCase()) : 'Page non compatible ou onglet à actualiser · auto suspendue';
  }
  async function load() {
    const result = await request({ type: 'state' });
    state = Core.validate(result.state, 'chatgpt', Adapter.normalize, Core.LIMITS, Adapter.normalizeEntity);
    if (result.error) status(result.error, true);
    render(); return result;
  }
  async function connectPage() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true }); tabId = tab?.id;
    page = null;
    if (tabId !== undefined) {
      try { page = await chrome.tabs.sendMessage(tabId, { channel: 'mon-gpt-collector-v2', type: 'pageStatus' }); } catch { /* Autre site ou onglet à actualiser. */ }
    }
    render();
  }
  async function guarded(action) {
    try { await action(); } catch (error) { status(error.message || 'Action impossible.', true); }
  }
  $('scanButton').addEventListener('click', () => guarded(async () => {
    if (busy || !page?.ok) return;
    busy = true; render(); status('Scan en cours… seuls les liens déjà rendus sont observés.');
    try {
      const result = await chrome.tabs.sendMessage(tabId, { channel: 'mon-gpt-collector-v2', type: 'scanCurrentPage' });
      if (!result?.ok) throw Error(result?.error || 'Scan indisponible ; actualisez cet onglet.');
      await load();
      status(result.detectedCount || result.entityCount ? `${result.newCount} nouvelle(s) · ${result.existingCount} déjà connue(s) · ${result.entityCount} projet(s) observé(s).` : 'Aucun lien de discussion ou projet observable sur cette page.');
    } finally { busy = false; render(); }
  }));
  for (const input of inputs) input.addEventListener('change', () => guarded(async () => {
    if (!input.checked || busy) return;
    busy = true; render();
    try {
      await request({ type: 'mode', mode: input.value }); await load(); await connectPage();
      status(View.MODES[input.value].name + ' enregistré.');
    } finally { busy = false; render(); }
  }));
  $('copyButton').addEventListener('click', () => guarded(async () => {
    await navigator.clipboard.writeText(Core.urlsText(state)); status('URLs copiées · une adresse par ligne.');
  }));
  $('jsonButton').addEventListener('click', () => guarded(async () => {
    const payload = Adapter.exportJson(state, new Date().toISOString());
    View.downloadTextFile(document, 'mon-gpt-observations.json', JSON.stringify(payload, null, 2) + '\n', 'application/json;charset=utf-8');
    status('Export JSON lancé · vos métadonnées observées sont conservées.');
  }));
  $('txtButton').addEventListener('click', () => guarded(async () => {
    Core.validate(state, 'chatgpt', Adapter.normalize, Core.LIMITS, Adapter.normalizeEntity);
    View.downloadTextFile(document, 'mon-gpt-urls.txt', Core.urlsText(state) + '\n', 'text/plain;charset=utf-8'); status('Export TXT lancé · une adresse par ligne.');
  }));
  $('clearButton').addEventListener('click', () => $('clearDialog').showModal());
  $('cancelClear').addEventListener('click', () => $('clearDialog').close());
  $('confirmClear').addEventListener('click', () => guarded(async () => {
    await request({ type: 'clear' }); $('clearDialog').close(); await load(); status('Observations vidées. Le mode choisi est conservé.');
  }));
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === 'local' && changes.monGptCollectorStateV2) guarded(async () => { await load(); });
  });
  Promise.all([load(), connectPage()]).then(results => {
    if (results[0].error) return;
    if (page?.error) status(page.error, true);
    else status(page?.ok ? 'Conservées ici · aucune importation dans Mon GPT.' : 'Ouvrez ChatGPT pour collecter. Vos exports restent disponibles.');
  }).catch(error => status('Stockage indisponible : ' + error.message, true));
  setInterval(() => {
    if (!busy) guarded(async () => {
      const result = await load(); await connectPage();
      if (result.error || page?.error) status(result.error || page.error, true);
    });
  }, 2000);
})();
