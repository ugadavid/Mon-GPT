'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const View = require('../ui/presentation.js');
test('Présentation commune bornée, titre long disponible, inconnu explicite et aucun UUID mural', () => {
  const input = Array.from({ length: 100 }, (_, n) => ({ identity: 'fictif-' + n, title: n ? 'Titre fictif '.repeat(30) : null, url: 'https://example.test/' + n, contexts: [], active: false, seenCount: 2, lastSeenAt: '2026-11-15T12:00:00.000Z' }));
  const rows = View.listModel(input); assert.equal(rows.length, 50);
  assert.equal(rows[0].title, 'Titre non observé'); assert.ok(rows[1].title.length > 100); assert.equal(rows[0].context, 'Lien de discussion');
  assert.equal(rows[0].identity, undefined);
});
test('Popup : libellés, radios, statut accessible, confirmation distincte et rendu sûr', () => {
  const base = path.resolve(__dirname, '../ui'); const html = fs.readFileSync(path.join(base, 'popup.html'), 'utf8'); const js = fs.readFileSync(path.join(base, 'presentation.js'), 'utf8');
  assert.match(html, /lang="fr"/); assert.match(html, /role="status" aria-live="polite"/);
  assert.equal((html.match(/name="collectionMode"/g) || []).length, 3);
  for (const id of ['scanButton', 'copyButton', 'jsonButton', 'txtButton', 'clearDialog', 'cancelClear', 'confirmClear']) assert.ok(html.includes(`id="${id}"`));
  assert.doesNotMatch(js, /innerHTML|insertAdjacentHTML/); assert.match(js, /title\.textContent = item\.title/);
  assert.doesNotMatch(js, /ChatGPT|chatgpt\.com/, 'le composant partagé ne dépend pas du site');
  assert.match(html, /La collecte ne garantit pas l’exhaustivité/);
});
