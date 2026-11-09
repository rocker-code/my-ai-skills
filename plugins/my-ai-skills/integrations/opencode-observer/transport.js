import { TYPES } from './protocol.js';

// Extensão pública fetch do cliente oficial; não substitui seu parser SSE/auth.
// A allowlist também vai ao servidor, pois o cliente 2.2.5 só filtra localmente.
export function metadataFetch(baseUrl, fetch = globalThis.fetch) {
  const base = new URL(baseUrl);
  if (!base.pathname.endsWith('/')) base.pathname += '/';
  const subscription = new URL('api/event', base);
  return (input, init) => {
    const request = new Request(input, init);
    const url = new URL(request.url);
    if (url.origin === subscription.origin && url.pathname === subscription.pathname) {
      if (request.method !== 'GET') throw new Error('invalid_subscription');
      // Não confiar na lista do cliente compartilhado nem aceitar filtro vazio.
      url.search = '';
      for (const type of TYPES) url.searchParams.append('types', type);
      return fetch(new Request(url, { ...init, method: request.method, headers: request.headers,
        signal: request.signal, redirect: 'error' }));
    }
    return fetch(request);
  };
}
