'use strict';
// Petit arbre sémantique pour fixtures unitaires. Les mêmes scénarios passent
// ensuite dans le moteur DOM de Chrome : ce helper n’est pas un navigateur.
function documentFrom(html) {
  const decode = text => text.replace(/&(?:amp|lt|gt|quot|apos);/g, v => ({ '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'" }[v]));
  class Element {
    constructor(tag, attrs = {}) { this.nodeType = 1; this.tag = tag; this.attrs = attrs; this.childNodes = []; this.parentElement = null; }
    get children() { return this.childNodes.filter(n => n.nodeType === 1); }
    getAttribute(key) { return Object.hasOwn(this.attrs, key) ? this.attrs[key] : null; }
    hasAttribute(key) { return Object.hasOwn(this.attrs, key); }
    append(node) { node.parentElement = this; this.childNodes.push(node); }
    contains(node) { return node === this || this.children.some(c => c.contains(node)); }
    checkVisibility() { return !this.closest('[hidden], [aria-hidden="true"], [inert]'); }
    matches(selector) {
      return selector.split(',').some(part => {
        const chain = part.trim().split(/\s+(?![^\[]*\])/); let node = this;
        if (!simple(node, chain.pop())) return false;
        while (chain.length) { const previous = chain.pop(); node = node.parentElement; while (node && !simple(node, previous)) node = node.parentElement; if (!node) return false; }
        return true;
      });
    }
    closest(selector) { for (let n = this; n; n = n.parentElement) if (n.matches(selector)) return n; return null; }
    querySelectorAll(selector) { const result = []; const walk = n => { for (const child of n.children) { if (child.matches(selector)) result.push(child); walk(child); } }; walk(this); return result; }
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  }
  function simple(node, selector) {
    if (!selector) return false;
    let good = true;
    const tag = selector.replace(/\[([\w-]+)(?:([*^~]?=)"([^"]*)"\s*(i)?)?\]/g, (_, key, op, value, insensitive) => {
      let actual = node.getAttribute(key);
      if (actual === null) good = false;
      else if (op) {
        if (insensitive) { actual = actual.toLowerCase(); value = value.toLowerCase(); }
        good = good && (op === '=' ? actual === value : op === '*=' ? actual.includes(value) : op === '^=' ? actual.startsWith(value) : actual.split(/\s+/).includes(value));
      }
      return '';
    }).trim();
    return good && (!tag || tag === '*' || tag === node.tag);
  }
  const root = new Element('document'), stack = [root];
  for (const token of html.match(/<!--[\s\S]*?-->|<[^>]+>|[^<]+/g) || []) {
    if (token.startsWith('<!--') || token.startsWith('<!')) continue;
    if (token.startsWith('</')) { stack.pop(); continue; }
    if (token.startsWith('<')) {
      const tag = token.match(/^<([\w-]+)/)?.[1]; if (!tag) continue;
      const attrs = {};
      for (const a of token.slice(tag.length + 1, -1).matchAll(/([\w-]+)(?:="([^"]*)")?/g)) attrs[a[1]] = decode(a[2] ?? '');
      const node = new Element(tag, attrs); stack.at(-1).append(node);
      if (!['input', 'img', 'br', 'hr', 'meta', 'link'].includes(tag) && !token.endsWith('/>')) stack.push(node);
    } else stack.at(-1).append({ nodeType: 3, nodeValue: decode(token) });
  }
  root.getElementById = id => root.querySelectorAll('[id]').find(n => n.getAttribute('id') === id) || null;
  return root;
}
module.exports = { documentFrom };
