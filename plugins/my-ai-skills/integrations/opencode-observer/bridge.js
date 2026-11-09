import { BridgeError, connect } from './connection.js';

import { MAX_BYTES, TYPES } from './protocol.js';
export { MAX_BYTES, TYPES } from './protocol.js';
const safeID = value => typeof value === 'string' && /^[A-Za-z0-9_][A-Za-z0-9_.:-]{0,199}$/.test(value);
const timestamp = value => typeof value === 'number' && Number.isSafeInteger(value) && value >= 0 && value <= 8640000000000000;
const directory = value => typeof value === 'string' && value.startsWith('/') && value.length <= 4096 && !/[\x00-\x1f]/.test(value);
const fail = category => { throw new BridgeError(category); };

export function configuration(input) {
  if (!input || input.version !== 1 || !Array.isArray(input.bindings) || input.bindings.length > 1000 ||
      !input.context || input.context.version !== '2.2.5' || !Number.isSafeInteger(input.context.pid) ||
      input.context.pid <= 0 || typeof input.context.endpoint !== 'string') fail('invalid_configuration');
  if (Object.keys(input.context).some(key => !['endpoint', 'version', 'pid'].includes(key))) fail('invalid_configuration');
  const sessions = new Set();
  for (const binding of input.bindings) {
    if (!safeID(binding.session_id) || !binding.session_id.startsWith('ses') ||
        !safeID(binding.revision) || !directory(binding.worktree) ||
        !Number.isFinite(Date.parse(binding.bound_at)) || sessions.has(binding.session_id)) fail('invalid_configuration');
    sessions.add(binding.session_id);
  }
  if (input.server !== undefined && input.server !== input.context.endpoint) fail('context_changed');
  if (input.server === undefined && input.context.endpoint !== 'shared-discovery') fail('context_changed');
  return input;
}

// Nenhum conteúdo de data/metadata/erro é transmitido por cópia genérica.
export function project(event, config, received = new Date().toISOString(), verifiedDirectory) {
  if (!event || typeof event !== 'object' || !['server.connected', ...TYPES].includes(event.type)) return null;
  // OpenCode 2.2.5 emits server.connected without created. It is only a
  // connection marker, so use receipt time; session events still require their
  // original server timestamp for correlation and coverage.
  const created = event.type === 'server.connected' && event.created === undefined
    ? Date.parse(received) : event.created;
  if (!safeID(event.id) || !event.id.startsWith('evt_') || !timestamp(created) ||
      !event.data || typeof event.data !== 'object') fail('invalid_event');
  if (Buffer.byteLength(JSON.stringify(event)) > MAX_BYTES) fail('oversized_event');
  const base = { version: 1, type: event.type, event_id: event.id, created,
    received_at: received, context: config.context };
  if (event.type === 'server.connected') return base;
  if (event.type === 'location.shutdown') {
    if (!config.bindings.some(b => b.worktree === event.location?.directory)) return null;
    return base;
  }
  const data = event.type === 'form.created' ? event.data.form : event.data;
  if (!data || typeof data !== 'object') fail('invalid_event');
  const binding = config.bindings.find(b => b.session_id === data.sessionID);
  if (!binding) return null;
  if ((event.location?.directory ?? verifiedDirectory) !== binding.worktree) fail('context_changed');
  if (event.created < Date.parse(binding.bound_at)) return null;
  const result = { ...base, session_id: binding.session_id, binding_revision: binding.revision };
  if (event.type.startsWith('session.execution.')) {
    if (event.durable?.aggregateID !== binding.session_id || event.durable?.version !== 1 ||
        !Number.isSafeInteger(event.durable?.seq) || event.durable.seq < 0) fail('invalid_event');
    result.sequence = event.durable.seq;
  } else if (event.type.startsWith('permission.')) {
    const request = event.type === 'permission.asked' ? data.id : data.requestID;
    if (!safeID(request) || !request.startsWith('per')) fail('invalid_event');
    result.request_id = request;
    if (event.type === 'permission.replied') {
      if (!['once', 'always', 'reject'].includes(data.reply)) fail('invalid_event');
      result.resolution = data.reply === 'reject' ? 'rejected' : 'answered';
    }
  } else if (event.type.startsWith('form.')) {
    if (!safeID(data.id) || !data.id.startsWith('frm_')) fail('invalid_event');
    result.request_id = data.id;
  }
  return result;
}

export async function observe(input, { signal, emit, connection = connect } = {}) {
  const config = configuration(input);
  if (!config.bindings.length) fail('no_bindings');
  const { client, context } = await connection({ server: config.server, signal });
  if (['endpoint', 'version', 'pid'].some(key => context[key] !== config.context[key])) fail('context_changed');
  for (const binding of config.bindings) {
    const session = await client.session.get({ sessionID: binding.session_id }, { signal: AbortSignal.any([
      ...(signal ? [signal] : []), AbortSignal.timeout(5000),
    ]) });
    // O cliente Promise desembrulha data; a CLI HTTP mantém o envelope.
    if (session?.id !== binding.session_id || session?.location?.directory !== binding.worktree) fail('context_changed');
  }
  for await (const event of client.event.subscribe({ types: TYPES, signal })) {
    if (signal?.aborted) break;
    let verifiedDirectory;
    if (TYPES.includes(event?.type) && event.type !== 'location.shutdown' && !event.location?.directory) {
      const data = event.type === 'form.created' ? event.data?.form : event.data;
      const binding = config.bindings.find(b => b.session_id === data?.sessionID);
      if (binding) {
        // V2 events may omit location. Revalidate the session instead of
        // trusting a cached checkout or treating an unlocated event as proof.
        const session = await client.session.get({ sessionID: binding.session_id }, { signal: AbortSignal.any([
          ...(signal ? [signal] : []), AbortSignal.timeout(5000),
        ]) });
        if (session?.id !== binding.session_id || session?.location?.directory !== binding.worktree) fail('context_changed');
        verifiedDirectory = session.location.directory;
      }
    }
    const result = project(event, config, new Date().toISOString(), verifiedDirectory);
    if (!result) continue;
    const line = JSON.stringify(result) + '\n';
    if (Buffer.byteLength(line) > MAX_BYTES) fail('oversized_event');
    await emit(line);
    if (['location.shutdown', 'session.moved'].includes(event.type)) fail('context_changed');
  }
  if (!signal?.aborted) fail('stream_ended');
}
