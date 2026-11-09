import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { OpenCode } from '@opencode/client';
import { Service } from '@opencode/client/service';
import { connect } from '../connection.js';

test('import instalado e descoberta oficial sem iniciar serviço', async () => {
  assert.equal(typeof OpenCode.make, 'function');
  const root = await mkdtemp(join(tmpdir(), 'aew-discover-'));
  try {
    assert.equal(await Service.discover({ file: join(root, 'absent.json'), version: '2.2.5' }), undefined);
  } finally {
    await rm(root, { recursive: true });
  }
});

function dependencies() {
  const calls = [];
  return {
    calls,
    service: {
      discover: async options => { calls.push(options); return { url: 'http://localhost:4096' }; },
      headers: Service.headers,
    },
    make: options => { calls.push(options); return { server: { info: async () => ({ version: '2.2.5', pid: 1234 }) } }; },
  };
}

test('descoberta exige versão fixada e revalida identidade', async () => {
  const deps = dependencies();
  const result = await connect({}, deps);
  assert.deepEqual(deps.calls[0], { version: '2.2.5' });
  assert.deepEqual(result.context, { endpoint: 'shared-discovery', version: '2.2.5', pid: 1234 });
});

test('servidor explícito usa autenticação oficial, sem descoberta ou fallback', async () => {
  for (const env of [{ OPENCODE_PASSWORD: 'fixture' }, { OPENCODE_SERVER_PASSWORD: 'fixture' },
                    { OPENCODE_PASSWORD: 'fixture', OPENCODE_SERVER_PASSWORD: 'ignored' }]) {
    const deps = dependencies();
    const result = await connect({ server: 'http://localhost:4096', env }, deps);
    assert.equal(deps.calls.length, 1);
    assert.deepEqual(deps.calls[0].headers, Service.headers({ url: 'http://localhost:4096',
      auth: { type: 'basic', username: 'opencode', password: 'fixture' } }));
    assert.ok(!JSON.stringify(result.context).includes('fixture'));
  }
});

test('erros e versões divergentes são sanitizados', async () => {
  const deps = dependencies();
  deps.make = () => ({ server: { info: async () => { throw new Error('segredo-fixture'); } } });
  await assert.rejects(connect({ server: 'http://localhost:4096' }, deps), /^Error: connection_failed$/);
  deps.make = () => ({ server: { info: async () => ({ version: '2.2.6', pid: 1234 }) } });
  await assert.rejects(connect({}, deps), /^Error: incompatible_contract$/);
  await assert.rejects(connect({ server: 'http://user:secret@localhost' }, deps), /^Error: invalid_endpoint$/);
});
