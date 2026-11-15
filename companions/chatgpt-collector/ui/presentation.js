/* Présentation commune : aucune extraction DOM de site, aucune règle d’identité. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.CollectorPresentation = api;
})(globalThis, function () {
  'use strict';
  const MODES = {
    manual: { name: 'Manuel', description: 'Aucune collecte automatique. Vous décidez quand scanner la page.' },
    targeted: { name: 'Auto cible', description: 'Seulement la discussion ouverte. Le titre reste inconnu si son lien n’est pas observable.' },
    broad: { name: 'Auto large', description: 'Les liens déjà rendus dans la sidebar. Peut conserver beaucoup de discussions, sans ouvrir les projets.' }
  };
  function listModel(records, limit = 50) {
    return [...records].sort((a, b) => b.lastSeenAt.localeCompare(a.lastSeenAt) || a.identity.localeCompare(b.identity)).slice(0, limit)
      .map(r => ({ title: r.title || 'Titre non observé', url: r.url,
        context: r.contexts.length ? 'Projet dans l’URL' : 'Lien de discussion',
        active: r.active, seenCount: r.seenCount, date: r.lastSeenAt }));
  }
  function downloadTextFile(doc, filename, content, type) {
    // Réemploi du téléchargement Blob de MJ Collector ; révocation différée.
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = doc.createElement('a'); link.href = url; link.download = filename;
    doc.body.appendChild(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function renderList(doc, list, records, { emptyHeading = 'Votre prochaine idée commence ici', emptyText = 'Aucun lien observé pour le moment.' } = {}) {
    const scroll = list.scrollTop;
    const focusedUrl = list.contains(doc.activeElement) ? doc.activeElement.href : null;
    list.textContent = '';
    const items = listModel(records);
    if (!items.length) {
      const empty = doc.createElement('li'); empty.className = 'empty';
      const heading = doc.createElement('strong'); heading.textContent = emptyHeading;
      const note = doc.createElement('span'); note.textContent = emptyText;
      empty.append(heading, note); list.append(empty); return;
    }
    for (const item of items) {
      const row = doc.createElement('li'); row.className = 'conversation';
      const mark = doc.createElement('span'); mark.className = 'conversation-mark'; mark.textContent = '↗'; mark.setAttribute('aria-hidden', 'true');
      const body = doc.createElement('div'); body.className = 'conversation-body';
      const title = doc.createElement('a'); title.className = 'conversation-title'; title.textContent = item.title; title.title = item.title;
      title.href = item.url; title.target = '_blank'; title.rel = 'noopener noreferrer';
      const details = doc.createElement('div'); details.className = 'conversation-details';
      const label = doc.createElement('span'); label.textContent = item.active ? 'Active au relevé' : item.context;
      if (item.active) label.className = 'active-note';
      const time = doc.createElement('time'); time.dateTime = item.date;
      time.textContent = new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(item.date));
      time.title = `${item.seenCount} relevé(s) · ${item.date}`;
      details.append(label, time); body.append(title, details); row.append(mark, body); list.append(row);
    }
    list.scrollTop = scroll;
    if (focusedUrl) [...list.querySelectorAll('a')].find(a => a.href === focusedUrl)?.focus({ preventScroll: true });
  }
  return { MODES, listModel, renderList, downloadTextFile };
});
