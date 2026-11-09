import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { observe, project, configuration, TYPES } from '../bridge.js';

const fixture = JSON.parse(await readFile(new URL('../../../tests/fixtures/opencode-observer-2.2.5.json', import.meta.url)));
const context = { endpoint: 'shared-discovery', version: '2.2.5', pid: 1234 };
const config = { version: 1, context, bindings: [{ session_id: 'ses_fixture', revision: 'rev_fixture',
  worktree: '/fixture/worktree', bound_at: '2026-11-08T23:59:59Z' }] };
// Horário inicial anterior a todos os eventos sintéticos.
config.bindings[0].bound_at = new Date(fixture.events[0].created - 1000).toISOString();

test('projeção de todos os tipos mantém somente metadados', () => {
  configuration(config);
  for (const event of fixture.events) {
    const altered = structuredClone(event);
    altered.metadata = { secret: 'SEGREDO_FIXTURE' };
    altered.data.answer = { secret: 'SEGREDO_FIXTURE' };
    altered.data.error = { message: 'SEGREDO_FIXTURE' };
    if (altered.data.form) altered.data.form.title = 'SEGREDO_FIXTURE';
    const projected = project(altered, config);
    assert.ok(projected);
    assert.ok(!JSON.stringify(projected).includes('SEGREDO_FIXTURE'));
    assert.ok(!Object.hasOwn(projected, 'answer'));
    assert.equal(projected.created, event.created);
  }
});

test('marcador real sem created usa recebimento, sem relaxar eventos de sessão', () => {
  const received = '2026-11-09T03:50:00.000Z';
  const marker = { id: 'evt_connected', type: 'server.connected', data: {} };
  assert.equal(project(marker, config, received).created, Date.parse(received));
  const session = structuredClone(fixture.events[1]);
  delete session.created;
  assert.throws(() => project(session, config, received), /invalid_event/);
});

test('sessão alheia, evento anterior ao bind e conteúdo não permitido são ignorados', () => {
  const event = structuredClone(fixture.events[1]);
  event.data.sessionID = 'ses_other';
  assert.equal(project(event, config), null);
  assert.equal(project({ type: 'session.text.delta', data: { text: 'SEGREDO_FIXTURE' } }, config), null);
  event.data.sessionID = 'ses_fixture';
  event.created = Date.parse(config.bindings[0].bound_at) - 1;
  assert.equal(project(event, config), null);
});

test('contexto divergente, evento inválido e grande invalidam continuidade', () => {
  const event = structuredClone(fixture.events[1]);
  event.location.directory = '/other';
  assert.throws(() => project(event, config), /context_changed/);
  event.location.directory = '/fixture/worktree';
  event.created = 'secret';
  assert.throws(() => project(event, config), /invalid_event/);
  event.created = fixture.events[1].created;
  event.data.error = 'secret'.repeat(3000);
  assert.throws(() => project(event, config), /oversized_event/);
});

test('assinatura tipada cancelável só consulta sessões permitidas', async () => {
  const controller = new AbortController();
  const lines = [];
  const connection = async () => ({ context, client: {
    session: { get: async ({ sessionID }) => {
      assert.equal(sessionID, 'ses_fixture');
      return { id: sessionID, location: { directory: '/fixture/worktree' } };
    } },
    event: { subscribe: async function* (options) {
      assert.deepEqual(options.types, TYPES);
      assert.equal(options.signal, controller.signal);
      yield fixture.events[0];
      controller.abort();
    } },
  } });
  await observe(config, { signal: controller.signal, connection, emit: async line => lines.push(JSON.parse(line)) });
  assert.equal(lines.length, 1);
});

test('evento sem location exige revalidação da sessão antes de projetar', async () => {
  const event = structuredClone(fixture.events.find(item => item.type === 'session.execution.started'));
  delete event.location;
  assert.throws(() => project(event, config), /context_changed/);
  for (const directory of ['/fixture/worktree', '/other']) {
    const controller = new AbortController();
    let queries = 0;
    const lines = [];
    const connection = async () => ({ context, client: {
      session: { get: async () => {
        queries++;
        return { id: 'ses_fixture', location: { directory: queries === 1 ? '/fixture/worktree' : directory } };
      } },
      event: { subscribe: async function* () { yield event; } },
    } });
    if (directory === '/other') {
      await assert.rejects(observe(config, { signal: controller.signal, connection, emit: async line => lines.push(line) }), /context_changed/);
      assert.equal(lines.length, 0);
    } else {
      await observe(config, { signal: controller.signal, connection, emit: async line => {
        lines.push(JSON.parse(line));
        controller.abort();
      } });
      assert.equal(lines[0].type, 'session.execution.started');
    }
    assert.equal(queries, 2);
  }
});

test('fim inesperado e contexto alterado falham sem publicar confirmação', async () => {
  await assert.rejects(observe(config, { connection: async () => ({ context: { ...context, pid: 2345 } }) }), /context_changed/);
  assert.throws(() => configuration({ ...config, bindings: [...config.bindings, ...config.bindings] }), /invalid_configuration/);
});
