'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { createRuntime } = require('../browser/runtime.js');
function harness() {
  const timers = new Map(), intervals = new Map(), observers = [], calls = []; let id = 0, failed = false;
  const target = {};
  const win = { location: { href: 'https://example.test/a' }, setTimeout: fn => { timers.set(++id, fn); return id; }, clearTimeout: n => timers.delete(n),
    setInterval: fn => { intervals.set(++id, fn); return id; }, clearInterval: n => intervals.delete(n),
    MutationObserver: class { constructor(callback) { this.callback = callback; this.active = false; observers.push(this); } observe() { this.active = true; } disconnect() { this.active = false; } } };
  let observations = [{ source: 'fictif', identity: 'A', url: 'https://example.test/a', title: 'A' }, { source: 'fictif', identity: 'B', url: 'https://example.test/b', title: 'B' }];
  const adapter = { roots: () => [target], relevantMutation: m => m.useful,
    scan: (_, window, mode) => mode === 'targeted' ? observations.filter(o => o.url === window.location.href) : observations };
  const runtime = createRuntime({ win, doc: {}, adapter, uuid: () => 'scan-' + (++id), send: async message => {
    calls.push(message); if (failed) throw Error('Quota fictif');
    return { summary: { detectedCount: new Set(message.observations.map(o => o.identity)).size } };
  } });
  async function flush() {
    const pending = [...timers]; timers.clear(); for (const [, fn] of pending) fn();
    await new Promise(resolve => setImmediate(resolve));
  }
  return { runtime, win, timers, intervals, observers, calls, flush, fail: v => { failed = v; }, observations: v => { observations = v; } };
}
test('Manuel : aucun timer, observer ou scan initial ; double événement partagé', async () => {
  const h = harness(); h.runtime.applyMode('manual');
  assert.equal(h.timers.size, 0); assert.equal(h.intervals.size, 0); assert.equal(h.observers.length, 0); assert.equal(h.calls.length, 0);
  const first = h.runtime.manual(), second = h.runtime.manual(); assert.equal(first, second);
  const result = await first; assert.equal(result.detectedCount, 2); assert.equal(h.calls.length, 1);
  await h.runtime.manual(); assert.equal(h.calls.length, 2);
});
test('Transitions cible/large/manuel et route SPA sans remplacer history', async () => {
  const h = harness(); h.runtime.applyMode('targeted'); await h.flush(); assert.equal(h.calls[0].observations.length, 1);
  h.win.location.href = 'https://example.test/b'; for (const fn of h.intervals.values()) fn(); await h.flush();
  assert.equal(h.calls[1].observations[0].identity, 'B');
  h.runtime.applyMode('broad'); await h.flush(); assert.equal(h.calls[2].observations.length, 2);
  h.runtime.applyMode('manual'); await h.flush(); assert.equal(h.calls.length, 3);
  assert.equal(h.timers.size, 0); assert.equal(h.intervals.size, 0); assert.ok(h.observers.every(o => !o.active));
});
test('Mutations utiles debouncées, frappe hors liens ignorée, scan inchangé sans écriture', async () => {
  const h = harness(); h.runtime.applyMode('broad'); await h.flush(); const count = h.calls.length;
  const observer = h.observers.at(-1); observer.callback([{ useful: false }]); assert.equal(h.timers.size, 0);
  for (let n = 0; n < 20; n++) observer.callback([{ useful: true }]); assert.equal(h.timers.size, 1);
  await h.flush(); assert.equal(h.calls.length, count);
  h.observations([{ source: 'fictif', identity: 'A', url: 'https://example.test/a', title: 'A renommé' }]);
  observer.callback([{ useful: true }]); await h.flush(); assert.equal(h.calls.length, count + 1);
});
test('Échec visible, pending conservé, relance manuelle et suspension complète', async () => {
  const h = harness(); h.fail(true); h.runtime.applyMode('broad'); await h.flush();
  assert.match(h.runtime.status().error, /Quota/); assert.equal(h.runtime.status().pendingCount, 2);
  h.runtime.applyMode('manual'); assert.equal(h.runtime.status().pendingCount, 2);
  h.fail(false); await h.runtime.manual(); assert.equal(h.runtime.status().pendingCount, 0); assert.equal(h.runtime.status().error, '');
  h.runtime.dispose(); await assert.rejects(h.runtime.manual(), /suspendue/);
});
