import React, { useEffect, useState } from 'react';
import { X, ChevronRight, FileText, Code, Database, Clock, Folder, Star } from 'lucide-react';

const PANEL_CONTENT = {
  operation: {
    'Manual': {
      title: 'System Manual',
      icon: FileText,
      items: [
        { name: 'Getting Started', type: 'guide' },
        { name: 'Voice Commands', type: 'guide' },
        { name: 'Ring Navigation', type: 'guide' },
        { name: 'AI Interaction', type: 'guide' },
        { name: 'Keyboard Shortcuts', type: 'reference' }
      ]
    },
    'Encyclopedia': {
      title: 'Knowledge Base',
      icon: Database,
      items: [
        { name: 'AI Profiles', type: 'entry' },
        { name: 'System Architecture', type: 'entry' },
        { name: 'Command Reference', type: 'entry' },
        { name: 'History & Logs', type: 'entry' },
        { name: 'Terminology', type: 'reference' }
      ]
    },
    'Memory': {
      title: 'Memory Bank',
      icon: Database,
      items: [
        { name: 'Recent Sessions', type: 'memory', count: 24 },
        { name: 'Saved Contexts', type: 'memory', count: 12 },
        { name: 'Bookmarks', type: 'memory', count: 8 },
        { name: 'Pinned Items', type: 'memory', count: 5 }
      ]
    },
    'System Monitor': {
      title: 'System Status',
      icon: Code,
      stats: [
        { name: 'Core Status', value: 'Online', status: 'good' },
        { name: 'Ring Sync', value: '100%', status: 'good' },
        { name: 'Voice Engine', value: 'Active', status: 'good' },
        { name: 'Memory Usage', value: '42%', status: 'normal' },
        { name: 'AI Response', value: '23ms', status: 'good' }
      ]
    },
    'Customization': {
      title: 'Preferences',
      icon: Code,
      options: [
        { name: 'Theme', value: 'Dark Void' },
        { name: 'Animation Speed', value: 'Normal' },
        { name: 'Sound Effects', value: 'Enabled' },
        { name: 'Voice Feedback', value: 'Enabled' },
        { name: 'Haptic Response', value: 'Medium' }
      ]
    },
    'Explore Mode': {
      title: 'Exploration Hub',
      icon: Folder,
      zones: [
        { name: 'Discovery Zone', status: 'unlocked' },
        { name: 'Deep Archive', status: 'unlocked' },
        { name: 'Experimental', status: 'locked' },
        { name: 'Beta Features', status: 'locked' }
      ]
    }
  },
  knowledge: {
    'Subjects': {
      title: 'Subject Library',
      icon: Folder,
      subjects: [
        { name: 'Quantum Mechanics', progress: 78 },
        { name: 'Neural Networks', progress: 92 },
        { name: 'Bioinformatics', progress: 45 },
        { name: 'Space Science', progress: 63 },
        { name: 'Philosophy', progress: 31 }
      ]
    },
    'Lab': {
      title: 'Research Lab',
      icon: Code,
      experiments: [
        { name: 'Pattern Recognition', status: 'running' },
        { name: 'Data Synthesis', status: 'complete' },
        { name: 'Model Training', status: 'queued' },
        { name: 'Analysis Pipeline', status: 'running' }
      ]
    },
    'Projects': {
      title: 'Project Workspace',
      icon: Folder,
      projects: [
        { name: 'Project Aurora', starred: true, updated: '2h ago' },
        { name: 'Data Nexus', starred: true, updated: '5h ago' },
        { name: 'Mind Map v2', starred: false, updated: '1d ago' },
        { name: 'Archive Rebuild', starred: false, updated: '3d ago' }
      ]
    },
    'Blueprints': {
      title: 'Blueprint Gallery',
      icon: FileText,
      blueprints: [
        { name: 'System Architecture', version: '3.2' },
        { name: 'Data Flow Model', version: '2.1' },
        { name: 'Interface Layout', version: '4.0' },
        { name: 'AI Integration', version: '1.8' }
      ]
    },
    'Systems': {
      title: 'System Network',
      icon: Database,
      nodes: [
        { name: 'Core Processor', connections: 12, active: true },
        { name: 'Memory Banks', connections: 8, active: true },
        { name: 'IO Controller', connections: 6, active: true },
        { name: 'Archive Server', connections: 4, active: false }
      ]
    },
    'Archive': {
      title: 'Data Archive',
      icon: Database,
      archives: [
        { name: 'Session Logs', size: '2.4 GB', entries: 1247 },
        { name: 'Research Data', size: '8.1 GB', entries: 3891 },
        { name: 'Media Library', size: '12.7 GB', entries: 892 },
        { name: 'Backup Store', size: '45.2 GB', entries: 15420 }
      ]
    }
  }
};

