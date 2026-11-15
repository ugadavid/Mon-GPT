'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const Core = require('../core/observations.js');
const Adapter = require('../adapters/chatgpt.js');
const { createRepository, KEY } = require('../browser/repository.js');
const T1 = '2026-11-15T12:00:00.000Z', T2 = '2026-11-15T12:05:00.000Z';
const ID = '11111111-2222-4333-8444-555555555555';
const ID2 = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee';
const link = (id = ID, extra = {}) => ({ source: 'chatgpt', identity: id, url: 'https://chatgpt.com/c/' + id, title: 'Un jardin fictif', titleQuality: 2, active: false, context: null, ...extra });
test('URL : UUID strict, hôte exact, URL de projet, query conservée et fragment retiré', () => {
  const raw = ` https://CHATGPT.COM/g/g-p-FICTIF/c/${ID.toUpperCase()}/?index=2#fin `;
  assert.deepEqual(Adapter.parseUrl(raw), { identity: ID, url: `https://chatgpt.com/g/g-p-FICTIF/c/${ID.toUpperCase()}?index=2`, context: 'g-p-FICTIF' });
  for (const raw of [`http://chatgpt.com/c/${ID}`, `https://chatgpt.com.evil/c/${ID}`, `https://evil.chatgpt.com/c/${ID}`, `https://user@chatgpt.com/c/${ID}`, `https://chatgpt.com:443/c/${ID}`, `https://chatgpt.com/share/${ID}`, `https://chatgpt.com/a/../c/${ID}`, `https://chatgpt.com/c/${ID}/suite`, 'javascript:alert(1)', `https://chat.openai.com/c/${ID}`, `https://chatgpt.com/g/a.b/c/${ID}`, 'https://chatgpt.com/c/texte']) assert.throws(() => Adapter.parseUrl(raw), raw);
});
test('Accord avec le validateur Python existant sur les URLs admises et refusées', () => {
  const corpus = [`https://chatgpt.com/c/${ID}`, `https://chatgpt.com/g/g-p-FICTIF/c/${ID.toUpperCase()}/?index=1#bas`, `https://chatgpt.com/c/${ID}?`, `https://chatgpt.com:443/c/${ID}`, `https://chatgpt.com/a/../c/${ID}`, `https://chatgpt.com.evil/c/${ID}`, `https://chatgpt.com/c/${ID}/suite`];
  const result = spawnSync('python', ['-c', 'import json,sys\nfrom mon_gpt.chatgpt import parse_url\na=[]\nfor s in json.load(sys.stdin):\n try: a.append(list(parse_url(s)))\n except ValueError: a.append(None)\nprint(json.dumps(a))'], { input: JSON.stringify(corpus), cwd: path.resolve(__dirname, '../../..'), encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  const actual = corpus.map(url => { try { const o = Adapter.parseUrl(url); return [o.identity, o.url]; } catch { return null; } });
  assert.deepEqual(actual, JSON.parse(result.stdout));
});
test('Une fiche par UUID : deux URLs, plusieurs occurrences et titres égaux distincts', () => {
  const first = link(), project = link(ID, { url: `https://chatgpt.com/g/g-p-fictif/c/${ID}`, title: null });
  const state = Core.merge(Core.empty('chatgpt'), [first, first, project, link(ID2)], T1, { normalize: Adapter.normalize });
  assert.equal(Object.keys(state.records).length, 2); assert.equal(state.records[ID].seenCount, 1);
  assert.equal(state.records[ID].observedUrls.length, 2); assert.deepEqual(state.records[ID].contexts, ['g-p-fictif']);
  assert.equal(state.records[ID].title, first.title); assert.equal(state.lastScan.newCount, 2);
  const second = Core.merge(state, [project], T2, { normalize: Adapter.normalize });
  assert.equal(second.records[ID].seenCount, 2); assert.equal(second.records[ID].firstSeenAt, T1); assert.equal(second.records[ID].lastSeenAt, T2);
  assert.equal(second.lastScan.existingCount, 1); assert.equal(state.records[ID].seenCount, 1, 'fusion pure');
});
test('Titre fidèle : null reste inconnu, aria prioritaire, titre récent et champs non prévus absents', () => {
  let state = Core.merge(Core.empty('chatgpt'), [link(ID, { title: null, cookie: 'INTERDIT', prompt: 'INTERDIT', token: 'INTERDIT' })], T1, { normalize: Adapter.normalize });
  assert.equal(state.records[ID].title, null);
  state = Core.merge(state, [link(ID, { title: '  Titre\n réel  ', titleQuality: 2 })], T2, { normalize: Adapter.normalize });
  state = Core.merge(state, [link(ID, { title: 'Texte moins précis', titleQuality: 1 })], T2, { normalize: Adapter.normalize });
  assert.equal(state.records[ID].title, 'Titre réel');
  assert.ok(!JSON.stringify(Adapter.exportJson(state, T2)).includes('INTERDIT'));
});
test('Contrat JSON déterministe, whitelist, TXT = URL observée par ligne', () => {
  const state = Core.merge(Core.empty('chatgpt'), [link(ID2, { title: null }), link()], T1, { normalize: Adapter.normalize });
  const data = Adapter.exportJson(state, T2);
  assert.equal(data.source, 'mon-gpt-collector'); assert.equal(data.schemaVersion, 2); assert.deepEqual(data.projects, []); assert.equal(data.conversations[0].conversationId, ID);
  assert.equal(data.conversations[1].observedTitle, null);
  assert.deepEqual(Object.keys(data.conversations[0]), ['conversationId', 'url', 'observedTitle', 'firstSeenAt', 'lastSeenAt', 'seenCount', 'observedUrls', 'observedProjectKeys', 'lastObservedActive']);
  assert.equal(JSON.stringify(Adapter.exportJson(state, T2)), JSON.stringify(data));
  assert.deepEqual(Core.urlsText(state).split('\n'), data.conversations.map(r => r.url));
});
test('Deux alias au même scan : garder le titre accessible actif, sans inventer un contexte trop long', () => {
  const active = link(ID, { title: 'Titre actuel fictif', active: true });
  const alias = link(ID, { url: `https://chatgpt.com/g/g-p-fictif/c/${ID}`, title: 'Ancien alias fictif' });
  const state = Core.merge(Core.empty('chatgpt'), [active, alias], T1, { normalize: Adapter.normalize });
  assert.equal(state.records[ID].title, active.title);
  assert.equal(state.records[ID].active, true);
  assert.equal(Adapter.parseUrl(`https://chatgpt.com/g/${'a'.repeat(129)}/c/${ID}`).context, null);
});
test('Limites et corruption : refus atomique, aucune suppression ou normalisation de date inventée', () => {
  const state = Core.merge(Core.empty('chatgpt'), [link()], T1, { normalize: Adapter.normalize });
  const before = JSON.stringify(state);
  assert.throws(() => Core.merge(state, [link(ID2)], T2, { normalize: Adapter.normalize, limits: { ...Core.LIMITS, records: 1 } }), /Limite/);
  assert.throws(() => Core.merge(state, [link()], T2, { normalize: Adapter.normalize, limits: { ...Core.LIMITS, bytes: 1 } }), /Limite/);
  for (const bad of ['pas une date', '2026-02-31T00:00:00.000Z', null]) assert.throws(() => Core.merge(state, [link()], bad));
  const broken = structuredClone(state); broken.records[ID].observedUrls = [`https://chatgpt.com/c/${ID2}`];
  assert.throws(() => Adapter.exportJson(broken, T2));
  broken.records[ID].observedUrls = [link().url]; broken.records[ID].seenCount = -1; assert.throws(() => Adapter.exportJson(broken, T2));
  assert.throws(() => Core.observation({ source: 'fictif', identity: '__proto__', url: 'https://example.test/a' }));
  assert.throws(() => Core.observation({ url: 'https://example.test/a' }));
  assert.equal(JSON.stringify(state), before);
});
test('Bornes de variantes : aucune URL évincée silencieusement', () => {
  let state = Core.empty('chatgpt');
  for (let n = 0; n < 10; n++) state = Core.merge(state, [link(ID, { url: link().url + '?index=' + n })], T1, { normalize: Adapter.normalize });
  assert.throws(() => Core.merge(state, [link(ID, { url: link().url + '?index=11' })], T2, { normalize: Adapter.normalize }), /Limite/);
  assert.equal(state.records[ID].observedUrls.length, 10);
});
test('Même API pure sur deux sources fictives, sans site, DOM ni Chrome', () => {
  const input = [
    { source: 'chatgpt', identity: ID, url: link().url, title: 'Fictif ChatGPT' },
    { source: 'atelier-fictif', identity: 'planche-42', url: 'https://example.test/oeuvres/42', title: 'Fictif non ChatGPT' }
  ];
  for (const observation of input) {
    const state = Core.merge(Core.empty(observation.source), [observation, observation], T1);
    assert.equal(Object.keys(state.records).length, 1); assert.equal(state.records[observation.identity].seenCount, 1);
    assert.equal(Core.exportData(state, T2).observations[0].identity, observation.identity);
  }
});
function memory() {
  let data = {}, fail = false;
  return { get: async key => structuredClone({ [key]: data[key] }), set: async value => { if (fail) throw Error('Quota fictif'); data = { ...data, ...structuredClone(value) }; }, snapshot: () => structuredClone(data), fail: value => { fail = value; } };
}
test('Pont : écritures de plusieurs onglets sérialisées, requête répétée idempotente', async () => {
  const storage = memory(), repository = createRepository(storage, { source: 'chatgpt', normalize: Adapter.normalize, now: () => T1 });
  await Promise.all([repository.ingest({ observations: [link()], entities: [] }, 'onglet-A', 'manual'), repository.ingest({ observations: [link(ID2)], entities: [] }, 'onglet-B', 'manual')]);
  await repository.ingest({ observations: [link()], entities: [] }, 'onglet-A', 'manual');
  const { state } = await repository.get(); assert.equal(Object.keys(state.records).length, 2); assert.equal(state.records[ID].seenCount, 1);
  assert.deepEqual(Object.keys(storage.snapshot()), [KEY]);
});
test('Pont : modes persistants, échec visible, reprise et vidage limité à la clé dédiée', async () => {
  const storage = memory(); await storage.set({ autreExtension: { intact: true } });
  const repository = createRepository(storage, { source: 'chatgpt', normalize: Adapter.normalize, now: () => T1 });
  assert.equal((await repository.get()).state.mode, 'targeted'); await repository.setMode('manual');
  assert.equal((await createRepository(storage, { source: 'chatgpt', normalize: Adapter.normalize }).get()).state.mode, 'manual');
  storage.fail(true); await assert.rejects(repository.ingest({ observations: [link()], entities: [] }, 'fail', 'manual'), /Quota/); storage.fail(false);
  assert.match((await repository.get()).error, /Quota/); assert.equal(Object.keys((await repository.get()).state.records).length, 0);
  await repository.ingest({ observations: [link()], entities: [] }, 'retry', 'manual'); await repository.clear();
  assert.equal((await repository.get()).state.mode, 'manual'); assert.deepEqual(storage.snapshot().autreExtension, { intact: true });
  assert.equal(Object.keys((await repository.get()).state.records).length, 0);
});
