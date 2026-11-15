/* Socle pur. Fusion adaptée de MJ Collector : index, dates, compteurs, URLs bornées.
 * Provenance et différences : README.md / reports/MG-008/rapport.md. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CollectorCore = api;
})(globalThis, function () {
  'use strict';
  const MODES = ['manual', 'targeted', 'broad'];
  const LIMITS = Object.freeze({ records: 5000, bytes: 6 * 1024 * 1024, urls: 10, title: 512, url: 2048, batch: 5000 });
  const own = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
  function date(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString() !== value) throw Error('Date d’observation invalide.');
    return value;
  }
  function text(value, maximum) {
    if (typeof value !== 'string') return null;
    const clean = value.replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim();
    return clean ? clean.slice(0, maximum) : null;
  }
  function mode(value) { return MODES.includes(value) ? value : 'targeted'; }
  function observation(raw) {
    if (!raw || typeof raw !== 'object' || typeof raw.source !== 'string' || typeof raw.identity !== 'string' || !/^[a-z][a-z0-9-]{0,31}$/.test(raw.source) || !/^[A-Za-z0-9_-]{1,128}$/.test(raw.identity) || ['__proto__', 'constructor', 'prototype'].includes(raw.identity)) throw Error('Identité d’observation invalide.');
    if (typeof raw.url !== 'string' || raw.url.length > LIMITS.url) throw Error('URL observée trop longue ou invalide.');
    const url = new URL(raw.url);
    if (url.protocol !== 'https:' || url.username || url.password) throw Error('URL observée non sûre.');
    const title = text(raw.title, LIMITS.title);
    return { source: raw.source, identity: raw.identity, url: raw.url, title,
      titleQuality: title ? (raw.titleQuality === 2 ? 2 : 1) : 0,
      context: text(raw.context, 128), active: raw.active === true };
  }
  function unique(list, value, maximum = LIMITS.urls) {
    if (value && !list.includes(value)) {
      if (list.length >= maximum) throw Error('Limite de variantes atteinte : exportez vos observations avant de poursuivre. Aucune donnée supprimée.');
      list.push(value);
    }
  }
  function empty(source) { return { schemaVersion: 1, source, mode: 'targeted', records: {}, lastScan: null }; }
  function validate(state, source, normalize = observation, limits = LIMITS) {
    if (!state || state.schemaVersion !== 1 || state.source !== source || !MODES.includes(state.mode) || !state.records || Array.isArray(state.records) || typeof state.records !== 'object') throw Error('Stockage incompatible ; données conservées.');
    const records = {};
    if (Object.keys(state.records).length > limits.records) throw Error('Trop d’observations ; données conservées.');
    for (const [id, r] of Object.entries(state.records)) {
      const clean = normalize(r);
      if (id !== clean.identity || clean.source !== source || !Number.isSafeInteger(r.seenCount) || r.seenCount < 1) throw Error('Observation stockée invalide ; données conservées.');
      date(r.firstSeenAt); date(r.lastSeenAt);
      if (r.firstSeenAt > r.lastSeenAt || !Array.isArray(r.observedUrls) || !r.observedUrls.length || r.observedUrls.length > limits.urls || new Set(r.observedUrls).size !== r.observedUrls.length || !r.observedUrls.includes(clean.url)) throw Error('Historique observé invalide.');
      for (const url of r.observedUrls) {
        const checked = normalize({ ...clean, url });
        if (checked.identity !== id) throw Error('URL sans rapport avec l’identité.');
      }
      if (!Array.isArray(r.contexts) || r.contexts.length > limits.urls || r.contexts.some(c => typeof c !== 'string' || !c || c.length > 128)) throw Error('Contexte observé invalide.');
      records[id] = { ...clean, firstSeenAt: r.firstSeenAt, lastSeenAt: r.lastSeenAt, seenCount: r.seenCount, observedUrls: [...r.observedUrls], contexts: [...new Set(r.contexts)] };
    }
    let lastScan = null;
    if (state.lastScan !== null) {
      const scan = state.lastScan;
      if (!scan || !['manual', 'auto'].includes(scan.kind) || ![scan.detectedCount, scan.newCount, scan.existingCount].every(v => Number.isSafeInteger(v) && v >= 0) || scan.detectedCount !== scan.newCount + scan.existingCount) throw Error('Résumé de scan invalide.');
      lastScan = { at: date(scan.at), kind: scan.kind, detectedCount: scan.detectedCount, newCount: scan.newCount, existingCount: scan.existingCount };
    }
    return { schemaVersion: 1, source, mode: state.mode, records, lastScan };
  }
  function merge(state, input, now, { normalize = observation, limits = LIMITS, kind = 'manual' } = {}) {
    date(now);
    const current = validate(state, state.source, normalize, limits);
    if (!Array.isArray(input) || input.length > limits.batch) throw Error('Trop de liens dans ce scan ; aucune observation enregistrée.');
    // Une occurrence par identité et par scan, même si plusieurs liens la désignent.
    const grouped = new Map();
    for (const raw of input) {
      const o = normalize(raw);
      if (o.source !== current.source) throw Error('Source inattendue.');
      const group = grouped.get(o.identity) || [];
      group.push(o); grouped.set(o.identity, group);
    }
    let newCount = 0, recordCount = Object.keys(current.records).length;
    for (const [identity, observations] of grouped) {
      const first = observations[0];
      let record = current.records[identity];
      if (!record) {
        if (recordCount >= limits.records) throw Error('Limite de 5 000 observations atteinte. Exportez avant de continuer ; aucune suppression automatique.');
        newCount++; recordCount++;
        record = { ...first, firstSeenAt: now, lastSeenAt: now, seenCount: 0, observedUrls: [], contexts: [] };
      }
      record = { ...record, observedUrls: [...record.observedUrls], contexts: [...record.contexts] };
      record.firstSeenAt = record.firstSeenAt < now ? record.firstSeenAt : now;
      record.lastSeenAt = record.lastSeenAt > now ? record.lastSeenAt : now;
      if (record.seenCount === Number.MAX_SAFE_INTEGER) throw Error('Compteur maximal atteint ; données conservées.');
      record.seenCount++;
      const best = observations.filter(o => o.title).sort((a, b) => b.titleQuality - a.titleQuality || Number(b.active) - Number(a.active))[0];
      if (best && best.titleQuality >= record.titleQuality) { record.title = best.title; record.titleQuality = best.titleQuality; }
      for (const o of observations) {
        unique(record.observedUrls, o.url, limits.urls);
        unique(record.contexts, o.context, limits.urls);
        record.context = o.context;
      }
      record.active = observations.some(o => o.active);
      current.records[identity] = record;
    }
    current.lastScan = { at: now, kind, detectedCount: grouped.size, newCount, existingCount: grouped.size - newCount };
    if (new TextEncoder().encode(JSON.stringify(current)).length > limits.bytes) throw Error('Limite locale atteinte (6 Mo). Exportez vos observations ; aucune donnée supprimée.');
    return current;
  }
  function recent(state) { return Object.values(state.records).sort((a, b) => b.lastSeenAt.localeCompare(a.lastSeenAt) || a.identity.localeCompare(b.identity)); }
  function exportData(state, now, { source, collectionKey = 'observations', map = r => r, normalize = observation } = {}) {
    const clean = validate(state, state.source, normalize);
    return { source: source || clean.source, schemaVersion: 1, exportedAt: date(now),
      [collectionKey]: Object.values(clean.records).sort((a, b) => a.identity.localeCompare(b.identity)).map(map) };
  }
  function urlsText(state) { return Object.values(state.records).sort((a, b) => a.identity.localeCompare(b.identity)).map(r => r.url).join('\n'); }
  return { MODES, LIMITS, date, text, mode, observation, unique, empty, validate, merge, recent, exportData, urlsText };
});
