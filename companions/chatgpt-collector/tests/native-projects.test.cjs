'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const Adapter = require('../adapters/chatgpt.js');
const Core = require('../core/observations.js');
const { documentFrom } = require('./helpers/dom.cjs');
const A = 'g-p-11111111111111111111111111111111', B = 'g-p-22222222222222222222222222222222', C = 'g-p-33333333333333333333333333333333';
const html = fs.readFileSync(path.join(__dirname, 'fixtures/native-projects.html'), 'utf8').split('<script>')[0];
const win = href => ({ location: { href: href || 'https://chatgpt.com/' } });
const named = (doc, href, mode = 'broad') => Adapter.scanProjects(doc, win(href), mode);
test('Vrai contrat natif réduit : div role button, mêmes contrôles clé/label, un ouvert et un replié', () => {
  const doc = documentFrom(html), projects = named(doc);
  assert.equal(projects.find(p => p.identity === A).name, 'Développement'); assert.equal(projects.find(p => p.identity === B).name, 'Développement');
  assert.equal(projects.find(p => p.identity === C).name, null);
  assert.equal(projects.filter(p => p.evidence.kind === 'direct-control').length, 2);
  assert.equal(Adapter.scan(doc, win()).length, 2, 'le fil caché de B reste non observé');
});
test('Dépli/repli natif : nom stable, enfants observés seulement quand rendus, aucune clé déduite des noms', () => {
  const doc = documentFrom(html), b = doc.getElementById('nativeB'), children = doc.getElementById('childrenB');
  b.attrs['aria-expanded'] = 'true'; b.attrs['data-app-action-sidebar-project-collapsed'] = 'false'; delete children.attrs.inert; children.attrs['aria-hidden'] = 'false';
  const batch = Adapter.scanBatch(doc, win(), 'broad'); assert.equal(batch.observations.length, 3); assert.equal(batch.entities.find(p => p.identity === B).name, 'Développement');
  children.attrs.inert = ''; children.attrs['aria-hidden'] = 'true'; b.attrs['aria-expanded'] = 'false';
  assert.equal(Adapter.scan(doc, win()).length, 2); assert.equal(named(doc).find(p => p.identity === B).name, 'Développement');
});
test('Aucune contamination : propriétaire contradictoire, nom voisin et bloc mixte restent sans nom', () => {
  const wrongOwner = documentFrom(html); wrongOwner.getElementById('nativeA').closest('[data-sidebar-project-kind]').attrs['data-sidebar-project-container-id'] = 'project:' + B;
  assert.equal(named(wrongOwner).find(p => p.identity === A).name, null); assert.equal(named(wrongOwner).find(p => p.identity === B).name, 'Développement');
  const mixed = documentFrom(html); mixed.getElementById('childrenA').querySelector('a').attrs.href = 'https://chatgpt.com/g/' + B + '/c/00000000-0000-4000-8000-000000000951';
  assert.equal(named(mixed).find(p => p.identity === A).name, null);
  const neighbor = documentFrom(html); neighbor.getElementById('nativeA').attrs['aria-labelledby'] = 'nameB';
  assert.equal(named(neighbor).find(p => p.identity === A).name, null);
});
test('Nom manquant, désaccord texte/attribut, ID ambigu et contrôle caché : aucun nom inventé', () => {
  const cases = [
    doc => { delete doc.getElementById('nativeA').attrs['data-app-action-sidebar-project-label']; },
    doc => { doc.getElementById('nativeA').attrs['data-app-action-sidebar-project-label'] = 'Un autre nom'; },
    doc => { doc.getElementById('nameB').attrs.id = 'nameA'; },
    doc => { doc.getElementById('nameA').attrs.hidden = ''; }
  ];
  for (const mutate of cases) { const doc = documentFrom(html); mutate(doc); assert.equal(named(doc).find(p => p.identity === A).name, null); }
  const hidden = documentFrom(html); hidden.getElementById('nativeB').attrs.hidden = ''; assert.ok(!named(hidden).some(p => p.identity === B));
});
test('Nom réel générique ou préfixe d’action : preuve concordante acceptée intégralement, sans tronquer', () => {
  for (const title of ['Projets', 'Options — Été & recherches', 'Couleur personnalisée', 'Ouvrir mes idées']) {
    const doc = documentFrom(html); doc.getElementById('nativeA').attrs['data-app-action-sidebar-project-label'] = title;
    doc.getElementById('nameA').querySelector('[data-marquee-content]').childNodes[0].nodeValue = title;
    assert.equal(named(doc).find(p => p.identity === A).name, title);
  }
});
test('Modes et accueil SPA : seul le projet courant en cible, tous les rendus en scan explicite', () => {
  const doc = documentFrom(html);
  assert.deepEqual(named(doc, 'https://chatgpt.com/', 'targeted'), []);
  const current = named(doc, 'https://chatgpt.com/g/' + B + '/project', 'targeted'); assert.equal(current.length, 1); assert.equal(current[0].identity, B); assert.equal(current[0].name, 'Développement');
  const conversation = Adapter.scanBatch(doc, win('https://chatgpt.com/g/' + A + '/c/00000000-0000-4000-8000-000000000951'), 'targeted');
  assert.equal(conversation.entities.length, 1); assert.equal(conversation.entities[0].identity, A);
});
test('Mutations natives : noms et marqueurs suivis, y compris attribut retiré ; texte de fil non utilisé comme nom', () => {
  const doc = documentFrom(html), target = doc.getElementById('nativeA');
  for (const attributeName of ['data-app-action-sidebar-project-label', 'data-app-action-sidebar-project-id', 'data-sidebar-project-container-id']) assert.equal(Adapter.relevantMutation({ type: 'attributes', target, attributeName }), true);
  assert.equal(Adapter.relevantMutation({ type: 'characterData', target: doc.getElementById('nameA').querySelector('[data-marquee-content]').childNodes[0] }), true);
  delete target.attrs['data-app-action-sidebar-project-row']; delete target.attrs['data-app-action-sidebar-project-id'];
  assert.equal(Adapter.relevantMutation({ type: 'attributes', target, attributeName: 'data-app-action-sidebar-project-id' }), true);
  assert.equal(named(doc).find(p => p.identity === A).name, null);
});
test('Export v2 inchangé : deux homonymes, clés distinctes, rattachements de conversations et dates conservés', () => {
  const doc = documentFrom(html), children = doc.getElementById('childrenB'); delete children.attrs.inert; children.attrs['aria-hidden'] = 'false';
  const batch = Adapter.scanBatch(doc, win(), 'broad'), time = '2026-11-15T20:00:00.000Z';
  const state = Core.merge(Core.empty('chatgpt'), batch.observations, time, { entities: batch.entities, normalize: Adapter.normalize, normalizeEntity: Adapter.normalizeEntity });
  const exported = Adapter.exportJson(state, time);
  assert.equal(exported.schemaVersion, 2); assert.equal(exported.projects.filter(p => p.observedName === 'Développement').length, 2);
  assert.equal(new Set(exported.projects.map(p => p.projectKey)).size, 3);
  for (const key of [A, B]) assert.ok(exported.conversations.some(c => c.observedProjectKeys.includes(key)));
  assert.equal(Object.keys(state.records).length, 3);
});
