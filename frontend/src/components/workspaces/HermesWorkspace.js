import React, { useEffect, useMemo, useState } from 'react';
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
} from 'lucide-react';
import { getAllProjects } from '../../data/atlasCore';
import BlueprintWorkbench from '../HUD/BlueprintWorkbench';
import './HermesWorkspace.css';

const SESSION_KEY = 'atlas.workspace.hermes.v1';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Engineering', icon: Activity },
  { id: 'projects', label: 'Projects', icon: FolderOpen },
  { id: 'blueprints', label: 'Blueprints', icon: FileCode2 },
  { id: 'notebook', label: 'Notebook', icon: BookOpen },
  { id: 'tasks', label: 'Tasks', icon: ClipboardList },
];

const DEFAULT_TASKS = [
  { id: 'review', label: 'Review active project requirements', status: 'ready' },
  { id: 'blueprint', label: 'Inspect latest blueprint revision', status: 'queued' },
  { id: 'report', label: 'Prepare engineering summary', status: 'queued' },
];

function readSession() {
  try {
    const saved = window.localStorage?.getItem(SESSION_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch (_) {
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

export default function HermesWorkspace({ open, onClose, onOpenChat, onOpenProject }) {
  const projects = useMemo(
    () => getAllProjects().filter((project) => project.ai === 'hermes'),
    [],
  );
  const saved = useMemo(readSession, []);
  const [section, setSection] = useState(saved.section || 'dashboard');
  const [activeProjectId, setActiveProjectId] = useState(saved.activeProjectId || projects[0]?.id || null);
  const [tasks, setTasks] = useState(saved.tasks || DEFAULT_TASKS);
  const [notebook, setNotebook] = useState(() => readNotebook(saved.activeProjectId || projects[0]?.id));
  const [noteStatus, setNoteStatus] = useState('saved');

  const activeProject = projects.find((project) => project.id === activeProjectId) || projects[0] || null;

  useEffect(() => {
    if (!open) return;
    try {
      window.localStorage?.setItem(SESSION_KEY, JSON.stringify({ section, activeProjectId, tasks }));
    } catch (_) {}
  }, [open, section, activeProjectId, tasks]);

  useEffect(() => {
    setNotebook(readNotebook(activeProjectId));
    setNoteStatus('saved');
  }, [activeProjectId]);

  if (!open) return null;

  const activateProject = (project) => {
    setActiveProjectId(project.id);
    setSection('dashboard');
    onOpenProject?.(project);
  };

  const completeTask = (taskId) => {
    setTasks((current) => current.map((task) => (
      task.id === taskId ? { ...task, status: task.status === 'done' ? 'ready' : 'done' } : task
    )));
  };

  const updateNotebook = (value) => {
    setNotebook(value);
    setNoteStatus('unsaved');
  };

  const saveNotebook = () => {
    try {
      window.localStorage?.setItem(notebookKey(activeProjectId), notebook);
      setNoteStatus('saved');
    } catch (_) {
      setNoteStatus('error');
    }
  };

  const renderMain = () => {
    if (section === 'projects') {
      return (
        <div className="hermes-project-grid">
          {projects.map((project) => (
            <button key={project.id} type="button" className="hermes-project-card" onClick={() => activateProject(project)}>
              <span className="hermes-kicker">{project.codename}</span>
              <strong>{project.name}</strong>
              <span>{project.phase}</span>
            </button>
          ))}
        </div>
      );
    }

    if (section === 'tasks') {
      return (
        <div className="hermes-task-list">
          {tasks.map((task) => (
            <button key={task.id} type="button" className={`hermes-task is-${task.status}`} onClick={() => completeTask(task.id)}>
              {task.status === 'done' ? <CheckCircle2 size={16} /> : <Clock3 size={16} />}
              <span>{task.label}</span>
              <small>{task.status}</small>
            </button>
          ))}
        </div>
      );
    }

    if (section === 'blueprints') {
      return (
        <section className="hermes-tool-surface" aria-label="Hermes blueprint workbench">
          <div className="hermes-tool-heading">
            <div>
              <span className="hermes-kicker">Blueprint workspace</span>
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

    return (
      <div className="hermes-dashboard-grid">
        <section className="hermes-resume-card">
          <span className="hermes-kicker">Continue project</span>
          <h2>{activeProject?.name || 'Choose a Hermes project'}</h2>
          <p>{activeProject?.codename || 'Engineering workspace ready'}</p>
          <div className="hermes-resume-actions">
            <button type="button" onClick={() => activeProject && onOpenProject?.(activeProject)}>
              <Play size={14} /> Resume
            </button>
            <button type="button" className="secondary" onClick={() => setSection('projects')}>
              Switch project
            </button>
          </div>
        </section>

        <section className="hermes-status-card">
          <span className="hermes-kicker">Hermes status</span>
          <strong>Ready</strong>
          <p>Awaiting engineering instructions.</p>
          <button type="button" onClick={onOpenChat}><MessageSquare size={14} /> Talk to Hermes</button>
        </section>

        <section className="hermes-queue-card">
          <span className="hermes-kicker">Task queue</span>
          {tasks.slice(0, 3).map((task) => (
            <div key={task.id} className={`hermes-mini-task is-${task.status}`}>
              <span>{task.label}</span><small>{task.status}</small>
            </div>
          ))}
          <button type="button" className="text-action" onClick={() => setSection('tasks')}>Open task queue</button>
        </section>

        <section className="hermes-activity-card">
          <span className="hermes-kicker">Activity</span>
          <div><time>Now</time><span>Workspace restored</span></div>
          <div><time>Ready</time><span>{activeProject?.name || 'No active project'}</span></div>
        </section>
      </div>
    );
  };

  return (
    <div className="hermes-workspace" role="dialog" aria-label="Hermes Engineering Workspace" data-testid="hermes-workspace">
      <header className="hermes-workspace-head">
        <div>
          <span className="hermes-kicker">HERMES</span>
          <h1>Engineering Workspace</h1>
        </div>
        <button type="button" className="hermes-close" onClick={onClose} aria-label="Close Hermes workspace"><X size={18} /></button>
      </header>

      <div className="hermes-workspace-body">
        <nav className="hermes-workspace-nav" aria-label="Hermes workspace sections">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
            <button key={id} type="button" className={section === id ? 'active' : ''} onClick={() => setSection(id)}>
              <Icon size={16} /><span>{label}</span>
            </button>
          ))}
        </nav>
        <main className="hermes-workspace-main">{renderMain()}</main>
      </div>

      <footer className="hermes-workspace-status">
        <span className="hermes-ready-dot" />
        <strong>Hermes ready</strong>
        <span>{activeProject?.name || 'No active project'}</span>
      </footer>
    </div>
  );
}
