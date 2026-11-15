'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Adapter = require('../adapters/chatgpt.js');
const ID = '11111111-2222-4333-8444-555555555555';
const OTHER = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';
// Mini DOM statique adapté du test 3GPT3, sans bibliothèque DOM à l’exécution.
function staticDocument(html) {
  const links = [];
  for (const match of html.matchAll(/<a\s+([^>]*)>([\s\S]*?)<\/a>/g)) {
    const attrs = {};
    for (const attr of match[1].matchAll(/([^\s=]+)(?:="([^"]*)")?/g)) attrs[attr[1]] = attr[2] ?? '';
    const content = match[2].replace(/<[^>]+>/g, '').trim();
    links.push({ nodeType: 1, childNodes: [{ nodeType: 3, nodeValue: content }],
      getAttribute: key => Object.hasOwn(attrs, key) ? attrs[key] : null,
      hasAttribute: key => Object.hasOwn(attrs, key),
      checkVisibility: () => !Object.hasOwn(attrs, 'hidden'), closest: () => null, matches: () => false });
  }
  const sidebar = { closest: () => null, checkVisibility: () => true,
    querySelectorAll: selector => {
      const targeted = selector.match(/\/c\/([0-9a-f-]{36})/i);
      return links.filter(a => targeted ? a.getAttribute('href')?.toLowerCase().includes('/c/' + targeted[1].toLowerCase()) : a.getAttribute('href')?.includes('/c/'));
    } };
  return { querySelectorAll: () => html.includes('<nav') ? [sidebar] : [] };
}
const win = href => ({ location: { href } });
test('Scanner 3GPT3 adapté : aria puis texte, projets, actif, titre inconnu', () => {
  const doc = staticDocument(`<nav><a data-sidebar-item data-active href="/c/${ID}" aria-label="Un jardin fictif">Fallback</a><a href="/g/g-p-FICTIF/c/${OTHER}"> Carnet d’hiver </a><a href="/c/00000000-0000-4000-8000-000000000003"></a></nav>`);
  const found = Adapter.scan(doc, win('https://chatgpt.com/'));
  assert.equal(found.length, 3); assert.equal(found[0].title, 'Un jardin fictif'); assert.equal(found[0].titleQuality, 2); assert.equal(found[0].active, true);
  assert.equal(found[1].title, 'Carnet d’hiver'); assert.equal(found[1].context, 'g-p-FICTIF'); assert.equal(found[2].title, null);
});
test('Scanner : UUID sans lien, domaine piégé, caché et DOM absent ne sont pas collectés', () => {
  const doc = staticDocument(`<nav><p>${ID}</p><a href="https://chatgpt.com.evil/c/${ID}">Faux</a><a hidden href="/c/${OTHER}">Caché</a><a href="javascript:alert(1)">Danger</a></nav>`);
  assert.deepEqual(Adapter.scan(doc, win('https://chatgpt.com/')), []);
  assert.deepEqual(Adapter.scan(staticDocument('<p>Projet fermé ou virtualisé</p>'), win('https://chatgpt.com/')), []);
  assert.deepEqual(Adapter.scan(doc, win('https://example.test/')), []);
});
test('Auto cible : aucun parcours large, seulement l’URL courante ; manuel/large voient les liens', () => {
  const doc = staticDocument(`<nav><a href="/c/${ID}">Actuelle</a><a href="/c/${OTHER}">Autre</a></nav>`);
  assert.equal(Adapter.scan(doc, win('https://chatgpt.com/c/' + ID), 'targeted').length, 1);
  assert.equal(Adapter.scan(doc, win('https://chatgpt.com/'), 'targeted').length, 0);
  assert.equal(Adapter.scan(doc, win('https://chatgpt.com/'), 'broad').length, 2);
  const missing = Adapter.scan(staticDocument(''), win('https://chatgpt.com/c/' + ID), 'targeted');
  assert.equal(missing[0].title, null); assert.equal(missing[0].active, true);
});
test('URLs de projet et globale conservées, doublons de nœuds neutralisés', () => {
  const doc = staticDocument(`<nav><a href="/c/${ID}">Fictif</a><a href="/c/${ID}">Fictif</a><a href="/g/g-p-FICTIF/c/${ID}">Fictif</a></nav>`);
  const found = Adapter.scan(doc, win('https://chatgpt.com/')); assert.equal(found.length, 2);
  assert.equal(new Set(found.map(o => o.identity)).size, 1);
});
test('Manifest et code : permissions minimales, pas d’injection UI ou collecte de contenu', () => {
  const base = path.resolve(__dirname, '..'); const manifest = JSON.parse(fs.readFileSync(path.join(base, 'manifest.json')));
  assert.equal(manifest.manifest_version, 3); assert.deepEqual(manifest.permissions, ['storage']);
  assert.deepEqual(manifest.content_scripts[0].matches, ['https://chatgpt.com/*']); assert.equal(manifest.content_scripts[0].all_frames, false);
  assert.equal(manifest.host_permissions, undefined); assert.equal(manifest.web_accessible_resources, undefined);
  for (const file of manifest.content_scripts[0].js) {
    const code = fs.readFileSync(path.join(base, file), 'utf8');
    assert.doesNotMatch(code, /\bfetch\s*\(|XMLHttpRequest|sendBeacon|innerHTML|__react|document\.title|document\.cookie|\.appendChild\(/);
  }
  for (const size of ['16', '32', '48', '128']) assert.ok(fs.existsSync(path.join(base, manifest.icons[size])));
});
