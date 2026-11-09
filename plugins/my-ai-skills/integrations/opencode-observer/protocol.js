export const MAX_BYTES = 16 * 1024;
export const TYPES = Object.freeze([
  'location.shutdown', 'session.moved',
  'session.execution.started', 'session.execution.succeeded',
  'session.execution.failed', 'session.execution.interrupted',
  'permission.asked', 'permission.replied', 'form.created', 'form.replied', 'form.cancelled',
]);
