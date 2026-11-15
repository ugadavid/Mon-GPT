/* Cycle de collecte adapté du content-script MJ Collector 0.3.0.
 * Scan/observer, délai 300 ms, pending conservé sur échec et modes contrôlables.
 * Le site, le transport et les horloges sont injectés ; aucune regex ChatGPT ici. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CollectorRuntime = api;
})(globalThis, function () {
  'use strict';
  function createRuntime({ win, doc, adapter, send, uuid = () => crypto.randomUUID() }) {
    let mode = 'manual', timer = null, interval = null, observer = null, targets = [], lastHref = '', lastError = '', disposed = false;
    let fingerprints = new Map(), pending = new Map(), entityFingerprints = new Map(), pendingEntities = new Map(), queue = Promise.resolve(), manualPromise = null, scheduledAt = 0;
    const key = o => o.identity + '|' + o.url;
    const fingerprint = o => JSON.stringify([o.title, o.titleQuality, o.context, o.active]);
    const entityFingerprint = e => JSON.stringify([e.name, e.confidence, e.evidence]);
    function cancelTimer() { if (timer !== null) win.clearTimeout(timer); timer = null; scheduledAt = 0; }
    function schedule(delay = 300) {
      if (disposed || mode === 'manual') return;
      if (!scheduledAt) scheduledAt = Date.now();
      if (timer !== null) win.clearTimeout(timer);
      timer = win.setTimeout(() => { timer = null; scheduledAt = 0; run('auto').catch(() => {}); }, Math.min(delay, Math.max(0, 1500 - (Date.now() - scheduledAt))));
    }
    function bindTargets() {
      const next = adapter.roots(doc, win);
      if (next.length === targets.length && next.every((v, i) => v === targets[i])) return;
      observer?.disconnect(); targets = next;
      if (mode === 'manual' || !next.length) return;
      observer = new win.MutationObserver(mutations => { if (mutations.some(adapter.relevantMutation)) schedule(); });
      for (const target of next) observer.observe(target, { childList: true, subtree: true, characterData: true, attributes: true,
        attributeFilter: ['href', 'aria-label', 'data-active', 'aria-current', 'hidden', 'aria-hidden', 'style', 'aria-expanded', 'aria-controls', 'aria-labelledby', 'data-project-id', 'data-project-key', 'id', 'role'] });
      schedule();
    }
    function run(kind) {
      if (disposed) return Promise.reject(Error('Extension suspendue ; actualisez la page.'));
      const requestMode = mode;
      const task = async () => {
        if (kind === 'auto' && (requestMode !== mode || mode === 'manual')) return null;
        try {
          const { observations: seen, entities } = adapter.scanBatch(doc, win, kind === 'manual' ? 'broad' : mode);
          if (seen.length > 5000) throw Error('Plus de 5 000 liens rendus : scan interrompu sans écriture.');
          if (entities.length > 1000) throw Error('Plus de 1 000 projets rendus : scan interrompu sans écriture.');
          const changed = kind === 'manual' ? seen : seen.filter(o => fingerprints.get(key(o)) !== fingerprint(o));
          // Un lot de fils conserve aussi les projets du même relevé, y compris
          // après un vidage effectué sans changer de mode.
          const changedEntities = kind === 'manual' || changed.length ? entities : entities.filter(e => entityFingerprints.get(e.identity) !== entityFingerprint(e));
          if (kind === 'auto' && !changed.length && !changedEntities.length && !pending.size && !pendingEntities.size) return null;
          for (const o of changed) {
            if (!pending.has(key(o)) && pending.size >= 5000) throw Error('Limite de 5 000 liens en attente atteinte ; collecte suspendue. Exportez les observations conservées.');
            pending.set(key(o), o);
          }
          for (const e of changedEntities) {
            if (!pendingEntities.has(e.identity) && pendingEntities.size >= 1000) throw Error('Limite de projets en attente atteinte ; aucune suppression.');
            pendingEntities.set(e.identity, e);
          }
          const batch = kind === 'manual' ? seen : [...pending.values()];
          const entityBatch = kind === 'manual' ? entities : [...pendingEntities.values()];
          const result = await send({ type: 'ingest', requestId: uuid(), kind, observations: batch, entities: entityBatch });
          for (const o of batch) pending.delete(key(o));
          for (const e of entityBatch) pendingEntities.delete(e.identity);
          fingerprints = new Map(seen.map(o => [key(o), fingerprint(o)]));
          entityFingerprints = new Map(entities.map(e => [e.identity, entityFingerprint(e)]));
          if (!pending.size && !pendingEntities.size) lastError = '';
          return result.summary;
        } catch (error) {
          lastError = error.message || 'Collecte non enregistrée.';
          // Pas de perte des observations refusées par le stockage.
          if (mode !== 'manual') schedule(1500);
          throw error;
        }
      };
      const result = queue.then(task); queue = result.catch(() => {}); return result;
    }
    function applyMode(value) {
      cancelTimer(); observer?.disconnect(); observer = null; targets = [];
      if (interval !== null) win.clearInterval(interval); interval = null;
      mode = ['manual', 'targeted', 'broad'].includes(value) ? value : 'targeted';
      fingerprints.clear();
      entityFingerprints.clear();
      if (mode === 'manual') return;
      lastHref = win.location.href; bindTargets(); schedule();
      // Observe les routes sans remplacer history.pushState ou toucher au site.
      interval = win.setInterval(() => {
        if (lastHref !== win.location.href) { lastHref = win.location.href; schedule(); }
        bindTargets();
      }, 1200);
    }
    function manual() {
      if (!manualPromise) {
        cancelTimer();
        manualPromise = run('manual').finally(() => { manualPromise = null; });
      }
      return manualPromise;
    }
    function dispose() { disposed = true; cancelTimer(); observer?.disconnect(); if (interval !== null) win.clearInterval(interval); }
    return { applyMode, manual, dispose, status: () => ({ mode, error: lastError, pendingCount: pending.size, pendingEntityCount: pendingEntities.size }) };
  }
  return { createRuntime };
});
