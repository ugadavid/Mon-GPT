/* Socle pur. Fusion adaptée de MJ Collector : index, dates, compteurs, URLs bornées.
 * Provenance et différences : README.md / reports/MG-008/rapport.md. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CollectorCore = api;
})(globalThis, function () {
  'use strict';
  const MODES = ['manual', 'targeted', 'broad'];
  const LIMITS = Object.freeze({ records: 5000, entities: 1000, name: 256, bytes: 6 * 1024 * 1024, urls: 10, title: 512, url: 2048, batch: 5000 });
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
  function validateIdentity(raw) {
    if (!raw || typeof raw !== 'object' || typeof raw.source !== 'string' || typeof raw.identity !== 'string' || !/^[a-z][a-z0-9-]{0,31}$/.test(raw.source) || !/^[A-Za-z0-9_-]{1,128}$/.test(raw.identity) || ['__proto__', 'constructor', 'prototype'].includes(raw.identity)) throw Error('Identité d’observation invalide.');
  }
  function observation(raw) {
    validateIdentity(raw);
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
  // Conteneurs nommés génériques : leur identité ne dépend jamais de leur nom.
  function entityObservation(raw) {
    if (!raw || typeof raw !== 'object') throw Error('Conteneur observé invalide.');
    validateIdentity(raw);
    if (raw.name !== null && (typeof raw.name !== 'string' || !raw.name.trim() || raw.name.length > LIMITS.name || /[\u0000-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]/.test(raw.name))) throw Error('Nom observé invalide.');
    const name = raw.name === null ? null : raw.name.replace(/\s+/g, ' ').trim();
    if (!raw.evidence || typeof raw.evidence.kind !== 'string' || !/^[a-z][a-z-]{0,31}$/.test(raw.evidence.kind) || !Number.isInteger(raw.confidence) || raw.confidence < 0 || raw.confidence > 2 || (name === null) !== (raw.confidence === 0)) throw Error('Preuve d’observation invalide.');
    const url = raw.evidence.url;
    if (url !== null) observation({ source: raw.source, identity: raw.identity, url });
    return { source: raw.source, identity: raw.identity, name, confidence: raw.confidence, evidence: { kind: raw.evidence.kind, url } };
  }
  function validateEntities(index, source, normalize, limits) {
    if (!index || typeof index !== 'object' || Array.isArray(index) || Object.keys(index).length > limits.entities) throw Error('Index de conteneurs invalide.');
    const clean = {};
    for (const [id, raw] of Object.entries(index)) {
      const entity = normalize(raw);
      if (id !== entity.identity || entity.source !== source || !Number.isSafeInteger(raw.seenCount) || raw.seenCount < 1) throw Error('Conteneur stocké invalide.');
      date(raw.firstSeenAt); date(raw.lastSeenAt);
      if (raw.firstSeenAt > raw.lastSeenAt || (entity.name === null ? raw.nameObservedAt !== null : date(raw.nameObservedAt) < raw.firstSeenAt || raw.nameObservedAt > raw.lastSeenAt)) throw Error('Dates de conteneur invalides.');
      clean[id] = { ...entity, firstSeenAt: raw.firstSeenAt, lastSeenAt: raw.lastSeenAt, seenCount: raw.seenCount, nameObservedAt: raw.nameObservedAt };
    }
    return clean;
  }
  function mergeEntities(index, input, source, now, normalize, limits) {
    if (!Array.isArray(input) || input.length > limits.entities) throw Error('Trop de conteneurs dans ce scan.');
    const grouped = new Map(); let count = Object.keys(index).length, newCount = 0;
    for (const raw of input) {
      const entity = normalize(raw);
      if (entity.source !== source) throw Error('Source de conteneur inattendue.');
      const group = grouped.get(entity.identity) || []; group.push(entity); grouped.set(entity.identity, group);
    }
    for (const [id, group] of grouped) {
      let record = index[id];
      if (!record) {
        if (count >= limits.entities) throw Error('Limite de conteneurs atteinte ; aucune donnée supprimée.');
        count++; newCount++;
        record = { ...group[0], name: null, confidence: 0, evidence: { kind: 'key-only', url: null }, nameObservedAt: null, firstSeenAt: now, lastSeenAt: now, seenCount: 0 };
      }
      record = { ...record, evidence: { ...record.evidence } };
      record.firstSeenAt = record.firstSeenAt < now ? record.firstSeenAt : now;
      record.lastSeenAt = record.lastSeenAt > now ? record.lastSeenAt : now;
      if (record.seenCount === Number.MAX_SAFE_INTEGER) throw Error('Compteur de conteneur maximal atteint.');
      record.seenCount++;
      const ranked = group.filter(e => e.name !== null).sort((a, b) => b.confidence - a.confidence);
      const best = ranked[0];
      // Une collision ne se résout jamais par l’ordre du DOM ou par le libellé.
      if (best && new Set(ranked.filter(e => e.confidence === best.confidence).map(e => e.name)).size === 1 && best.confidence >= record.confidence && (!record.nameObservedAt || now >= record.nameObservedAt)) {
        Object.assign(record, best); record.nameObservedAt = now;
      } else if (record.name === null) {
        const unknown = group.find(e => e.name === null);
        if (unknown) record.evidence = { ...unknown.evidence };
      }
      index[id] = record;
    }
    return { count: grouped.size, newCount };
  }
  function empty(source) { return { schemaVersion: 2, source, mode: 'targeted', records: {}, entities: {}, lastScan: null }; }
  function validate(state, source, normalize = observation, limits = LIMITS, normalizeEntity = entityObservation) {
    if (!state || state.schemaVersion !== 2 || state.source !== source || !MODES.includes(state.mode) || !state.records || Array.isArray(state.records) || typeof state.records !== 'object') throw Error('Stockage incompatible ; données conservées.');
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
      if (!scan || !['manual', 'auto'].includes(scan.kind) || ![scan.detectedCount, scan.newCount, scan.existingCount, scan.entityCount, scan.newEntityCount].every(v => Number.isSafeInteger(v) && v >= 0) || scan.detectedCount !== scan.newCount + scan.existingCount || scan.newEntityCount > scan.entityCount) throw Error('Résumé de scan invalide.');
      lastScan = { at: date(scan.at), kind: scan.kind, detectedCount: scan.detectedCount, newCount: scan.newCount, existingCount: scan.existingCount, entityCount: scan.entityCount, newEntityCount: scan.newEntityCount };
    }
    return { schemaVersion: 2, source, mode: state.mode, records, entities: validateEntities(state.entities, source, normalizeEntity, limits), lastScan };
  }
  function merge(state, input, now, { normalize = observation, normalizeEntity = entityObservation, entities = [], limits = LIMITS, kind = 'manual' } = {}) {
    date(now);
    if (!['manual', 'auto'].includes(kind)) throw Error('Type de scan invalide.');
    const current = validate(state, state.source, normalize, limits, normalizeEntity);
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
    const mergedEntities = mergeEntities(current.entities, entities, current.source, now, normalizeEntity, limits);
    current.lastScan = { at: now, kind, detectedCount: grouped.size, newCount, existingCount: grouped.size - newCount, entityCount: mergedEntities.count, newEntityCount: mergedEntities.newCount };
    if (new TextEncoder().encode(JSON.stringify(current)).length > limits.bytes) throw Error('Limite locale atteinte (6 Mo). Exportez vos observations ; aucune donnée supprimée.');
    return current;
  }
  function recent(state) { return Object.values(state.records).sort((a, b) => b.lastSeenAt.localeCompare(a.lastSeenAt) || a.identity.localeCompare(b.identity)); }
  function exportData(state, now, { source, collectionKey = 'observations', map = r => r, entityKey = 'entities', mapEntity = r => r, normalize = observation, normalizeEntity = entityObservation } = {}) {
    const clean = validate(state, state.source, normalize, LIMITS, normalizeEntity);
    return { source: source || clean.source, schemaVersion: 2, exportedAt: date(now),
      [entityKey]: Object.values(clean.entities).sort((a, b) => a.identity.localeCompare(b.identity)).map(mapEntity),
      [collectionKey]: Object.values(clean.records).sort((a, b) => a.identity.localeCompare(b.identity)).map(map) };
  }
  function urlsText(state) { return Object.values(state.records).sort((a, b) => a.identity.localeCompare(b.identity)).map(r => r.url).join('\n'); }
  return { MODES, LIMITS, date, text, mode, observation, entityObservation, unique, empty, validate, merge, recent, exportData, urlsText };
});
