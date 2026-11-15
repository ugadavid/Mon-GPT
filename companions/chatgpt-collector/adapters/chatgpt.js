/* Extraction adaptée de 3GPT3 getVisibleConversations / parseConversationHref.
 * Pas d’overlay, de rectangle, de stockage, de message ou de requête réseau. */
(function (root, factory) {
  const core = typeof module === 'object' && module.exports ? require('../core/observations.js') : root.CollectorCore;
  const api = factory(core);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.ChatGPTAdapter = api;
})(globalThis, function (Core) {
  'use strict';
  const UUID = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}';
  const PATH = new RegExp('^/(?:g/([A-Za-z0-9_-]+)/)?c/(' + UUID + ')/?$');
  const PROJECT_KEY = /^g-p-[A-Za-z0-9_-]{1,124}$/;
  const PROJECT_HOME = /^\/g\/(g-p-[A-Za-z0-9_-]{1,124})(?:\/project)?\/?$/;
  const EVIDENCE = Object.freeze({ 'key-only': 0, 'expanded-group': 1, 'direct-link': 2, 'direct-control': 2, 'project-page': 2 });
  const ROOTS = 'nav[aria-label="Historique de chat"], nav[aria-label="Chat history"], [data-testid="history"], aside, nav, [role="navigation"]';
  function parseUrl(value) {
    if (typeof value !== 'string' || value.length > Core.LIMITS.url) throw Error('Lien ChatGPT invalide.');
    const raw = value.trim();
    // Autorité brute contrôlée avant URL() : refuse aussi :443, identifiants et chemins normalisés ../.
    const parts = raw.match(/^https:\/\/chatgpt\.com(\/[^?#]*)(?:\?([^#]*))?(?:#.*)?$/i);
    const match = parts?.[1].match(PATH);
    if (!match || /[\u0000-\u0020\u007f]/.test(raw)) throw Error('Lien ChatGPT invalide.');
    return { identity: match[2].toLowerCase(), url: 'https://chatgpt.com' + parts[1].replace(/\/$/, '') + (parts[2] ? '?' + parts[2] : ''), context: match[1] && match[1].length <= 128 ? match[1] : null };
  }
  function allowedPage(value) {
    try { const u = new URL(value); return u.protocol === 'https:' && u.host === 'chatgpt.com' && !u.username && !u.password; } catch { return false; }
  }
  function normalize(raw) {
    const parsed = parseUrl(raw?.url);
    if (raw?.source !== 'chatgpt' || raw?.identity !== parsed.identity) throw Error('Identité ChatGPT incohérente.');
    if (raw.contexts !== undefined) {
      if (!Array.isArray(raw.contexts) || !Array.isArray(raw.observedUrls)) throw Error('Contextes ChatGPT invalides.');
      const expected = new Set(raw.observedUrls.map(url => parseUrl(url).context).filter(key => PROJECT_KEY.test(key || '')));
      if (raw.contexts.length !== expected.size || raw.contexts.some(key => typeof key !== 'string' || !PROJECT_KEY.test(key) || !expected.has(key))) throw Error('Contexte projet non observé dans les URL.');
    }
    return Core.observation({ ...raw, ...parsed, context: PROJECT_KEY.test(parsed.context || '') ? parsed.context : null, source: 'chatgpt' });
  }
  function absolute(href) { return typeof href === 'string' && href.startsWith('/') && !href.startsWith('//') ? 'https://chatgpt.com' + href : href; }
  function parseProjectUrl(value) {
    if (typeof value !== 'string' || value.length > Core.LIMITS.url || /[\u0000-\u0020\u007f]/.test(value.trim())) throw Error('Lien de projet invalide.');
    const parts = value.trim().match(/^https:\/\/chatgpt\.com(\/[^?#]*)(?:\?([^#]*))?(?:#.*)?$/i);
    const match = parts?.[1].match(PROJECT_HOME);
    if (!match) throw Error('Lien d’accueil projet invalide.');
    return { identity: match[1], url: 'https://chatgpt.com' + parts[1].replace(/\/$/, '') + (parts[2] ? '?' + parts[2] : '') };
  }
  function normalizeEntity(raw) {
    if (raw?.source !== 'chatgpt' || !PROJECT_KEY.test(raw?.identity || '') || !Object.hasOwn(EVIDENCE, raw?.evidence?.kind)) throw Error('Projet ou source de preuve invalide.');
    const rank = EVIDENCE[raw.evidence.kind];
    if ((raw.name === null) !== (rank === 0)) throw Error('Nom sans preuve fiable.');
    const url = raw.evidence.url;
    if (url !== null) {
      let id;
      try { id = parseProjectUrl(url).identity; } catch { id = parseUrl(url).context; }
      if (id !== raw.identity) throw Error('Preuve sans rapport avec la clé projet.');
    }
    if (['direct-link', 'project-page', 'expanded-group'].includes(raw.evidence.kind) && url === null) throw Error('URL de preuve absente.');
    if (['direct-link', 'project-page'].includes(raw.evidence.kind)) parseProjectUrl(url);
    if (raw.evidence.kind === 'expanded-group') parseUrl(url);
    if (raw.evidence.kind === 'direct-control' && url !== null) throw Error('Une preuve par attribut ne porte pas d’URL.');
    return Core.entityObservation({ ...raw, confidence: rank });
  }
  function visible(node, win) {
    if (!node || node.closest?.('[hidden], [aria-hidden="true"], [inert]')) return false;
    if (typeof node.checkVisibility === 'function') return node.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
    for (let p = node; p; p = p.parentElement) {
      const style = win.getComputedStyle?.(p);
      if (style?.display === 'none' || style?.visibility === 'hidden') return false;
    }
    return true;
  }
  function roots(doc, win) {
    const result = [...doc.querySelectorAll(ROOTS)];
    try { parseProjectUrl(win?.location.href); result.push(...doc.querySelectorAll('main, [role="main"]')); } catch { /* Pas de lecture/observation du contenu des conversations. */ }
    return [...new Set(result)];
  }
  function linkTitle(link, win) {
    const accessible = Core.text(link.getAttribute('aria-label'), Core.LIMITS.title);
    if (accessible) return { title: accessible, titleQuality: 2 };
    // Lire seulement le lien ; ignorer ses boutons d’options, sans toucher au DOM.
    const parts = []; let visited = 0;
    function read(node) {
      if (++visited > 512) return;
      if (node.nodeType === 3) { parts.push(node.nodeValue || ''); return; }
      if (node.nodeType !== 1 || node.matches?.('button, [role="button"], script, style') || !visible(node, win)) return;
      for (const child of node.childNodes || []) read(child);
    }
    read(link);
    return { title: Core.text(parts.join(' '), Core.LIMITS.title), titleQuality: 1 };
  }
  function scan(doc, win, mode = 'broad') {
    if (!allowedPage(win.location.href)) return [];
    let current = null;
    try { current = parseUrl(win.location.href); } catch { /* Accueil, projet ou autre page autorisée. */ }
    if (mode === 'targeted' && !current) return [];
    const found = new Map(); let checked = 0;
    for (const sidebar of roots(doc)) {
      if (!visible(sidebar, win)) continue;
      // Sélecteur éprouvé d’abord, puis fallback sémantique sans classes CSS.
      const selector = mode === 'targeted' ? `a[href*="/c/${current.identity}" i]` : 'a[data-sidebar-item][href*="/c/"], a[href*="/c/"]';
      for (const link of sidebar.querySelectorAll(selector)) {
        if (++checked > 20000) throw Error('Trop de liens rendus ; scan interrompu sans écriture.');
        if (!visible(link, win)) continue;
        const href = link.getAttribute('href');
        let parsed;
        try { parsed = parseUrl(href?.startsWith('/') && !href.startsWith('//') ? 'https://chatgpt.com' + href : href); } catch { continue; }
        if (mode === 'targeted' && parsed.identity !== current?.identity) continue;
        const title = linkTitle(link, win);
        const observation = { source: 'chatgpt', ...parsed, context: PROJECT_KEY.test(parsed.context || '') ? parsed.context : null, ...title, active: current ? parsed.identity === current.identity : link.hasAttribute('data-active') || link.getAttribute('aria-current') === 'page' };
        const key = parsed.identity + '|' + parsed.url;
        const previous = found.get(key);
        if (!previous || observation.titleQuality >= previous.titleQuality) found.set(key, observation);
      }
    }
    if (current && ![...found.values()].some(o => o.identity === current.identity && o.url === current.url)) found.set('current', { source: 'chatgpt', ...current, context: PROJECT_KEY.test(current.context || '') ? current.context : null, title: null, titleQuality: 0, active: true });
    return [...found.values()];
  }
  function auxiliary(node) { return node.hasAttribute('data-trailing-button') || node.getAttribute('aria-haspopup') === 'menu'; }
  function projectName(node, win) {
    if (auxiliary(node)) return null;
    const parts = []; let visited = 0, overflow = false;
    function read(child) {
      if (++visited > 512) { overflow = true; return; }
      if (child.nodeType === 3) { parts.push(child.nodeValue || ''); return; }
      if (child.nodeType !== 1 || !visible(child, win)) return;
      if (child !== node && child.matches('a, button, [role="button"], [role="group"], [role="treeitem"], svg, script, style')) return;
      for (const inner of child.childNodes || []) read(inner);
    }
    read(node);
    if (overflow) return null;
    // Le texte propre est préférable à un aria-label contenant une action/décoration.
    const value = parts.join(' ').replace(/\s+/g, ' ').trim() || node.getAttribute('aria-label');
    if (typeof value !== 'string' || !value.trim() || value.length > Core.LIMITS.name || /[\u0000-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]/.test(value) || /^(?:ouvrir\b|open\b|options?\b|couleur personnalisée\b|custom colou?r\b)/i.test(value.trim())) return null;
    return value.replace(/\s+/g, ' ').trim();
  }
  function scanProjects(doc, win, mode = 'broad', conversations = scan(doc, win, mode)) {
    if (!allowedPage(win.location.href)) return [];
    const allowed = new Set(conversations.map(o => o.context).filter(k => PROJECT_KEY.test(k || '')));
    let home = null;
    try { home = parseProjectUrl(win.location.href); allowed.add(home.identity); } catch { /* Conversation ou accueil général. */ }
    if (mode === 'targeted' && !allowed.size) return [];
    const candidates = new Map(); let checked = 0;
    function add(identity, name, kind, url) {
      if (!PROJECT_KEY.test(identity || '') || (mode === 'targeted' && !allowed.has(identity))) return;
      const observation = normalizeEntity({ source: 'chatgpt', identity, name, evidence: { kind: name === null ? 'key-only' : kind, url } });
      const group = candidates.get(identity) || []; group.push(observation); candidates.set(identity, group);
      if (candidates.size > Core.LIMITS.entities) throw Error('Trop de projets rendus ; aucun lot enregistré.');
    }
    for (const o of conversations) if (o.context) add(o.context, null, 'key-only', o.url);
    if (home) add(home.identity, null, 'key-only', home.url);
    for (const sidebar of [...doc.querySelectorAll(ROOTS)]) {
      if (!visible(sidebar, win)) continue;
      for (const control of sidebar.querySelectorAll('a[href*="/g/g-p-"], button[data-project-id], button[data-project-key], [role="treeitem"][data-project-id], [role="treeitem"][data-project-key], [role="button"][data-project-id], [role="button"][data-project-key]')) {
        if (++checked > 20000) throw Error('Trop de contrôles projet rendus.');
        if (!visible(control, win) || auxiliary(control)) continue;
        let direct = null;
        try { direct = parseProjectUrl(absolute(control.getAttribute('href'))); } catch { /* Attribut explicite ou lien de fil, qui n’est pas un nom de projet. */ }
        if (control.matches('a[href]') && !direct) continue;
        const attributes = ['data-project-id', 'data-project-key'].filter(a => control.hasAttribute(a)).map(a => control.getAttribute(a));
        const keys = [...attributes, ...(direct ? [direct.identity] : [])];
        if (!keys.length || keys.some(k => !PROJECT_KEY.test(k)) || new Set(keys).size !== 1) continue;
        const identity = keys[0];
        if (mode === 'targeted' && !allowed.has(identity)) continue;
        add(identity, projectName(control, win), direct ? 'direct-link' : 'direct-control', direct?.url || null);
      }
      for (const control of sidebar.querySelectorAll('button[aria-expanded="true"], [role="treeitem"][aria-expanded="true"]')) {
        if (++checked > 20000) throw Error('Trop de contrôles projet rendus.');
        if (!visible(control, win) || auxiliary(control)) continue;
        const name = projectName(control, win);
        if (/^(?:projets|projects|chats|discussions|historique de chat|chat history|épinglés|pinned|récents|recent)$/i.test(name || '')) continue;
        const groups = [];
        const id = control.getAttribute('aria-controls');
        if (id && /^[A-Za-z0-9_:-]{1,128}$/.test(id)) {
          const group = doc.getElementById(id), controlId = control.getAttribute('id');
          if (group && /^[A-Za-z0-9_:-]{1,128}$/.test(controlId || '') && doc.querySelectorAll(`[id="${id}"]`).length === 1 && doc.querySelectorAll(`[id="${controlId}"]`).length === 1 && sidebar.contains(group) && group.matches('[role="group"], [role="region"]') && (group.getAttribute('aria-labelledby') || '').split(/\s+/).includes(controlId)) groups.push(group);
        }
        if (control.matches('[role="treeitem"]')) {
          groups.push(...[...control.querySelectorAll('[role="group"]')].filter(g => g.closest('[role="treeitem"]') === control));
        } else if (control.querySelector('a[href*="/c/"]')) groups.push(control);
        for (const group of [...new Set(groups)]) {
          if (!visible(group, win)) continue;
          // Une section globale, un sous-projet ou un autre bouton expansible rompt la preuve.
          const competing = [...group.querySelectorAll('[role="treeitem"], button[aria-expanded], a[href*="/g/g-p-"]')].some(node => {
            if (node === control || auxiliary(node)) return false;
            if (node.matches('[role="treeitem"], button[aria-expanded]')) return true;
            try { parseProjectUrl(absolute(node.getAttribute('href'))); return true; } catch { return false; }
          });
          if (competing) continue;
          const links = [...group.querySelectorAll('a[href*="/c/"]')].filter(n => visible(n, win));
          const children = [];
          for (const link of links) {
            if (++checked > 20000) throw Error('Trop de liens dans les groupes projet.');
            try { children.push(parseUrl(absolute(link.getAttribute('href')))); } catch { /* Lien non utilisable. */ }
          }
          if (!children.length || children.some(c => !PROJECT_KEY.test(c.context || '')) || new Set(children.map(c => c.context)).size !== 1) continue;
          const identity = children[0].context;
          const explicit = ['data-project-id', 'data-project-key'].filter(a => control.hasAttribute(a)).map(a => control.getAttribute(a));
          if (explicit.some(k => k !== identity)) continue;
          if (mode === 'targeted' && !allowed.has(identity)) continue;
          add(identity, name, 'expanded-group', children[0].url);
        }
      }
    }
    if (home) {
      const titles = [...doc.querySelectorAll('main h1, [role="main"] h1')].filter(n => visible(n, win));
      if (titles.length === 1) add(home.identity, projectName(titles[0], win), 'project-page', home.url);
    }
    return [...candidates].map(([identity, group]) => {
      const known = group.filter(o => o.name !== null).sort((a, b) => b.confidence - a.confidence);
      const best = known[0];
      if (best && new Set(known.filter(o => o.confidence === best.confidence).map(o => o.name)).size === 1) return best;
      return normalizeEntity({ source: 'chatgpt', identity, name: null, evidence: { kind: 'key-only', url: group.find(o => o.evidence.url)?.evidence.url || null } });
    });
  }
  function scanBatch(doc, win, mode) { const observations = scan(doc, win, mode); return { observations, entities: scanProjects(doc, win, mode, observations) }; }
  function exportJson(state, now) {
    return Core.exportData(state, now, { source: 'mon-gpt-collector', collectionKey: 'conversations', normalize, normalizeEntity, entityKey: 'projects',
      mapEntity: p => ({ projectKey: p.identity, observedName: p.name, firstSeenAt: p.firstSeenAt, lastSeenAt: p.lastSeenAt, seenCount: p.seenCount, nameObservedAt: p.nameObservedAt, evidence: { ...p.evidence } }),
      map: r => ({ conversationId: r.identity, url: r.url, observedTitle: r.title, firstSeenAt: r.firstSeenAt, lastSeenAt: r.lastSeenAt, seenCount: r.seenCount,
        observedUrls: [...r.observedUrls].sort(), observedProjectKeys: [...r.contexts].sort(), lastObservedActive: r.active }) });
  }
  function relevantMutation(m) {
    const relevant = 'a[href], button[aria-expanded], [role="treeitem"], [data-project-id], [data-project-key], h1';
    if (m.type === 'attributes') return m.target.matches?.(relevant) || ['hidden', 'aria-hidden', 'style'].includes(m.attributeName);
    if (m.type === 'characterData') return Boolean(m.target.parentElement?.closest(relevant));
    return [...(m.addedNodes || []), ...(m.removedNodes || [])].some(n => n.nodeType === 1 && (n.matches?.(relevant) || n.querySelector?.(relevant))) || Boolean(m.target.closest?.(relevant));
  }
  return { source: 'chatgpt', ROOTS, parseUrl, parseProjectUrl, allowedPage, normalize, normalizeEntity, roots, visible, scan, scanProjects, scanBatch, relevantMutation, exportJson };
});
