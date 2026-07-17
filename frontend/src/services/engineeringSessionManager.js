const STORAGE_KEY = 'atlas.engineering.sessions.v1';
const ACTIVE_KEY = 'atlas.engineering.active-session.v1';
const VALID_STATUSES = new Set(['active', 'paused', 'completed']);

function nowIso() {
  return new Date().toISOString();
}

function cleanText(value, maxLength = 500) {
  return typeof value === 'string' ? value.trim().slice(0, maxLength) : '';
}

function makeId(prefix = 'session') {
  const random = Math.random().toString(36).slice(2, 9);
  return `${prefix}-${Date.now()}-${random}`;
}

function safeStorage() {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage || null;
  } catch (_) {
    return null;
  }
}

function sanitizeTimeline(value) {
  if (!Array.isArray(value)) return [];
  return value
    .filter((entry) => entry && typeof entry === 'object')
    .map((entry) => ({
      id: cleanText(entry.id, 120) || makeId('event'),
      type: cleanText(entry.type, 80) || 'note',
      message: cleanText(entry.message, 500),
      at: cleanText(entry.at, 80) || nowIso(),
      actor: cleanText(entry.actor, 80) || 'atlas',
    }))
    .filter((entry) => entry.message)
    .slice(-200);
}

function sanitizeSession(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const projectId = cleanText(value.projectId, 160);
  if (!projectId) return null;

  return {
    id: cleanText(value.id, 160) || makeId(),
    projectId,
    projectName: cleanText(value.projectName, 200),
    leadPersona: cleanText(value.leadPersona, 80) || 'hermes',
    status: VALID_STATUSES.has(value.status) ? value.status : 'active',
    activeGoal: cleanText(value.activeGoal, 500),
    secondaryGoals: Array.isArray(value.secondaryGoals)
      ? value.secondaryGoals.map((goal) => cleanText(goal, 300)).filter(Boolean).slice(0, 12)
      : [],
    constraints: Array.isArray(value.constraints)
      ? value.constraints.map((item) => cleanText(item, 300)).filter(Boolean).slice(0, 20)
      : [],
    successCriteria: Array.isArray(value.successCriteria)
      ? value.successCriteria.map((item) => cleanText(item, 300)).filter(Boolean).slice(0, 20)
      : [],
    startedAt: cleanText(value.startedAt, 80) || nowIso(),
    updatedAt: cleanText(value.updatedAt, 80) || nowIso(),
    pausedAt: value.pausedAt ? cleanText(value.pausedAt, 80) : null,
    completedAt: value.completedAt ? cleanText(value.completedAt, 80) : null,
    timeline: sanitizeTimeline(value.timeline),
  };
}

function readSessions() {
  const storage = safeStorage();
  if (!storage) return [];
  try {
    const parsed = JSON.parse(storage.getItem(STORAGE_KEY) || '[]');
    if (!Array.isArray(parsed)) return [];
    return parsed.map(sanitizeSession).filter(Boolean);
  } catch (_) {
    return [];
  }
}

function writeSessions(sessions) {
  const storage = safeStorage();
  if (!storage) return false;
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(sessions.map(sanitizeSession).filter(Boolean)));
    return true;
  } catch (_) {
    return false;
  }
}

function setActiveSessionId(sessionId) {
  const storage = safeStorage();
  if (!storage) return;
  try {
    if (sessionId) storage.setItem(ACTIVE_KEY, sessionId);
    else storage.removeItem(ACTIVE_KEY);
  } catch (_) {}
}

export function listEngineeringSessions({ projectId } = {}) {
  const sessions = readSessions();
  return projectId ? sessions.filter((session) => session.projectId === projectId) : sessions;
}

export function getEngineeringSession(sessionId) {
  return readSessions().find((session) => session.id === sessionId) || null;
}

export function getActiveEngineeringSession() {
  const storage = safeStorage();
  if (!storage) return null;
  try {
    const id = storage.getItem(ACTIVE_KEY);
    return id ? getEngineeringSession(id) : null;
  } catch (_) {
    return null;
  }
}

