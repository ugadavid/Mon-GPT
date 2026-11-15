'use strict';
// Génère un diagnostic local à lire avant de l’exécuter dans la console du
// Chrome connecté. Ne franchit aucune protection Chrome, n’ouvre aucun profil.
// Le script généré ne lit que navigation/titres de projet et URL courante.
// Aucune écriture DOM, stockage, réseau ou export personnel sur disque.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const core = fs.readFileSync(path.join(root, 'core/observations.js'), 'utf8');
const adapter = fs.readFileSync(path.join(root, 'adapters/chatgpt.js'), 'utf8');
const previous = execFileSync('git', ['show', '5c099d0acf3d9c8c1a695d2e3c71b8373a748fc0:companions/chatgpt-collector/adapters/chatgpt.js'], { cwd: root, encoding: 'utf8' });
const wrap = (source, dependency = '') => `(() => { const module = { exports: {} }; ${dependency}\n${source}\nreturn module.exports; })()`;
const dependency = `const require = name => { if (name !== '../core/observations.js') throw Error('Dépendance inattendue'); return core; };`;
const script = `(() => {
'use strict';
const core = ${wrap(core)};
const adapter = ${wrap(adapter, dependency)};
const previous = ${wrap(previous, dependency)};
if (location.origin !== 'https://chatgpt.com') throw Error('Onglet ChatGPT requis');
const clean = value => value.replace(/\\s+/g, ' ').trim();
const selector = '[data-app-action-sidebar-project-row][data-app-action-sidebar-project-id]';
const ownerSelector = '[data-sidebar-project-kind="local"][data-sidebar-project-container-id]';
const controls = [...document.querySelectorAll(selector)].filter(node => node.closest('nav, aside, [role="navigation"]') && node.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}) && !node.closest('[hidden], [inert], [aria-hidden="true"]'));
const seen = new Set(), expected = [];
for (const control of controls) {
  const key = control.getAttribute('data-app-action-sidebar-project-id');
  const name = control.getAttribute('data-app-action-sidebar-project-label');
  const label = document.getElementById(control.getAttribute('aria-labelledby'));
  const owner = control.closest(ownerSelector);
  if (!key || !name || !label || !control.contains(label) || !owner || owner.getAttribute('data-sidebar-project-container-id') !== 'project:' + key || seen.has(key)) continue;
  const rendered = [...label.querySelectorAll('[data-marquee-content]')].filter(node => node.checkVisibility()).map(node => clean(node.textContent));
  if (!rendered.length || !rendered.every(text => text === clean(name))) continue;
  const links = [...owner.querySelectorAll('a[href*="/c/"]')].filter(node => node.closest(ownerSelector) === owner && !node.closest('[hidden], [inert], [aria-hidden="true"]') && node.checkVisibility()).map(node => node.getAttribute('href'));
  seen.add(key); expected.push({key,name:clean(name),links});
}
const now = new Date().toISOString(), batch = adapter.scanBatch(document, window, 'broad');
const state = core.merge(core.empty('chatgpt'), batch.observations, now, {entities:batch.entities,normalize:adapter.normalize,normalizeEntity:adapter.normalizeEntity});
// Vrai export de production, sérialisé/relu exclusivement en mémoire.
const exported = JSON.parse(JSON.stringify(adapter.exportJson(state, now)));
const baseline = previous.scanBatch(document, window, 'broad');
const checks = expected.filter(item => item.links.length > 0).slice(0, 2).map((item,index) => {
  const project = exported.projects.find(p => p.projectKey === item.key);
  const linked = item.links.map(href => {
    const url = new URL(href, location.origin), match = url.pathname.match(/^\\/g\\/([^/]+)\\/c\\/([0-9a-f-]{36})\\/?$/i);
    if (url.origin !== 'https://chatgpt.com' || !match || match[1] !== item.key) return false;
    return exported.conversations.some(c => c.conversationId === match[2].toLowerCase() && c.observedProjectKeys.includes(item.key));
  });
  return {alias:'Projet '+String.fromCharCode(65+index),keyExact:project?.projectKey===item.key,nameExactAgainstRendered:project?.observedName===item.name,evidenceDirect:project?.evidence.kind==='direct-control',linkedConversationCount:item.links.length,allLinkedConversationsCorrect:linked.every(Boolean)};
});
const uniqueKeys = new Set(exported.projects.map(p => p.projectKey)).size === exported.projects.length;
return JSON.stringify({version:'0.8.2',checkedAt:now,readOnly:true,exportOnDisk:false,originVerified:true,exportSchemaVersion:exported.schemaVersion,nativeControls:controls.length,baselineNamedProjects:baseline.entities.filter(p=>p.name!==null).length,correctedNamedProjects:exported.projects.filter(p=>p.observedName!==null).length,checkedProjectCount:checks.length,checks,allProjectKeysDistinct:uniqueKeys,GO:checks.length===2&&checks.every(c=>c.keyExact&&c.nameExactAgainstRendered&&c.evidenceDirect&&c.allLinkedConversationsCorrect)&&uniqueKeys});
})()`;
const output = path.join(root, '.recette', 'connected-probe-readonly.js');
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, script);
console.log(JSON.stringify({ script: output, bytes: Buffer.byteLength(script), privateDataEmbedded: false }));
