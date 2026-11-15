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
    return Core.observation({ ...raw, ...parsed, source: 'chatgpt' });
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
  function roots(doc) { return [...doc.querySelectorAll(ROOTS)]; }
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
        const observation = { source: 'chatgpt', ...parsed, ...title, active: current ? parsed.identity === current.identity : link.hasAttribute('data-active') || link.getAttribute('aria-current') === 'page' };
        const key = parsed.identity + '|' + parsed.url;
        const previous = found.get(key);
        if (!previous || observation.titleQuality >= previous.titleQuality) found.set(key, observation);
      }
    }
    if (current && ![...found.values()].some(o => o.identity === current.identity && o.url === current.url)) found.set('current', { source: 'chatgpt', ...current, title: null, titleQuality: 0, active: true });
    return [...found.values()];
  }
  function exportJson(state, now) {
    return Core.exportData(state, now, { source: 'mon-gpt-collector', collectionKey: 'conversations', normalize,
      map: r => ({ conversationId: r.identity, url: r.url, observedTitle: r.title, firstSeenAt: r.firstSeenAt, lastSeenAt: r.lastSeenAt, seenCount: r.seenCount,
        observedUrls: [...r.observedUrls].sort(), observedProjectKeys: [...r.contexts].sort(), lastObservedActive: r.active }) });
  }
  function relevantMutation(m) {
    if (m.type === 'attributes') return m.target.matches?.('a[href]') || ['hidden', 'aria-hidden', 'style'].includes(m.attributeName);
    if (m.type === 'characterData') return Boolean(m.target.parentElement?.closest('a[href]'));
    return [...(m.addedNodes || []), ...(m.removedNodes || [])].some(n => n.nodeType === 1 && (n.matches?.('a[href]') || n.querySelector?.('a[href]'))) || Boolean(m.target.closest?.('a[href]'));
  }
  return { source: 'chatgpt', ROOTS, parseUrl, allowedPage, normalize, roots, visible, scan, relevantMutation, exportJson };
});
