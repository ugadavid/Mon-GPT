/* Recette sur Chrome installé, profil isolé, vrai MV3 et vraie popup.
 * Interception de la seule navigation de fixture : aucun compte ChatGPT utilisé.
 * --hold : arrêts pour captures Windows natives, repris par .recette/continue-<étape>. */
'use strict';
const puppeteer = require('puppeteer-core');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const ROOT = path.resolve(__dirname, '..');
const REPORT = path.resolve(ROOT, '../../reports/MG-008a');
const WORK = path.join(ROOT, '.recette');
const PROFILE = path.join(WORK, 'chrome-' + Date.now());
const ID = '00000000-0000-4000-8000-000000000801';
const KEY = 'monGptCollectorStateV2';
const A = 'g-p-11111111111111111111111111111111', B = 'g-p-22222222222222222222222222222222', C = 'g-p-33333333333333333333333333333333', D = 'g-p-44444444444444444444444444444444';
const PACKAGED = JSON.parse(execFileSync('python', ['tools/package_collector.py'], { cwd: path.resolve(ROOT, '../..'), encoding: 'utf8' })).folder;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const checkpoints = process.argv.includes('--hold');
let browser, worker, popup, extensionId, page;
const log = [];
function pass(message) { log.push('OK · ' + message); console.log(log.at(-1)); }
async function until(predicate, message, timeout = 12000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) { if (await predicate()) return; await sleep(100); }
  throw Error('Délai dépassé : ' + message);
}
async function state() { return worker.evaluate(async key => (await chrome.storage.local.get(key))[key], KEY); }
async function openPopup(targetPage = page) {
  if (popup && !popup.isClosed()) await popup.close();
  await targetPage.bringToFront();
  await worker.evaluate(() => chrome.action.openPopup());
  const target = await browser.waitForTarget(t => t.url().endsWith('/ui/popup.html'));
  popup = await target.asPage();
  await popup.waitForFunction(() => document.getElementById('total').textContent !== '—');
  return popup;
}
async function chooseMode(mode) {
  await popup.click(`label:has(input[value="${mode}"])`);
  await until(async () => (await state())?.mode === mode, 'mode ' + mode);
  await popup.waitForFunction(value => document.querySelector(`input[value="${value}"]`).checked && !document.querySelector(`input[value="${value}"]`).disabled, {}, mode);
}
async function checkpoint(stage) {
  const size = await popup.evaluate(() => ({ body: document.body.scrollHeight, viewport: document.documentElement.clientHeight }));
  console.log('POPUP_HEIGHT', stage, size); assert.ok(size.body <= 600, 'Popup entièrement utilisable sous le plafond Chrome');
  await popup.screenshot({ path: path.join(WORK, stage + '-renderer.png') });
  if (!checkpoints || !stage.includes('projets-')) return;
  if (process.env.COLLECTOR_CAPTURE_STAGE && process.env.COLLECTOR_CAPTURE_STAGE !== stage) return;
  const continuation = 'continue-' + path.basename(PROFILE) + '-' + stage;
  await fs.writeFile(path.join(WORK, 'stage.json'), JSON.stringify({ stage, continuation, extensionId, fixtureTitle: 'Recette fictive MG-008a' }));
  console.log('CAPTURE_NATIVE · ' + stage);
  await until(async () => { try { await fs.access(path.join(WORK, continuation)); return true; } catch { return false; } }, 'capture native ' + stage, 20 * 60 * 1000);
}
async function launch(install = false) {
  browser = await puppeteer.launch({ executablePath: process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: false,
    pipe: true, enableExtensions: true, protocolTimeout: 30000, userDataDir: PROFILE, defaultViewport: null, args: ['--window-size=1360,850'] });
  // Le chargement de test CDP est propre au processus Chrome : même chemin,
  // même ID et même stockage, rechargés explicitement après redémarrage.
  const loadedId = await browser.installExtension(PACKAGED);
  if (install) extensionId = loadedId;
  else assert.equal(loadedId, extensionId);
  const target = await browser.waitForTarget(t => t.type() === 'service_worker' && t.url().endsWith('/browser/background.js'));
  worker = await target.worker();
}
async function fixture(url = 'https://chatgpt.com/', filename = 'sidebar.html') {
  const p = await browser.newPage(); const requests = [];
  await p.setRequestInterception(true);
  const html = await fs.readFile(path.join(__dirname, 'fixtures', filename), 'utf8');
  p.on('request', request => {
    requests.push(request.url());
    if (request.isNavigationRequest() && request.frame() === p.mainFrame()) request.respond({ status: 200, contentType: 'text/html; charset=utf-8', body: html });
    else request.abort();
  });
  await p.goto(url, { waitUntil: 'load' });
  return { page: p, requests };
}
(async () => {
  await fs.mkdir(WORK, { recursive: true }); await fs.mkdir(REPORT, { recursive: true });
  await launch(true); pass('Extension MV3 installée et activée dans ' + await browser.version());
  const blank = (await browser.pages())[0]; page = blank;
  await openPopup(); await chooseMode('manual'); await popup.close();
  const controlled = await fixture(); page = controlled.page;
  await sleep(1000); assert.equal(Object.keys((await state())?.records || {}).length, 0);
  await openPopup(); await popup.waitForFunction(() => !document.getElementById('scanButton').disabled);
  assert.equal(await popup.$eval('#copyButton', el => el.disabled), true);
  pass('Manuel : aucune collecte avant clic, état vide et actions d’export désactivées');
  await checkpoint('01-vide-manuel');
  const domBefore = await page.content();
  await popup.click('#scanButton');
  await until(async () => Object.keys((await state()).records).length === 15, 'scan manuel');
  await popup.waitForFunction(() => document.getElementById('newCount').textContent === '+15');
  assert.equal(await page.content(), domBefore, 'Aucune écriture dans le DOM de la fixture');
  let current = await state();
  assert.equal(current.records[ID].observedUrls.length, 2);
  assert.equal(current.records['00000000-0000-4000-8000-000000000815'].title, null);
  assert.ok(!JSON.stringify(current).includes('INTERDIT'));
  assert.ok(!current.records['00000000-0000-4000-8000-000000000897']);
  assert.ok(!current.records['00000000-0000-4000-8000-000000000898']);
  pass('Scan réel : 15 nouvelles, URL globale/projet fusionnées, titre inconnu, faux domaine et contenu exclus');
  assert.equal((await popup.$$('.conversation')).length, 15);
  assert.equal(await popup.$eval('body', e => e.getBoundingClientRect().width), 408);
  assert.ok(await popup.$eval('#conversationList', e => e.scrollHeight > e.clientHeight));
  await checkpoint('02-popup-remplie');
  await popup.click('#scanButton');
  await until(async () => (await state()).records[ID].seenCount === 2, 'scan répété');
  current = await state(); assert.equal(current.lastScan.newCount, 0); assert.equal(current.lastScan.existingCount, 15);
  await popup.focus('#scanButton'); await popup.keyboard.press('Tab');
  assert.equal(await popup.evaluate(() => document.activeElement.id), 'copyButton');
  await popup.keyboard.press('Enter');
  await popup.waitForFunction(() => document.getElementById('status').textContent.includes('URLs copiées'));
  const clipboard = execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', 'Get-Clipboard -Raw'], { encoding: 'utf8' }).trim();
  const expected = Object.values(current.records).sort((a, b) => a.identity.localeCompare(b.identity)).map(r => r.url).join('\n');
  assert.ok(clipboard.replace(/\r\n/g, '\n') === expected, 'Copie des seules URLs fictives attendues');
  pass('Second scan : 0 nouvelle / 15 connues ; Tab/Entrée et copie effective des URLs');
  const downloads = path.join(PROFILE, 'exports-fictifs'); await fs.mkdir(downloads, { recursive: true });
  await browser.defaultBrowserContext().setDownloadBehavior({ policy: 'allow', downloadPath: downloads });
  await popup.click('#jsonButton'); await popup.click('#txtButton');
  await until(async () => { try { await fs.access(path.join(downloads, 'mon-gpt-observations.json')); await fs.access(path.join(downloads, 'mon-gpt-urls.txt')); return true; } catch { return false; } }, 'exports');
  const exported = JSON.parse(await fs.readFile(path.join(downloads, 'mon-gpt-observations.json'), 'utf8'));
  assert.equal(exported.schemaVersion, 2); assert.equal(exported.conversations.length, 15);
  assert.equal(exported.projects.length, 1); assert.equal(exported.projects[0].observedName, null);
  assert.ok((await fs.readFile(path.join(downloads, 'mon-gpt-urls.txt'), 'utf8')).trim() === expected);
  pass('Téléchargements JSON/TXT réels relus : contrat v2, 15 UUID, une URL observée par ligne, projet sans nom honnête');
  await popup.click('#clearButton'); assert.ok(await popup.$eval('#clearDialog', e => e.open));
  await popup.keyboard.press('Escape'); assert.equal(await popup.$eval('#clearDialog', e => e.open), false);
  assert.equal(Object.keys((await state()).records).length, 15);
  pass('Confirmation de vidage affichée ; Échap annule sans modification');
  await worker.evaluate(() => { globalThis.recipeOriginalSet = chrome.storage.local.set; chrome.storage.local.set = async () => { throw Error('Quota fictif de recette : données conservées.'); }; });
  await popup.click('#scanButton');
  await popup.waitForFunction(() => document.getElementById('status').classList.contains('error') && document.getElementById('status').textContent.includes('Quota fictif'));
  assert.equal((await state()).records[ID].seenCount, 2);
  await checkpoint('05-erreur-stockage');
  await worker.evaluate(() => { chrome.storage.local.set = globalThis.recipeOriginalSet; delete globalThis.recipeOriginalSet; });
  await popup.click('#scanButton'); await until(async () => (await state()).records[ID].seenCount === 3, 'reprise après échec');
  pass('Échec de stockage injecté dans le profil fictif : erreur visible, aucune perte, nouvelle tentative réussie');
  await chooseMode('targeted'); await popup.close();
  // Remise à zéro par l’API du dépôt isolé, distincte d’un clic destructif UI.
  await worker.evaluate(() => repository.clear());
  await page.evaluate(id => history.pushState({}, '', '/c/' + id), ID);
  await until(async () => Object.keys((await state()).records).length === 1, 'auto cible');
  await sleep(800); assert.equal((await state()).records[ID].seenCount, 1);
  await page.click('#rename'); await until(async () => (await state()).records[ID].title.includes('actualisé'), 'titre muté');
  await page.click('#route'); await until(async () => Object.keys((await state()).records).length === 2, 'route SPA');
  pass('Auto cible : uniquement URL courante ; mutation de titre et route SPA détectées sans double comptage');
  await openPopup(); await chooseMode('broad');
  await until(async () => Object.keys((await state()).records).length === 15, 'auto large');
  await popup.close(); await page.click('#add');
  await until(async () => Object.keys((await state()).records).length === 16, 'lien ajouté au DOM');
  await openPopup(); await popup.$eval('#conversationList', e => { e.scrollTop = e.scrollHeight; });
  await checkpoint('03-auto-large-fin');
  pass('Auto large : sidebar rendue, nouvelle mutation, liste scrollable jusqu’au dernier élément');
  const modeState = await state(); assert.equal(modeState.mode, 'broad');
  assert.ok(controlled.requests.every(url => url === 'https://chatgpt.com/' || url === 'https://chatgpt.com/favicon.ico'), 'Aucune requête supplémentaire : ' + JSON.stringify(controlled.requests));
  const other = await browser.newPage(); await other.goto('about:blank'); await openPopup(other);
  assert.equal(await popup.$eval('#scanButton', e => e.disabled), true);
  await checkpoint('04-page-non-compatible');
  pass('Autre onglet/domaine : scan désactivé, exports disponibles, collecte suspendue');
  await chooseMode('manual'); await popup.close();
  const saved = await state();
  // API de la page interne de Chrome, jamais une permission de l’extension.
  const manager = await browser.newPage(); await manager.goto('chrome://extensions');
  await manager.evaluate(id => chrome.management.setEnabled(id, false), extensionId);
  assert.equal(await manager.evaluate(async id => (await chrome.management.get(id)).enabled, extensionId), false);
  await manager.evaluate(id => chrome.management.setEnabled(id, true), extensionId);
  // Nouveau contexte après réactivation : ne pas réutiliser le handle CDP du worker arrêté.
  const resumed = await browser.newPage(); await resumed.goto(`chrome-extension://${extensionId}/ui/popup.html`);
  await resumed.waitForFunction(() => document.getElementById('total').textContent === '16');
  const resumedState = await resumed.evaluate(async key => (await chrome.storage.local.get(key))[key], KEY);
  assert.deepEqual(resumedState.records, saved.records); assert.equal(resumedState.mode, 'manual');
  await resumed.close();
  await manager.close();
  pass('Désactivation/réactivation par Chrome : mode et 16 observations conservés, sans permission management dans l’extension');
  await browser.close(); browser = null; popup = null;
  await launch(false); current = await state();
  assert.equal(current.mode, 'manual'); assert.equal(Object.keys(current.records).length, 16);
  assert.deepEqual(current.records, saved.records);
  pass('Redémarrage réel de Chrome et rechargement CDP : même ID, mode Manuel et 16 observations conservés');
  page = (await browser.pages())[0]; await page.goto('about:blank');
  await openPopup(); await popup.click('#clearButton');
  assert.ok(await popup.$eval('#clearDialog', e => e.open));
  await popup.click('#confirmClear');
  await until(async () => Object.keys((await state()).records).length === 0, 'vidage fictif confirmé');
  assert.equal((await state()).mode, 'manual');
  pass('Vidage confirmé dans la vraie popup : seules les observations fictives sont retirées, mode conservé');
  await popup.close();
  for (const tab of await browser.pages()) if (tab !== page) await tab.close();
  const projectsFixture = await fixture('https://chatgpt.com/', 'projects.html'); await page.close(); page = projectsFixture.page;
  await sleep(600); assert.equal(Object.keys((await state()).entities).length, 0);
  const projectDomBefore = await page.content();
  await openPopup(); await popup.click('#scanButton');
  await until(async () => Object.keys((await state()).entities).length === 4, 'quatre projets fictifs');
  current = await state();
  assert.equal(Object.keys(current.records).length, 3);
  assert.equal(current.entities[A].name, 'Développement'); assert.equal(current.entities[B].name, 'Développement');
  assert.equal(current.entities[B].evidence.kind, 'expanded-group'); assert.equal(current.entities[C].name, null);
  assert.equal(current.entities[D].name, 'Été — Recherche & idées'); assert.equal(Object.keys(current.entities).length, 4);
  assert.equal(await page.content(), projectDomBefore); assert.ok(!JSON.stringify(current).includes('INTERDIT'));
  await popup.waitForFunction(() => document.querySelectorAll('.project-row').length === 4);
  assert.ok((await popup.$eval('#projectsSummary', el => el.textContent)).includes('3 nommé(s) · 1 sans nom'));
  await checkpoint('01-projets-homonymes');
  pass('Projets : deux Développement distincts par clé, preuve directe et groupe explicite, trois noms connus / un inconnu, aucun message ni lien caché collecté');
  const projectDownloads = path.join(PROFILE, 'exports-projets-fictifs'); await fs.mkdir(projectDownloads, { recursive: true });
  await browser.defaultBrowserContext().setDownloadBehavior({ policy: 'allow', downloadPath: projectDownloads });
  await popup.click('#jsonButton');
  const projectExport = path.join(projectDownloads, 'mon-gpt-observations.json');
  await until(async () => { try { await fs.access(projectExport); return true; } catch { return false; } }, 'export projets');
  const projectData = JSON.parse(await fs.readFile(projectExport, 'utf8'));
  assert.equal(projectData.schemaVersion, 2); assert.equal(projectData.projects.length, 4); assert.equal(projectData.conversations.length, 3);
  assert.deepEqual(projectData.conversations.find(c => c.conversationId.endsWith('901')).observedProjectKeys, [A, B]);
  assert.equal(projectData.projects.filter(p => p.observedName === 'Développement').length, 2);
  await chooseMode('broad'); await popup.close(); await page.click('#renameA');
  await until(async () => (await state()).entities[A].name === 'Développement solaire', 'nom direct muté');
  await page.click('#toggleB'); await page.click('#renameB'); await sleep(700);
  assert.equal((await state()).entities[B].name, 'Développement');
  await openPopup(); await checkpoint('02-projets-renommes-replies'); await popup.close();
  await page.click('#toggleB'); await until(async () => (await state()).entities[B].name === 'Développement secret', 'groupe rouvert');
  assert.equal(Object.keys((await state()).entities).length, 4);
  pass('Renommages en Auto large : même clé, aucune duplication ; groupe replié sans fausse mise à jour, enrichissement après réouverture manuelle');
  await page.click('#openUnknown'); await until(async () => (await state()).entities[C].name === 'Carnets d’hiver', 'nom sur accueil projet');
  assert.equal((await state()).entities[C].evidence.kind, 'project-page');
  await openPopup(); await checkpoint('03-projets-accueil');
  await chooseMode('manual'); await popup.close(); await worker.evaluate(() => repository.clear());
  await openPopup(); await chooseMode('targeted');
  await until(async () => Object.keys((await state()).entities).length === 1, 'cible projet seul');
  assert.equal(Object.keys((await state()).records).length, 0); assert.equal((await state()).entities[C].name, 'Carnets d’hiver');
  await popup.waitForFunction(() => !document.getElementById('jsonButton').disabled && document.getElementById('copyButton').disabled);
  await checkpoint('04-projets-cible-seule');
  pass('Accueil projet : nom depuis H1 sur URL projet ; Auto cible conserve seulement ce projet, export JSON actif même sans conversation');
  await chooseMode('manual'); await popup.close();
  assert.ok(projectsFixture.requests.every(url => url === 'https://chatgpt.com/' || url === 'https://chatgpt.com/favicon.ico'));
  // Diagnostic du site réel dans ce profil neuf, sans connexion et sans aucun geste de compte.
  const live = await browser.newPage(); let liveStatus = 'PARTIEL : diagnostic ChatGPT réel indisponible';
  try {
    await live.goto('https://chatgpt.com/', { waitUntil: 'domcontentloaded', timeout: 20000 });
    const count = await live.$$eval('nav a[href*="/c/"], aside a[href*="/c/"]', list => list.length);
    liveStatus = 'PARTIEL : site ChatGPT réel chargé dans le profil neuf, ' + count + ' lien(s) de discussion observables ; aucun compte personnel utilisé.';
  } catch { liveStatus = 'PARTIEL : page ChatGPT réelle non exploitable dans le profil neuf ; aucune authentification ni barrière contournée.'; }
  log.push(liveStatus); console.log(liveStatus); await live.close();
  await fs.writeFile(path.join(REPORT, 'recette-chrome.txt'), log.join('\n') + '\n');
  await browser.close(); browser = null;
})().catch(async error => {
  console.error(error.stack || error); process.exitCode = 1;
  await fs.mkdir(REPORT, { recursive: true });
  await fs.writeFile(path.join(WORK, 'erreur-recette.txt'), log.join('\n') + '\n' + error.stack);
  if (browser) await browser.close();
});
