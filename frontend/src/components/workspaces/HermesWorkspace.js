import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  X,
  FolderOpen,
  FileCode2,
  BookOpen,
  Activity,
  ClipboardList,
  MessageSquare,
  Play,
  CheckCircle2,
  Clock3,
  Save,
  Gauge,
} from 'lucide-react';
import { getAllProjects } from '../../data/atlasCore';
import BlueprintWorkbench from '../HUD/BlueprintWorkbench';
import HermesSimulationPanel from './HermesSimulationPanel';
import './HermesWorkspace.css';

const SESSION_KEY = 'atlas.workspace.hermes.v1';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Engineering', icon: Activity },
  { id: 'projects', label: 'Projects', icon: FolderOpen },
  { id: 'blueprints', label: 'Blueprints', icon: FileCode2 },
  { id: 'notebook', label: 'Notebook', icon: BookOpen },
  { id: 'simulation', label: 'Simulation', icon: Gauge },
  { id: 'tasks', label: 'Tasks', icon: ClipboardList },
];

const BRANCH_LABELS = {
  engineering: 'Engineering',
  robotics: 'Robotics',
  software: 'Software',
  manufacturing: 'Manufacturing',
  architecture: 'Architecture',
  systems: 'Systems',
};

const DEFAULT_TASKS = [
  { id: 'review', label: 'Review active project requirements', status: 'ready' },
  { id: 'blueprint', label: 'Inspect latest blueprint revision', status: 'queued' },
  { id: 'report', label: 'Prepare engineering summary', status: 'queued' },
];

const DEFAULT_ACTIVITY = [
  { id: 'workspace-ready', at: Date.now(), label: 'Workspace ready' },
];

const VALID_SECTIONS = new Set(NAV_ITEMS.map((item) => item.id));
const VALID_BRANCHES = new Set(Object.keys(BRANCH_LABELS));
const VALID_STATUSES = new Set(['ready', 'blueprinting', 'simulating', 'paused', 'noting']);

function cleanTasks(value) {
  if (!Array.isArray(value)) return DEFAULT_TASKS;
  const tasks = value
    .filter((task) => task && typeof task === 'object')
    .map((task, index) => ({
      id: typeof task.id === 'string' && task.id ? task.id : `restored-task-${index}`,
      label: typeof task.label === 'string' && task.label ? task.label : 'Recovered engineering task',
      status: task.status === 'done' ? 'done' : task.status === 'queued' ? 'queued' : 'ready',
    }));
  return tasks.length ? tasks : DEFAULT_TASKS;
}

function cleanActivity(value) {
  if (!Array.isArray(value)) return DEFAULT_ACTIVITY;
  const activity = value
    .filter((event) => event && typeof event === 'object' && typeof event.label === 'string')
    .map((event, index) => ({
      id: typeof event.id === 'string' && event.id ? event.id : `restored-event-${index}`,
      at: Number.isFinite(Number(event.at)) ? Number(event.at) : Date.now(),
      label: event.label,
    }))
    .slice(0, 12);
  return activity.length ? activity : DEFAULT_ACTIVITY;
}

function readSession() {
  try {
    const raw = window.localStorage?.getItem(SESSION_KEY);
    if (!raw) return {};

    const saved = JSON.parse(raw);
    if (!saved || typeof saved !== 'object' || Array.isArray(saved)) return {};

    return {
      section: VALID_SECTIONS.has(saved.section) ? saved.section : 'dashboard',
      focusBranch: VALID_BRANCHES.has(saved.focusBranch) ? saved.focusBranch : 'engineering',
      activeProjectId: typeof saved.activeProjectId === 'string' ? saved.activeProjectId : null,
      tasks: cleanTasks(saved.tasks),
      hermesStatus: VALID_STATUSES.has(saved.hermesStatus) ? saved.hermesStatus : 'ready',
      activity: cleanActivity(saved.activity),
    };
  } catch (_) {
    try { window.localStorage?.removeItem(SESSION_KEY); } catch (_) {}
    return {};
  }
}

function notebookKey(projectId) {
  return `atlas.workspace.hermes.notebook.${projectId || 'general'}`;
}

function readNotebook(projectId) {
  try {
    return window.localStorage?.getItem(notebookKey(projectId)) || '';
  } catch (_) {
    return '';
  }
}

