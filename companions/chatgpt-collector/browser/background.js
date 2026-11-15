'use strict';
importScripts('../core/observations.js', '../adapters/chatgpt.js', 'repository.js');
const repository = CollectorRepository.createRepository(chrome.storage.local, { source: ChatGPTAdapter.source, normalize: ChatGPTAdapter.normalize, normalizeEntity: ChatGPTAdapter.normalizeEntity });
function isPopup(sender) { return sender.id === chrome.runtime.id && sender.url === chrome.runtime.getURL('ui/popup.html'); }
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  if (message?.channel !== 'mon-gpt-collector-v2') return false;
  const popup = isPopup(sender);
  const content = sender.id === chrome.runtime.id && sender.tab && sender.frameId === 0 && ChatGPTAdapter.allowedPage(sender.url);
  if (!popup && !content) { respond({ ok: false, error: 'Origine de requête refusée.' }); return false; }
  (async () => {
    switch (message.type) {
      case 'state': {
        const { state, error } = await repository.get();
        return popup ? { state, error } : { mode: state.mode, error };
      }
      case 'ingest':
        if (!content || !['manual', 'auto'].includes(message.kind)) throw Error('Collecte refusée.');
        return { summary: await repository.ingest({ observations: message.observations, entities: message.entities }, message.requestId, message.kind) };
      case 'mode':
        if (!popup) throw Error('Commande réservée à la popup.');
        return { state: await repository.setMode(message.mode) };
      case 'clear':
        if (!popup) throw Error('Commande réservée à la popup.');
        return { state: await repository.clear() };
      default: throw Error('Commande inconnue.');
    }
  })().then(result => respond({ ok: true, ...result }), error => respond({ ok: false, error: error.message || 'Stockage indisponible.' }));
  return true;
});
