/* eslint-disable */
import React, { useEffect, useState } from 'react';
import { X, ChevronRight, AlertTriangle, Zap, Brain, User, FileCode, Beaker, Clock, Star, ArrowRight } from 'lucide-react';
import { PHASES, TEACHING_MODES, getProjectsByAI } from '../../data/atlasCore';
import BlueprintWorkbench from './BlueprintWorkbench';
import TeachingWorkbench from './TeachingWorkbench';
import DiagnosticsPanel from './DiagnosticsPanel';
import ManualPanel from './ManualPanel';
import MemoryPanel from './MemoryPanel';
import CustomizationPanel from './CustomizationPanel';
import CyclopediaPanel from './CyclopediaPanel';
import CouncilPanel from './CouncilPanel';
import IntakePanel from './IntakePanel';
import ArchiveBrowser from './ArchiveBrowser';
import ProjectsPanel from './ProjectsPanel';

export default function AtlasSidePanel({ content, activeAI, aiPersonas, onClose, onSelectProject }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (content) {
      setTimeout(() => setIsVisible(true), 50);
    } else {
      setIsVisible(false);
    }
  }, [content]);

  if (!content) return null;

  const ai = aiPersonas[activeAI];
  const aiColor = ai.color;

  const renderContent = () => {
    switch (content.type) {
      case 'ai-info':
        return renderAIInfo();
      case 'mode':
        return renderModeInfo();
      case 'field':
        return renderFieldInfo();
      case 'projects':
        return renderProjects();
      case 'project-detail':
        return renderProjectDetail();
      case 'operation':
        return renderOperationInfo();
      default:
        return null;
    }
  };

  const renderOperationInfo = () => {
    const opName = content.operation;

    // Special-case: Blueprints opens the live AI workbench (Blueprint Engine
    // + Minerva approval + Hermes validation), not a static gallery.
    if (opName === 'blueprints') {
      return <BlueprintWorkbench aiColor={aiColor} />;
    }

    // Special-case: Subjects opens the Teaching Engine workbench.
    if (opName === 'subjects') {
      return <TeachingWorkbench aiColor={aiColor} />;
    }

    // Special-case: Lab opens the Teaching Engine with the hands-on sandbox
    // pre-expanded — the architect can experiment without typing a topic first.
    if (opName === 'lab') {
      return <TeachingWorkbench aiColor={aiColor} forceSandbox={true} />;
    }

    // Special-case: Systems opens the live Diagnostics panel.
    if (opName === 'systems') {
      return <DiagnosticsPanel />;
    }

    // Middle-ring system surfaces — all live, all backend-wired.
    if (opName === 'manual')        return <ManualPanel aiColor={aiColor} />;
    if (opName === 'encyclopedia')  return <CyclopediaPanel aiColor={aiColor} />;
    if (opName === 'memory')        return <MemoryPanel aiColor={aiColor} />;
    if (opName === 'customization') return <CustomizationPanel aiColor={aiColor} />;

    // Outer-ring operations.
    if (opName === 'archive')       return <ArchiveBrowser aiColor={aiColor} />;
    if (opName === 'explore')       return <IntakePanel aiColor={aiColor} />;
    if (opName === 'projects')      return <ProjectsPanel aiColor={aiColor} />;

    // Any op that isn't routed above is, by definition, not yet wired to a
    // real backend. Per the operational rule "every visible HUD element
    // must perform a real function", we refuse to render fake content.
    return (
      <div className="panel-operation-info" data-testid="atlas-sidepanel-not-implemented">
        <div style={{
          display: 'flex', flexDirection: 'column', gap: 14,
          padding: '20px 18px',
          background: 'rgba(220, 38, 38, 0.06)',
          border: '1px solid rgba(220, 38, 38, 0.45)',
          borderRadius: 8,
        }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            color: '#F87171',
            fontFamily: 'Orbitron', fontSize: 13, letterSpacing: '0.08em',
          }}>
            <AlertTriangle size={14} />
            🔴 NOT IMPLEMENTED
          </div>
          <div style={{ fontSize: 12, color: 'var(--hud-text-dim)', lineHeight: 1.6 }}>
            Specification pending
            <br />
            Reserved for future ATLAS modules.
          </div>
          <div style={{ fontSize: 10, color: 'var(--hud-text-dim)', opacity: 0.6, letterSpacing: '0.04em' }}>
            operation: <span style={{ color: '#F87171' }}>{opName}</span>
          </div>
        </div>
      </div>
    );
  };

  const renderAIInfo = () => {
    const selectedAI = aiPersonas[content.ai];
    const projects = getProjectsByAI(content.ai);
    
    return (
      <div className="panel-ai-info">
        <div className="ai-header" style={{ borderColor: selectedAI.color }}>
          <div className="ai-avatar" style={{ background: `${selectedAI.color}30`, borderColor: selectedAI.color }}>
            {content.ai === 'ajani' && <User style={{ color: selectedAI.color }} />}
            {content.ai === 'minerva' && <Brain style={{ color: selectedAI.color }} />}
            {content.ai === 'hermes' && <Zap style={{ color: selectedAI.color }} />}
            {content.ai === 'trinity' && <span style={{ color: selectedAI.color }}>⚡</span>}
          </div>
          <div className="ai-meta">
            <h3 style={{ color: selectedAI.color }}>{selectedAI.name}</h3>
            <p className="ai-role">{selectedAI.title}</p>
          </div>
        </div>
        
        <div className="info-section">
          <label>Domain</label>
          <p className="domain-value">{selectedAI.domain}</p>
        </div>
        
        <div className="info-section belief">
          <label>Core Belief</label>
          <p>"{selectedAI.coreBelief}"</p>
        </div>
        
        <div className="info-section hard-rule">
          <label><AlertTriangle className="inline w-4 h-4 mr-1" />Hard Rule</label>
          <p>{selectedAI.hardRule}</p>
        </div>

        {content.ai !== 'trinity' && (
          <div className="info-section projects-summary">
            <label>Projects ({projects.length})</label>
            <div className="phase-breakdown">
              {Object.entries(PHASES).map(([phase, data]) => {
                const count = projects.filter(p => p.phase === phase).length;
                if (count === 0) return null;
                return (
                  <div key={phase} className="phase-item">
                    <span className="phase-dot" style={{ background: data.color }} />
                    <span className="phase-name">{phase}</span>
                    <span className="phase-count">{count}</span>
                  </div>
                );
              })}
            </div>
            <button 
              className="view-projects-btn"
              onClick={() => onSelectProject && onSelectProject({ type: 'projects', ai: content.ai })}
              style={{ borderColor: selectedAI.color, color: selectedAI.color }}
            >
              View All Projects <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {content.ai === 'trinity' && (
          <div className="trinity-note">
            <p>{selectedAI.description}</p>
            <CouncilPanel aiColor={selectedAI.color} />
          </div>
        )}
      </div>
    );
  };

  const renderModeInfo = () => {
    const mode = TEACHING_MODES.find(m => m.id === content.mode);
    if (!mode) return null;

    return (
      <div className="panel-mode-info">
        <div className="mode-header">
          <h3>{mode.name}</h3>
          <p>{mode.description}</p>
        </div>

        <div className="capabilities-section">
          <label>Capabilities in {mode.name}</label>
          <ul className="capabilities-list">
            <li>Text responses</li>
            <li>Voice interaction</li>
            <li>Visual diagrams</li>
            <li>Simulations</li>
            <li>Code generation</li>
            <li>Blueprint breakdowns</li>
          </ul>
        </div>

        <div className="learning-style">
          <label>Learning Approach</label>
          <div className="style-tags">
            <span className="tag">ADHD-aware</span>
            <span className="tag">Visual-first</span>
            <span className="tag">Mastery-gated</span>
            <span className="tag">No grades</span>
          </div>
        </div>

        <div className="mode-cta">
          <p>Select a field from Ring 3 to begin learning in {mode.name}.</p>
        </div>
      </div>
    );
  };

  const renderFieldInfo = () => {
    const field = content.field;
    if (!field) return null;

    return (
      <div className="panel-field-info">
        <div className="field-header">
          <h3>{field.name}</h3>
          <span className="field-category">{field.category}</span>
        </div>

        <div className="teachers-section">
          <label>Taught by All Three</label>
          <div className="teacher-avatars">
            <div className="teacher" style={{ borderColor: aiPersonas.ajani.color }}>
              <User className="w-4 h-4" style={{ color: aiPersonas.ajani.color }} />
            </div>
            <div className="teacher" style={{ borderColor: aiPersonas.minerva.color }}>
              <Brain className="w-4 h-4" style={{ color: aiPersonas.minerva.color }} />
            </div>
            <div className="teacher" style={{ borderColor: aiPersonas.hermes.color }}>
              <Zap className="w-4 h-4" style={{ color: aiPersonas.hermes.color }} />
            </div>
          </div>
        </div>

        <div className="related-projects">
          <label>Related Projects</label>
          <p className="hint">Projects from all AIs that relate to {field.name}</p>
        </div>

        <div className="start-learning">
          <button className="start-btn" style={{ background: aiColor }}>
            Start Learning {field.name}
          </button>
        </div>
      </div>
    );
  };

  const renderProjects = () => {
    const projects = getProjectsByAI(content.ai || activeAI);

    return (
      <div className="panel-projects">
        <div className="projects-header">
          <h3>{content.ai === 'trinity' ? 'All Projects' : `${aiPersonas[content.ai]?.name || ai.name}'s Projects`}</h3>
          <span className="project-count">{projects.length} projects</span>
        </div>

        <div className="projects-list">
          {projects.map((project, index) => {
            const phase = PHASES[project.phase];
            const projectAI = aiPersonas[project.ai];
            
            return (
              <button 
                key={project.id}
                className="project-card"
                onClick={() => onSelectProject && onSelectProject(project)}
                data-testid={`project-${project.id}`}
              >
                <div className="project-header">
                  <span className="project-codename" style={{ color: projectAI?.color || aiColor }}>
                    {project.codename}
                  </span>
                  <span 
                    className="project-phase"
                    style={{ background: phase?.color + '30', color: phase?.color }}
                  >
                    {project.phase}
                  </span>
                </div>
                <div className="project-name">{project.name}</div>
                <div className="project-progress">
                  <div 
                    className="progress-bar"
                    style={{ width: `${phase?.progress || 0}%`, background: phase?.color }}
                  />
                </div>
                <ChevronRight className="project-arrow" />
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  const renderProjectDetail = () => {
    const project = content.project;
    if (!project) return null;
    
    const phase = PHASES[project.phase];
    const projectAI = aiPersonas[project.ai];

    return (
      <div className="panel-project-detail">
        <div className="project-detail-header">
          <div className="codename-badge" style={{ background: projectAI?.color + '20', borderColor: projectAI?.color }}>
            {project.codename}
          </div>
          <h3>{project.name}</h3>
        </div>

        <div className="project-meta">
          <div className="meta-item">
            <label>Lead</label>
            <span style={{ color: projectAI?.color }}>{projectAI?.name}</span>
          </div>
          <div className="meta-item">
            <label>Domain</label>
            <span>{projectAI?.domain}</span>
          </div>
        </div>

        <div className="phase-indicator">
          <label>Phase</label>
          <div className="phase-display">
            <span 
              className="phase-badge"
              style={{ background: phase?.color + '30', color: phase?.color }}
            >
              {project.phase}
            </span>
            <span className="phase-desc">{phase?.description}</span>
          </div>
          <div className="phase-progress-bar">
            <div 
              className="phase-fill"
              style={{ width: `${phase?.progress || 0}%`, background: phase?.color }}
            />
          </div>
          <div className="phase-steps">
            {Object.entries(PHASES).map(([name, data]) => (
              <span 
                key={name}
                className={`step ${data.order <= (phase?.order || 0) ? 'complete' : ''}`}
                style={{ color: data.order <= (phase?.order || 0) ? data.color : 'rgba(255,255,255,0.3)' }}
              >
                {name.charAt(0)}
              </span>
            ))}
          </div>
        </div>

        <div className="project-description">
          <label>Description</label>
          <p>{project.description}</p>
        </div>

        <div className="project-actions">
          <button className="action-btn" style={{ borderColor: projectAI?.color }}>
            <Beaker className="w-4 h-4" /> View Research
          </button>
          <button className="action-btn" style={{ borderColor: projectAI?.color }}>
            <FileCode className="w-4 h-4" /> Blueprints
          </button>
        </div>
      </div>
    );
  };

  const getTitle = () => {
    switch (content.type) {
      case 'ai-info':
        return aiPersonas[content.ai]?.name || 'AI Profile';
      case 'mode':
        return TEACHING_MODES.find(m => m.id === content.mode)?.name || 'Mode';
      case 'field':
        return content.field?.name || 'Field';
      case 'projects':
        return 'Projects';
      case 'project-detail':
        return content.project?.codename || 'Project';
      case 'operation':
        return content.operation || 'Operation';
      default:
        return 'Panel';
    }
  };

  return (
    <div 
      className={`side-panel atlas-panel ${isVisible ? 'visible' : ''}`}
      style={{ '--panel-accent': aiColor }}
      data-testid="side-panel"
    >
      <div className="panel-header">
        <div className="panel-title">
          <h2>{getTitle()}</h2>
        </div>
        <button 
          className="close-btn"
          onClick={onClose}
          data-testid="panel-close-btn"
          aria-label="Close panel"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      <div className="panel-content">
        {renderContent()}
      </div>
    </div>
  );
}