export default function SidePanel({ content, activeAI, aiConfig, onClose }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (content) {
      setTimeout(() => setIsVisible(true), 50);
    } else {
      setIsVisible(false);
    }
  }, [content]);

  if (!content) return null;

  const panelData = PANEL_CONTENT[content.type]?.[content.content];
  if (!panelData) return null;

  const Icon = panelData.icon;
  const aiColor = aiConfig[activeAI].color;

  const renderContent = () => {
    if (panelData.items) {
      return (
        <div className="panel-list">
          {panelData.items.map((item, i) => (
            <button key={i} className="panel-item" data-testid={`panel-item-${i}`}>
              <FileText className="item-icon" />
              <span className="item-name">{item.name}</span>
              <span className="item-type">{item.type}</span>
              {item.count && <span className="item-count">{item.count}</span>}
              <ChevronRight className="item-arrow" />
            </button>
          ))}
        </div>
      );
    }

    if (panelData.stats) {
      return (
        <div className="panel-stats">
          {panelData.stats.map((stat, i) => (
            <div key={i} className="stat-row" data-testid={`stat-${i}`}>
              <span className="stat-name">{stat.name}</span>
              <span className={`stat-value status-${stat.status}`}>{stat.value}</span>
            </div>
          ))}
        </div>
      );
    }

    if (panelData.options) {
      return (
        <div className="panel-options">
          {panelData.options.map((option, i) => (
            <div key={i} className="option-row" data-testid={`option-${i}`}>
              <span className="option-name">{option.name}</span>
              <span className="option-value">{option.value}</span>
            </div>
          ))}
        </div>
      );
    }

    if (panelData.zones) {
      return (
        <div className="panel-zones">
          {panelData.zones.map((zone, i) => (
            <button key={i} className={`zone-card ${zone.status}`} data-testid={`zone-${i}`}>
              <Folder className="zone-icon" />
              <span className="zone-name">{zone.name}</span>
              <span className="zone-status">{zone.status}</span>
            </button>
          ))}
        </div>
      );
    }

    if (panelData.subjects) {
      return (
        <div className="panel-subjects">
          {panelData.subjects.map((subject, i) => (
            <div key={i} className="subject-row" data-testid={`subject-${i}`}>
              <span className="subject-name">{subject.name}</span>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${subject.progress}%`, background: aiColor }}
                />
              </div>
              <span className="progress-value">{subject.progress}%</span>
            </div>
          ))}
        </div>
      );
    }

    if (panelData.experiments) {
      return (
        <div className="panel-experiments">
          {panelData.experiments.map((exp, i) => (
            <div key={i} className={`experiment-row status-${exp.status}`} data-testid={`experiment-${i}`}>
              <span className={`status-dot ${exp.status}`} />
              <span className="exp-name">{exp.name}</span>
              <span className="exp-status">{exp.status}</span>
            </div>
          ))}
        </div>
      );
    }

    if (panelData.projects) {
      return (
        <div className="panel-projects">
          {panelData.projects.map((project, i) => (
            <button key={i} className="project-card" data-testid={`project-${i}`}>
              <div className="project-header">
                {project.starred && <Star className="star-icon" style={{ color: aiColor }} />}
                <span className="project-name">{project.name}</span>
              </div>
              <div className="project-meta">
                <Clock className="meta-icon" />
                <span>{project.updated}</span>
              </div>
            </button>
          ))}
        </div>
      );
    }

    if (panelData.blueprints) {
      return (
        <div className="panel-blueprints">
          {panelData.blueprints.map((bp, i) => (
            <button key={i} className="blueprint-card" data-testid={`blueprint-${i}`}>
              <FileText className="bp-icon" />
              <span className="bp-name">{bp.name}</span>
              <span className="bp-version">v{bp.version}</span>
            </button>
          ))}
        </div>
      );
    }

    if (panelData.nodes) {
      return (
        <div className="panel-nodes">
          {panelData.nodes.map((node, i) => (
            <div key={i} className={`node-card ${node.active ? 'active' : 'inactive'}`} data-testid={`node-${i}`}>
              <div className="node-status" style={{ background: node.active ? aiColor : '#666' }} />
              <span className="node-name">{node.name}</span>
              <span className="node-connections">{node.connections} connections</span>
            </div>
          ))}
        </div>
      );
    }

    if (panelData.archives) {
      return (
        <div className="panel-archives">
          {panelData.archives.map((archive, i) => (
            <div key={i} className="archive-card" data-testid={`archive-${i}`}>
              <Database className="archive-icon" />
              <div className="archive-info">
                <span className="archive-name">{archive.name}</span>
                <span className="archive-meta">{archive.size} • {archive.entries} entries</span>
              </div>
            </div>
          ))}
        </div>
      );
    }

    return null;
  };

  return (
    <div 
      className={`side-panel ${isVisible ? 'visible' : ''}`}
      style={{ '--panel-accent': aiColor }}
      data-testid="side-panel"
    >
      <div className="panel-header">
        <div className="panel-title">
          <Icon className="title-icon" style={{ color: aiColor }} />
          <h2>{panelData.title}</h2>
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
      <div className="panel-footer">
        <span className="footer-text">
          {content.type === 'operation' ? 'Ring 2 • Operations' : 'Ring 3 • Knowledge'}
        </span>
      </div>
    </div>
  );
}
