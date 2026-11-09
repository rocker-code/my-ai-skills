import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { test } from 'node:test';
import { connect } from '../connection.js';
import { metadataFetch } from '../transport.js';
import { TYPES } from '../protocol.js';

async function server(t, handler) {
  const http = createServer(handler);
  await new Promise(resolve => http.listen(0, '127.0.0.1', resolve));
  t.after(() => { http.closeAllConnections(); http.close(); });
  return `http://127.0.0.1:${http.address().port}`;
}

test('cliente instalado categoriza senha ausente e negada sem vazar corpo', async t => {
  const url = await server(t, (_request, response) => {
    response.writeHead(401, { 'content-type': 'application/json' });
    response.end(JSON.stringify({ _tag: 'UnauthorizedError', message: 'SEGREDO_FIXTURE' }));
  });
  await assert.rejects(connect({ server: url, env: {} }), /^Error: authentication_required$/);
  await assert.rejects(connect({ server: url, env: { OPENCODE_PASSWORD: 'SEGREDO_FIXTURE' } }), /^Error: authentication_denied$/);
});

test('cliente instalado filtra na requisição HTTP, sanitiza IPC e cancela assinatura', async t => {
  const created = Date.now();
  let subscriptionURL;
  let feedClosed;
  const closed = new Promise(resolve => { feedClosed = resolve; });
  const url = await server(t, (request, response) => {
    if (request.url === '/api/info') {
      response.setHeader('content-type', 'application/json');
      response.end(JSON.stringify({ version: '2.2.5', pid: 1234 }));
    } else if (request.url === '/api/session/ses_fixture') {
      response.setHeader('content-type', 'application/json');
      response.end(JSON.stringify({ data: { id: 'ses_fixture', location: { directory: '/fixture/worktree' } } }));
    } else if (request.url.startsWith('/api/event')) {
      subscriptionURL = new URL(request.url, 'http://fixture');
      if (JSON.stringify(subscriptionURL.searchParams.getAll('types')) !== JSON.stringify(TYPES)) {
        response.writeHead(400); response.end(); return;
      }
      response.writeHead(200, { 'content-type': 'text/event-stream' });
      response.write('data: ' + JSON.stringify({ type: 'form.created', id: 'evt_fixture', created,
        location: { directory: '/fixture/worktree' }, data: { form: {
          id: 'frm_fixture', sessionID: 'ses_fixture', title: 'SEGREDO_FIXTURE', fields: [],
        } } }) + '\n\n');
      request.on('close', feedClosed);
    } else {
      response.writeHead(404); response.end();
    }
  });
  const child = spawn(process.execPath, [new URL('../main.js', import.meta.url).pathname], {
    env: { ...process.env, OPENCODE_PASSWORD: 'SEGREDO_FIXTURE' }, stdio: ['pipe', 'pipe', 'pipe'],
  });
  t.after(() => { if (child.exitCode === null) child.kill('SIGKILL'); });
  child.stdin.end(JSON.stringify({ version: 1, server: url,
    context: { endpoint: url, version: '2.2.5', pid: 1234 },
    bindings: [{ session_id: 'ses_fixture', revision: 'rev_fixture', worktree: '/fixture/worktree',
      bound_at: new Date(created - 1000).toISOString() }],
  }));
  let output = '', errors = '';
  child.stderr.on('data', chunk => { errors += chunk; });
  const gotLine = new Promise(resolve => child.stdout.on('data', chunk => {
    output += chunk;
    if (output.includes('\n')) resolve();
  }));
  const timeout = AbortSignal.timeout(5000);
  await Promise.race([gotLine, once(child, 'exit').then(([code]) => { throw new Error(`saída prematura: ${code} ${errors}`); }),
    once(timeout, 'abort').then(() => { throw new Error('timeout incremental'); })]);
  assert.equal(JSON.parse(output.trim()).request_id, 'frm_fixture');
  assert.deepEqual(subscriptionURL.searchParams.getAll('types'), TYPES);
  assert.deepEqual([...new Set(subscriptionURL.searchParams.keys())], ['types']);
  const exited = once(child, 'exit');
  child.kill('SIGTERM');
  const [code] = await exited;
  assert.equal(code, 0);
  await Promise.race([closed, once(timeout, 'abort').then(() => { throw new Error('assinatura não encerrada'); })]);
  assert.equal(errors, '');
  assert.ok(!output.includes('SEGREDO_FIXTURE'));
});

test('fetch preserva autenticação e cancelamento, sem broaden de tipos ou redirects', async () => {
  const requests = [];
  const controller = new AbortController();
  const transport = metadataFetch('https://fixture/prefix', async request => {
    requests.push(request); return new Response('{}');
  });
  await transport(new URL('https://fixture/prefix/api/event?types=session.text.delta'), {
    signal: controller.signal, headers: { authorization: 'Basic fixture' },
  });
  const request = requests[0];
  assert.deepEqual(new URL(request.url).searchParams.getAll('types'), TYPES);
  assert.equal(request.headers.get('authorization'), 'Basic fixture');
  assert.equal(request.redirect, 'error');
  controller.abort();
  assert.equal(request.signal.aborted, true);
  await transport('https://fixture/prefix/api/info?fixture=1');
  assert.equal(requests[1].url, 'https://fixture/prefix/api/info?fixture=1');
  assert.ok(TYPES.every(type => !/text|reasoning|skill|tool/.test(type)));
});

test('entrada inválida produz somente diagnóstico categorizado', async () => {
  const child = spawn(process.execPath, [new URL('../main.js', import.meta.url).pathname]);
  let output = '', errors = '';
  child.stdout.on('data', chunk => { output += chunk; });
  child.stderr.on('data', chunk => { errors += chunk; });
  const exited = once(child, 'exit');
  child.stdin.end('SEGREDO_FIXTURE');
  const [code] = await exited;
  assert.equal(code, 1);
  assert.equal(output, '');
  assert.deepEqual(JSON.parse(errors), { version: 1, category: 'invalid_configuration' });
});
