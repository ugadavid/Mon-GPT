/* Pont réutilisable : un seul écrivain, stockage injecté, aucune API DOM. */
(function (root, factory) {
  const core = typeof module === 'object' && module.exports ? require('../core/observations.js') : root.CollectorCore;
  const api = factory(core);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CollectorRepository = api;
})(globalThis, function (Core) {
  'use strict';
  const KEY = 'monGptCollectorStateV2';
  function createRepository(storage, { source, normalize, normalizeEntity = Core.entityObservation, limits = Core.LIMITS, key = KEY, now = () => new Date().toISOString() }) {
    let queue = Promise.resolve(); let lastError = ''; const requests = new Map();
    async function read() {
      const data = await storage.get(key);
      return data[key] === undefined ? Core.empty(source) : Core.validate(data[key], source, normalize, limits, normalizeEntity);
    }
    function transact(fn) {
      const next = queue.then(fn);
      queue = next.catch(() => {});
      return next.catch(error => { lastError = error.message || 'Stockage inaccessible.'; throw error; });
    }
    async function write(state) {
      if (new TextEncoder().encode(JSON.stringify(state)).length > limits.bytes) throw Error('Limite locale atteinte ; données conservées.');
      await storage.set({ [key]: state }); lastError = '';
    }
    return {
      get: () => transact(async () => ({ state: await read(), error: lastError })),
      ingest: (batch, requestId, kind) => transact(async () => {
        if (typeof requestId !== 'string' || requestId.length > 128 || !requestId) throw Error('Requête de scan invalide.');
        if (requests.has(requestId)) return requests.get(requestId);
        if (!batch || !Array.isArray(batch.observations) || !Array.isArray(batch.entities)) throw Error('Lot d’observations invalide.');
        const state = Core.merge(await read(), batch.observations, now(), { normalize, normalizeEntity, entities: batch.entities, limits, kind });
        await write(state);
        requests.set(requestId, state.lastScan);
        if (requests.size > 128) requests.delete(requests.keys().next().value);
        return state.lastScan;
      }),
      setMode: value => transact(async () => {
        if (!Core.MODES.includes(value)) throw Error('Mode inconnu.');
        const state = await read(); state.mode = value; await write(state); return state;
      }),
      clear: () => transact(async () => {
        const state = await read(); const clean = Core.empty(source); clean.mode = state.mode;
        await write(clean); requests.clear(); return clean;
      })
    };
  }
  return { KEY, createRepository };
});