export function startEngineeringSession({ projectId, projectName = '', leadPersona = 'hermes', goal = '' }) {
  if (!cleanText(projectId, 160)) throw new Error('projectId is required');

  const timestamp = nowIso();
  const session = sanitizeSession({
    id: makeId(),
    projectId,
    projectName,
    leadPersona,
    status: 'active',
    activeGoal: goal,
    startedAt: timestamp,
    updatedAt: timestamp,
    timeline: [{
      id: makeId('event'),
      type: 'session-started',
      message: goal ? `Session started with goal: ${cleanText(goal, 500)}` : 'Engineering session started',
      at: timestamp,
      actor: leadPersona,
    }],
  });

  const sessions = readSessions();
  sessions.push(session);
  writeSessions(sessions);
  setActiveSessionId(session.id);
  return session;
}

export function resumeEngineeringSession(sessionId) {
  return updateEngineeringSession(sessionId, (session) => ({
    ...session,
    status: 'active',
    pausedAt: null,
    completedAt: null,
  }), {
    type: 'session-resumed',
    message: 'Engineering session resumed',
  });
}

export function pauseEngineeringSession(sessionId) {
  const paused = updateEngineeringSession(sessionId, (session) => ({
    ...session,
    status: 'paused',
    pausedAt: nowIso(),
  }), {
    type: 'session-paused',
    message: 'Engineering session paused',
  });
  if (paused) setActiveSessionId(null);
  return paused;
}

export function completeEngineeringSession(sessionId) {
  const completed = updateEngineeringSession(sessionId, (session) => ({
    ...session,
    status: 'completed',
    completedAt: nowIso(),
  }), {
    type: 'session-completed',
    message: 'Engineering session completed',
  });
  if (completed) setActiveSessionId(null);
  return completed;
}

export function setEngineeringGoal(sessionId, goal, actor = 'user') {
  const cleanedGoal = cleanText(goal, 500);
  if (!cleanedGoal) throw new Error('goal is required');
  return updateEngineeringSession(sessionId, (session) => ({
    ...session,
    activeGoal: cleanedGoal,
  }), {
    type: 'goal-updated',
    message: `Active goal set to: ${cleanedGoal}`,
    actor,
  });
}

export function addEngineeringTimelineEntry(sessionId, { type = 'note', message, actor = 'atlas' }) {
  const cleanedMessage = cleanText(message, 500);
  if (!cleanedMessage) throw new Error('message is required');
  return updateEngineeringSession(sessionId, (session) => session, {
    type,
    message: cleanedMessage,
    actor,
  });
}

function updateEngineeringSession(sessionId, transform, timelineEntry = null) {
  const sessions = readSessions();
  const index = sessions.findIndex((session) => session.id === sessionId);
  if (index < 0) return null;

  const timestamp = nowIso();
  const current = sessions[index];
  const transformed = transform({ ...current }) || current;
  const timeline = [...current.timeline];

  if (timelineEntry) {
    timeline.push({
      id: makeId('event'),
      type: cleanText(timelineEntry.type, 80) || 'note',
      message: cleanText(timelineEntry.message, 500),
      at: timestamp,
      actor: cleanText(timelineEntry.actor, 80) || current.leadPersona || 'atlas',
    });
  }

  const updated = sanitizeSession({
    ...transformed,
    id: current.id,
    projectId: current.projectId,
    updatedAt: timestamp,
    timeline,
  });

  sessions[index] = updated;
  writeSessions(sessions);
  if (updated.status === 'active') setActiveSessionId(updated.id);
  return updated;
}

export function clearEngineeringSessions() {
  const storage = safeStorage();
  if (!storage) return;
  try {
    storage.removeItem(STORAGE_KEY);
    storage.removeItem(ACTIVE_KEY);
  } catch (_) {}
}

export { STORAGE_KEY, ACTIVE_KEY, sanitizeSession };