function timeLabel(timestamp) {
  try {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch (_) {
    return 'Now';
  }
}

export default function HermesWorkspace({
  open,
  requestedSection,
  requestedBranch,
  requestId,
  onClose,
  onOpenChat,
  onOpenProject,
}) {
  const projects = useMemo(
    () => getAllProjects().filter((project) => project.ai === 'hermes'),
    [],
  );
  const saved = useMemo(readSession, []);
  const [section, setSection] = useState(saved.section || 'dashboard');
  const [focusBranch, setFocusBranch] = useState(saved.focusBranch || 'engineering');
  const [activeProjectId, setActiveProjectId] = useState(saved.activeProjectId || projects[0]?.id || null);
  const [tasks, setTasks] = useState(saved.tasks || DEFAULT_TASKS);
  const [notebook, setNotebook] = useState(() => readNotebook(saved.activeProjectId || projects[0]?.id));
  const [noteStatus, setNoteStatus] = useState('saved');
  const [hermesStatus, setHermesStatus] = useState(saved.hermesStatus || 'ready');
  const [activity, setActivity] = useState(saved.activity || DEFAULT_ACTIVITY);

  const activeProject = projects.find((project) => project.id === activeProjectId) || projects[0] || null;

  useEffect(() => {
    if (!open) return;
    try {
      window.localStorage?.setItem(SESSION_KEY, JSON.stringify({
        section,
        focusBranch,
        activeProjectId,
        activeProjectName: activeProject?.name || '',
        tasks,
        hermesStatus,
        activity: activity.slice(0, 12),
      }));
    } catch (_) {}
  }, [open, section, focusBranch, activeProjectId, activeProject, tasks, hermesStatus, activity]);

  useEffect(() => {
    setNotebook(readNotebook(activeProjectId));
    setNoteStatus('saved');
  }, [activeProjectId]);

  const addActivity = useCallback((label) => {
    setActivity((current) => [
      { id: `${Date.now()}-${label}`, at: Date.now(), label },
      ...current,
    ].slice(0, 12));
  }, []);

  useEffect(() => {
    if (!open || !requestedSection || !requestId) return;
    setSection(requestedSection);
    setFocusBranch(requestedBranch || 'engineering');
    setHermesStatus(requestedSection === 'blueprints' ? 'blueprinting' : 'ready');
    addActivity(`Focus branch opened: ${BRANCH_LABELS[requestedBranch] || requestedBranch || 'Engineering'}`);
  }, [open, requestedSection, requestedBranch, requestId, addActivity]);

  if (!open) return null;

  const activateProject = (project) => {
    setActiveProjectId(project.id);
    setSection('dashboard');
    addActivity(`Opened ${project.name}`);
    onOpenProject?.(project);
  };

  const completeTask = (taskId) => {
    setTasks((current) => current.map((task) => (
      task.id === taskId ? { ...task, status: task.status === 'done' ? 'ready' : 'done' } : task
    )));
    const task = tasks.find((item) => item.id === taskId);
    if (task) addActivity(`${task.status === 'done' ? 'Reopened' : 'Completed'} task: ${task.label}`);
  };

  const updateNotebook = (value) => {
    setNotebook(value);
    setNoteStatus('unsaved');
    setHermesStatus('noting');
  };

  const saveNotebook = () => {
    try {
      window.localStorage?.setItem(notebookKey(activeProjectId), notebook);
      setNoteStatus('saved');
      setHermesStatus('ready');
      addActivity('Engineering notebook saved');
    } catch (_) {
      setNoteStatus('error');
    }
  };

  const changeSection = (nextSection) => {
    setSection(nextSection);
    if (nextSection !== 'simulation') {
      setHermesStatus(nextSection === 'blueprints' ? 'blueprinting' : 'ready');
    }
    addActivity(`Opened ${NAV_ITEMS.find((item) => item.id === nextSection)?.label || nextSection}`);
  };

  const renderMain = () => {
    if (section === 'projects') {
      return (
        <div>
          <div className="hermes-branch-context">
            <span className="hermes-kicker">{BRANCH_LABELS[focusBranch] || 'Engineering'} focus</span>
            <p>Select an active Hermes project for this branch.</p>
          </div>
          <div className="hermes-project-grid">
            {projects.map((project) => (
              <button key={project.id} type="button" className="hermes-project-card" onClick={() => activateProject(project)}>
                <span className="hermes-kicker">{project.codename}</span>
                <strong>{project.name}</strong>
                <span>{project.phase}</span>
              </button>
            ))}
          </div>
        </div>
      );
    }

    if (section === 'tasks') {
      return (
        <div>
          <div className="hermes-branch-context">
            <span className="hermes-kicker">{BRANCH_LABELS[focusBranch] || 'Software'} focus</span>
            <p>Review implementation, software, and engineering tasks.</p>
          </div>
          <div className="hermes-task-list">
            {tasks.map((task) => (
              <button key={task.id} type="button" className={`hermes-task is-${task.status}`} onClick={() => completeTask(task.id)}>
                {task.status === 'done' ? <CheckCircle2 size={16} /> : <Clock3 size={16} />}
                <span>{task.label}</span>
                <small>{task.status}</small>
              </button>
            ))}
          </div>
        </div>
      );
    }

    if (section === 'blueprints') {
      return (
        <section className="hermes-tool-surface" aria-label="Hermes blueprint workbench">
          <div className="hermes-tool-heading">
            <div>
              <span className="hermes-kicker">{BRANCH_LABELS[focusBranch] || 'Architecture'} workspace</span>
              <h2>{activeProject?.name || 'No project selected'}</h2>
            </div>
          </div>
          <BlueprintWorkbench aiColor="#F4EFE4" />
        </section>
      );
    }

    if (section === 'notebook') {
      return (
        <section className="hermes-notebook" aria-label="Hermes engineering notebook">
          <div className="hermes-tool-heading">
            <div>
              <span className="hermes-kicker">Engineering notebook</span>
              <h2>{activeProject?.name || 'General notes'}</h2>
            </div>
            <button type="button" className="hermes-save-note" onClick={saveNotebook} disabled={noteStatus === 'saved'}>
              <Save size={14} /> {noteStatus === 'saved' ? 'Saved' : noteStatus === 'error' ? 'Retry save' : 'Save notes'}
            </button>
          </div>
          <textarea
            value={notebook}
            onChange={(event) => updateNotebook(event.target.value)}
            placeholder="Record design decisions, measurements, failures, fixes, and next steps..."
            spellCheck="true"
            data-testid="hermes-notebook-editor"
          />
          <div className="hermes-notebook-meta">
            <span>{notebook.length} characters</span>
            <span>{noteStatus === 'saved' ? 'Stored on this device' : 'Unsaved changes'}</span>
          </div>
        </section>
      );
    }

    if (section === 'simulation') {
      return (
        <HermesSimulationPanel
          project={activeProject}
          onStatusChange={setHermesStatus}
          onActivity={addActivity}
        />
      );
    }

    return (
      <div className="hermes-dashboard-grid">
        <section className="hermes-resume-card">
          <span className="hermes-kicker">{BRANCH_LABELS[focusBranch] || 'Engineering'} focus</span>
          <h2>{activeProject?.name || 'Choose a Hermes project'}</h2>
          <p>{activeProject?.codename || 'Engineering workspace ready'}</p>
          <div className="hermes-resume-actions">
            <button type="button" onClick={() => activeProject && onOpenProject?.(activeProject)}>
              <Play size={14} /> Resume
            </button>
            <button type="button" className="secondary" onClick={() => changeSection('projects')}>
              Switch project
            </button>
          </div>
        </section>

        <section className="hermes-status-card">
          <span className="hermes-kicker">Hermes status</span>
          <strong>{hermesStatus}</strong>
          <p>{hermesStatus === 'simulating' ? 'Tracking the active simulation workflow.' : hermesStatus === 'paused' ? 'Simulation workflow paused.' : hermesStatus === 'noting' ? 'Engineering notes have unsaved changes.' : hermesStatus === 'blueprinting' ? 'Blueprint workspace active.' : 'Awaiting engineering instructions.'}</p>
          <button type="button" onClick={onOpenChat}><MessageSquare size={14} /> Talk to Hermes</button>
        </section>

        <section className="hermes-queue-card">
          <span className="hermes-kicker">Task queue</span>
          {tasks.slice(0, 3).map((task) => (
            <div key={task.id} className={`hermes-mini-task is-${task.status}`}>
              <span>{task.label}</span><small>{task.status}</small>
            </div>
          ))}
          <button type="button" className="text-action" onClick={() => changeSection('tasks')}>Open task queue</button>
        </section>

        <section className="hermes-activity-card">
          <span className="hermes-kicker">Activity</span>
          {activity.slice(0, 4).map((event) => (
            <div key={event.id}><time>{timeLabel(event.at)}</time><span>{event.label}</span></div>
          ))}
        </section>
      </div>
    );
  };

  return (
    <div className="hermes-workspace" role="dialog" aria-label="Hermes Engineering Workspace" data-testid="hermes-workspace" data-hermes-status={hermesStatus} data-focus-branch={focusBranch}>
      <header className="hermes-workspace-head">
        <div>
          <span className="hermes-kicker">HERMES · {BRANCH_LABELS[focusBranch] || 'Engineering'}</span>
          <h1>Engineering Workspace</h1>
        </div>
        <button type="button" className="hermes-close" onClick={onClose} aria-label="Close Hermes workspace"><X size={18} /></button>
      </header>

      <div className="hermes-workspace-body">
        <nav className="hermes-workspace-nav" aria-label="Hermes workspace sections">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button key={id} type="button" className={section === id ? 'active' : ''} onClick={() => changeSection(id)}>
              <Icon size={16} /><span>{label}</span>
            </button>
          ))}
        </nav>
        <main className="hermes-workspace-main">{renderMain()}</main>
      </div>

      <footer className="hermes-workspace-status">
        <span className={`hermes-ready-dot is-${hermesStatus}`} />
        <strong>Hermes {hermesStatus}</strong>
        <span>{activeProject?.name || 'No active project'}</span>
        <span>{BRANCH_LABELS[focusBranch] || 'Engineering'}</span>
      </footer>
    </div>
  );
}
