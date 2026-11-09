import { once } from 'node:events';
import { BridgeError } from './connection.js';
import { MAX_BYTES, observe } from './bridge.js';

const controller = new AbortController();
for (const signal of ['SIGTERM', 'SIGINT']) process.once(signal, () => controller.abort());
process.stdout.on('error', () => controller.abort());
try {
  // Configuração única limitada via stdin; mudança de vínculos exige nova ponte.
  let input = '';
  for await (const chunk of process.stdin) {
    if (Buffer.byteLength(input) + chunk.length > MAX_BYTES) throw new BridgeError('oversized_configuration');
    input += chunk;
  }
  let config;
  try { config = JSON.parse(input); } catch { throw new BridgeError('invalid_configuration'); }
  await observe(config, { signal: controller.signal, emit: async line => {
    if (!process.stdout.write(line)) await once(process.stdout, 'drain', { signal: controller.signal });
  } });
} catch (error) {
  if (!controller.signal.aborted) {
    // Nunca imprimir stack, corpo remoto ou stdout/stderr bruto do transporte.
    process.stderr.write(JSON.stringify({ version: 1, category: error instanceof BridgeError ? error.category : 'transport_failed' }) + '\n');
    process.exitCode = 1;
  }
} finally {
  controller.abort();
}
