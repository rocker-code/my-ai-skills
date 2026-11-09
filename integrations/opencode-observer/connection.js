import { OpenCode, isUnauthorizedError } from '@opencode/client';
import { Service } from '@opencode/client/service';
import { metadataFetch } from './transport.js';

export class BridgeError extends Error {
  constructor(category) {
    super(category);
    this.category = category;
  }
}

// Erros públicos nunca incluem corpo remoto, URL, credencial ou causa bruta.
export async function connect({ server, env = process.env, signal } = {},
                              { service = Service, make = OpenCode.make } = {}) {
  let endpoint;
  try {
    if (server !== undefined) {
      const url = new URL(server);
      if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
        throw new BridgeError('invalid_endpoint');
      }
      const password = env.OPENCODE_PASSWORD ?? env.OPENCODE_SERVER_PASSWORD;
      endpoint = { url: server, ...(password ? { auth: { type: 'basic', username: 'opencode', password } } : {}) };
    } else {
      endpoint = await service.discover({ version: '2.2.5' });
      if (!endpoint) throw new BridgeError('service_unavailable');
    }
    const client = make({ baseUrl: endpoint.url, headers: service.headers(endpoint), fetch: metadataFetch(endpoint.url) });
    const info = await client.server.info({ signal: AbortSignal.any([
      ...(signal ? [signal] : []), AbortSignal.timeout(5000),
    ]) });
    if (info?.version !== '2.2.5' || !Number.isSafeInteger(info?.pid) || info.pid <= 0) {
      throw new BridgeError('incompatible_contract');
    }
    return { client, context: { endpoint: server ?? 'shared-discovery', version: info.version, pid: info.pid } };
  } catch (error) {
    if (error instanceof BridgeError) throw error;
    if (isUnauthorizedError(error)) {
      throw new BridgeError(endpoint?.auth ? 'authentication_denied' : 'authentication_required');
    }
    throw new BridgeError(signal?.aborted ? 'cancelled' : 'connection_failed');
  }
}
