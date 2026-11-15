'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const Core = require('../core/observations.js');
const Adapter = require('../adapters/chatgpt.js');
const { createRepository, KEY } = require('../browser/repository.js');
const { documentFrom } = require('./helpers/dom.cjs');
const A = 'g-p-11111111111111111111111111111111', B = 'g-p-22222222222222222222222222222222';
const C = 'g-p-33333333333333333333333333333333', ID = '11111111-2222-4333-8444-555555555555';
const T1 = '2026-11-15T12:00:00.000Z', T2 = '2026-11-15T12:05:00.000Z';
const win = href => ({ location: { href: href || 'https://chatgpt.com/' } });
const project = (identity = A, name = 'Développement', kind = 'direct-link') => ({ source: 'chatgpt', identity, name, evidence: { kind, url: kind === 'direct-control' ? null : 'https://chatgpt.com/g/' + identity + (kind === 'expanded-group' ? '/c/' + ID : '/project') } });
const options = entities => ({ normalize: Adapter.normalize, normalizeEntity: Adapter.normalizeEntity, entities });
test('Preuves directes : deux homonymes, clé sur lien ou contrôle, titres localisés et exclusion des actions', () => {
  const doc = documentFrom(`<nav><a href="/g/${A}/project">Développement</a><button data-project-id="${B}">Développement<button data-trailing-button aria-label="Ouvrir les options du projet pour Développement"></button></button><a href="/g/${C}/project" aria-label="Ouvrir l’accueil du projet"></a></nav>`);
  const projects = Adapter.scanProjects(doc, win());
  assert.equal(projects.length, 3); assert.deepEqual(projects.map(p => p.name), ['Développement', 'Développement', null]);
  assert.notEqual(projects[0].identity, projects[1].identity);
  const english = Adapter.scanProjects(documentFrom(`<nav><a href="/g/${A}/project" aria-label="Été — Recherche &amp; idées"></a></nav>`), win());
  assert.equal(english[0].name, 'Été — Recherche & idées');
});
test('Groupes explicites : enfants concordants, homonymes, groupe replié et voisinage incertain', () => {
  const doc = documentFrom(`<nav><button id="a" aria-expanded="true" aria-controls="ga">Développement</button><div role="group" id="ga" aria-labelledby="a"><a href="/g/${A}/c/${ID}">Titre de fil jamais projet</a></div><div role="treeitem" aria-expanded="true"><span>Développement</span><div role="group"><a href="/g/${B}/c/${ID}">Autre fil</a></div></div><button aria-expanded="false">Projet replié</button><a href="/g/${C}/c/${ID}">Un voisin sans relation</a></nav>`);
  const found = Adapter.scanProjects(doc, win());
  assert.equal(found.find(p => p.identity === A).name, 'Développement');
  assert.equal(found.find(p => p.identity === B).name, 'Développement');
  assert.equal(found.find(p => p.identity === C).name, null);
  assert.equal(found.find(p => p.identity === A).evidence.kind, 'expanded-group');
});
test('Aucune supposition : groupes mixtes, sections imbriquées, conflit, faux domaine et titre de fil', () => {
  const mixed = documentFrom(`<nav><button id="a" aria-expanded="true" aria-controls="g">Mauvais nom</button><div id="g" role="group" aria-labelledby="a"><a href="/g/${A}/c/${ID}">Fil A</a><a href="/g/${B}/c/${ID}">Fil B</a></div><a data-project-id="${C}" href="/g/${C}/c/${ID}">Ne pas utiliser comme nom</a><a href="https://chatgpt.com.evil/g/${C}/project">Faux domaine</a></nav>`);
  assert.ok(Adapter.scanProjects(mixed, win()).every(p => p.name === null));
  const conflict = documentFrom(`<nav><a href="/g/${A}/project">Un nom</a><a href="/g/${A}/project">Un autre nom</a><button data-project-id="${A}" data-project-key="${B}">Contradictoire</button></nav>`);
  assert.equal(Adapter.scanProjects(conflict, win())[0].name, null);
  const nested = documentFrom(`<nav><button id="s" aria-controls="g" aria-expanded="true">Projets</button><div id="g" role="group" aria-labelledby="s"><button aria-expanded="true">Projet interne</button><a href="/g/${A}/c/${ID}">Fil</a></div></nav>`);
  assert.equal(Adapter.scanProjects(nested, win())[0].name, null);
});
test('Page projet : un H1 propre sur URL projet ; jamais le H1 d’une conversation ni un titre ambigu', () => {
  const doc = documentFrom('<main><h1>Été, idées et découvertes</h1><p>PROMPT_INTERDIT</p></main>');
  assert.equal(Adapter.scanProjects(doc, win('https://chatgpt.com/g/' + A + '/project'))[0].name, 'Été, idées et découvertes');
  assert.equal(Adapter.scanProjects(doc, win('https://chatgpt.com/g/' + A + '/c/' + ID))[0].name, null);
  assert.equal(Adapter.scanProjects(documentFrom('<main><h1>Un</h1><h1>Deux</h1></main>'), win('https://chatgpt.com/g/' + A))[0].name, null);
});
test('Auto cible : seulement projet courant, enrichissement sans collecte des autres projets rendus', () => {
  const doc = documentFrom(`<nav><a href="/g/${A}/project">Actuel</a><a href="/g/${B}/project">Autre</a><a href="/g/${A}/c/${ID}">Fil</a></nav>`);
  const batch = Adapter.scanBatch(doc, win('https://chatgpt.com/g/' + A + '/c/' + ID), 'targeted');
  assert.equal(batch.observations.length, 1); assert.equal(batch.entities.length, 1); assert.equal(batch.entities[0].name, 'Actuel');
  assert.deepEqual(Adapter.scanBatch(doc, win(), 'targeted'), { observations: [], entities: [] });
});
test('Fusion par clé, renommage et protection des preuves plus fiables ; noms inconnus honnêtes', () => {
  let state = Core.merge(Core.empty('chatgpt'), [], T1, options([project(A), project(B), project(C, null, 'key-only')]));
  assert.equal(Object.keys(state.entities).length, 3); assert.equal(state.entities[C].name, null);
  state = Core.merge(state, [], T2, options([project(A, 'Recherche personnelle')]));
  assert.equal(Object.keys(state.entities).length, 3); assert.equal(state.entities[A].name, 'Recherche personnelle'); assert.equal(state.entities[B].name, 'Développement');
  state = Core.merge(state, [], T2, options([project(A, 'Preuve plus faible', 'expanded-group'), project(B, null, 'key-only')]));
  assert.equal(state.entities[A].name, 'Recherche personnelle'); assert.equal(state.entities[B].name, 'Développement');
  const conflict = Core.merge(Core.empty('chatgpt'), [], T1, options([project(A, 'Un'), project(A, 'Deux')]));
  assert.equal(conflict.entities[A].name, null);
});
test('Validation stricte et refus atomique conversations + projets, sans écriture partielle', async () => {
  let data = {}; const storage = { get: async key => ({ [key]: data[key] }), set: async change => { data = structuredClone({ ...data, ...change }); } };
  const repository = createRepository(storage, { source: 'chatgpt', normalize: Adapter.normalize, normalizeEntity: Adapter.normalizeEntity, now: () => T1 });
  assert.equal(KEY, 'monGptCollectorStateV2'); assert.deepEqual((await repository.get()).state.entities, {});
  await repository.ingest({ observations: [], entities: [project()] }, 'initial', 'manual');
  const before = JSON.stringify(data);
  for (const bad of [project('clé incorrecte'), project(A, 42), project(A, 'x'.repeat(257)), project(A, 'Nom\u0001invalide'), { ...project(), evidence: { kind: 'deviné', url: null } }, { ...project(), evidence: { kind: 'direct-link', url: 'https://chatgpt.com/g/' + B + '/project' } }]) {
    await assert.rejects(repository.ingest({ observations: [{ source: 'chatgpt', identity: ID, url: 'https://chatgpt.com/c/' + ID }], entities: [bad] }, 'bad', 'manual'));
    assert.equal(JSON.stringify(data), before);
  }
  const limited = { ...Core.LIMITS, entities: 1 };
  assert.throws(() => Core.merge(data[KEY], [], T2, { ...options([project(B)]), limits: limited }), /Limite/);
  assert.equal(JSON.stringify(data), before);
});
test('Export v2 déterministe : deux homonymes distincts, inconnu null et deux contextes pour un seul UUID', () => {
  const observations = [A, B].map(key => ({ source: 'chatgpt', identity: ID, url: `https://chatgpt.com/g/${key}/c/${ID}`, title: 'Un fil fictif' }));
  const state = Core.merge(Core.empty('chatgpt'), observations, T1, options([project(B), project(A), project(C, null, 'key-only')]));
  const data = Adapter.exportJson(state, T2);
  assert.equal(data.schemaVersion, 2); assert.equal(data.projects.length, 3); assert.equal(data.conversations.length, 1);
  assert.deepEqual(data.conversations[0].observedProjectKeys, [A, B]);
  assert.deepEqual(data.projects.map(p => p.observedName), ['Développement', 'Développement', null]);
  assert.equal(JSON.stringify(Adapter.exportJson(state, T2)), JSON.stringify(data));
  assert.ok(!JSON.stringify(data).includes('titleQuality'));
});
test('API de conteneurs réutilisable hors ChatGPT, clés distinctes malgré le nom identique', () => {
  const entities = ['planche-a', 'planche-b'].map(identity => ({ source: 'atelier-fictif', identity, name: 'Même nom', confidence: 2, evidence: { kind: 'direct-control', url: null } }));
  const state = Core.merge(Core.empty('atelier-fictif'), [], T1, { entities });
  assert.equal(Object.keys(state.entities).length, 2); assert.equal(Core.exportData(state, T2).entities.length, 2);
});
test('Clés et preuves strictes : hôte exact, routes de projet, contexte non inventé et dates valides', () => {
  assert.equal(Adapter.parseProjectUrl('https://CHATGPT.COM/g/' + A + '/project/?x=1#fin').identity, A);
  for (const url of ['https://chatgpt.com:443/g/' + A, 'https://user@chatgpt.com/g/' + A, 'https://chatgpt.com/g/g-custom/project', 'https://chatgpt.com/g/' + A + '/c/' + ID, 'https://chatgpt.com/a/../g/' + A]) assert.throws(() => Adapter.parseProjectUrl(url));
  assert.throws(() => Adapter.normalizeEntity({ ...project(), evidence: { kind: 'expanded-group', url: project().evidence.url } }));
  const state = Core.merge(Core.empty('chatgpt'), [{ source: 'chatgpt', identity: ID, url: 'https://chatgpt.com/g/' + A + '/c/' + ID }], T1, options([project()]));
  const broken = structuredClone(state); broken.records[ID].contexts = [B]; assert.throws(() => Adapter.exportJson(broken, T2));
  broken.records[ID].contexts = [A]; broken.entities[A].nameObservedAt = '2026-02-31T00:00:00.000Z'; assert.throws(() => Adapter.exportJson(broken, T2));
  const section = documentFrom(`<nav><button id="s" aria-expanded="true" aria-controls="g">Projets</button><div role="group" id="g" aria-labelledby="s"><a href="/g/${A}/c/${ID}">Fil</a></div></nav>`);
  assert.equal(Adapter.scanProjects(section, win())[0].name, null);
});
