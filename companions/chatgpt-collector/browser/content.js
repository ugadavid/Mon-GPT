(function () {
  'use strict';
  if (!ChatGPTAdapter.allowedPage(location.href)) return;
  async function send(message) {
    try {
      if (!chrome.runtime?.id) throw Error('Extension context invalidated');
      const response = await chrome.runtime.sendMessage({ channel: 'mon-gpt-collector-v2', ...message });
      if (!response?.ok) throw Error(response?.error || 'Extension indisponible ; actualisez cet onglet.');
      return response;
    } catch (error) {
      if (/invalidated|context.*invalid/i.test(error.message || '')) runtime.dispose();
      throw error;
    }
  }
  const runtime = CollectorRuntime.createRuntime({ win: window, doc: document, adapter: ChatGPTAdapter, send });
  chrome.runtime.onMessage.addListener((message, sender, respond) => {
    if (sender.id !== chrome.runtime.id || message?.channel !== 'mon-gpt-collector-v2') return false;
    if (message.type === 'pageStatus') { respond({ ok: true, ...runtime.status() }); return false; }
    if (message.type !== 'scanCurrentPage') return false;
    runtime.manual().then(summary => respond({ ok: true, ...summary }), error => respond({ ok: false, error: error.message }));
    return true;
  });
  chrome.storage.onChanged.addListener((changes, area) => {
    const change = changes.monGptCollectorStateV2;
    if (area === 'local' && change && change.newValue?.mode !== runtime.status().mode) runtime.applyMode(change.newValue?.mode);
  });
  window.addEventListener('pagehide', () => runtime.dispose(), { once: true });
  send({ type: 'state' }).then(result => runtime.applyMode(result.mode)).catch(() => runtime.applyMode('manual'));
})();
