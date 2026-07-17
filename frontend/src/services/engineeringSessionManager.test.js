import {
  addEngineeringTimelineEntry,
  clearEngineeringSessions,
  completeEngineeringSession,
  getActiveEngineeringSession,
  getEngineeringSession,
  listEngineeringSessions,
  pauseEngineeringSession,
  resumeEngineeringSession,
  setEngineeringGoal,
  startEngineeringSession,
} from './engineeringSessionManager';

describe('engineeringSessionManager', () => {
  beforeEach(() => {
    clearEngineeringSessions();
  });

  test('creates and restores an active engineering session', () => {
    const created = startEngineeringSession({
      projectId: 'power-cell',
      projectName: 'Power Cell',
      leadPersona: 'hermes',
      goal: 'Reduce weight without reducing capacity',
    });

    expect(created.status).toBe('active');
    expect(created.activeGoal).toBe('Reduce weight without reducing capacity');
    expect(getActiveEngineeringSession().id).toBe(created.id);
    expect(getEngineeringSession(created.id).projectId).toBe('power-cell');
  });

  test('pauses and resumes without losing the goal or timeline', () => {
    const created = startEngineeringSession({ projectId: 'weaver', goal: 'Improve arm precision' });
    const paused = pauseEngineeringSession(created.id);

    expect(paused.status).toBe('paused');
    expect(getActiveEngineeringSession()).toBeNull();

    const resumed = resumeEngineeringSession(created.id);
    expect(resumed.status).toBe('active');
    expect(resumed.activeGoal).toBe('Improve arm precision');
    expect(resumed.timeline.map((entry) => entry.type)).toEqual(
      expect.arrayContaining(['session-started', 'session-paused', 'session-resumed']),
    );
  });

  test('updates the active goal and records engineering activity', () => {
    const created = startEngineeringSession({ projectId: 'green-bots' });
    setEngineeringGoal(created.id, 'Improve soil repair coverage', 'user');
    const updated = addEngineeringTimelineEntry(created.id, {
      type: 'research-requested',
      message: 'Compare root-inspired locomotion systems',
      actor: 'minerva',
    });

    expect(updated.activeGoal).toBe('Improve soil repair coverage');
    expect(updated.timeline.at(-1)).toMatchObject({
      type: 'research-requested',
      actor: 'minerva',
    });
  });

  test('completes a session and filters project history', () => {
    const first = startEngineeringSession({ projectId: 'power-cell' });
    completeEngineeringSession(first.id);
    startEngineeringSession({ projectId: 'weaver' });

    expect(listEngineeringSessions()).toHaveLength(2);
    expect(listEngineeringSessions({ projectId: 'power-cell' })).toHaveLength(1);
    expect(getEngineeringSession(first.id).status).toBe('completed');
  });

  test('rejects sessions without a project id', () => {
    expect(() => startEngineeringSession({ projectId: '' })).toThrow('projectId is required');
  });
});
