/* eslint-disable */
import React, { useMemo, useState } from 'react';
import { Clapperboard, BookOpen, Palette, Scale, RefreshCw, ShieldCheck } from 'lucide-react';

const STAGES = [
  { id: 'brief', label: 'Brief', icon: BookOpen },
  { id: 'references', label: 'References', icon: Clapperboard },
  { id: 'create', label: 'Create', icon: Palette },
  { id: 'critique', label: 'Critic Council', icon: Scale },
  { id: 'revision', label: 'Revisions', icon: RefreshCw },
  { id: 'master', label: 'Master Gate', icon: ShieldCheck },
];

/**
 * CreativeStudioPanel — HUD command surface for ATLAS Creative Intelligence.
 *
 * This first integration deliberately exposes the real production contract and
 * does not fake generation. Backend actions are enabled only as their endpoints
 * are connected. The radial HUD remains unchanged; Projects owns this workspace.
 */
export default function CreativeStudioPanel({ aiColor, project, onBack }) {
  const [stage, setStage] = useState('brief');
  const title = project?.title || project?.name || 'Untitled Creative Project';
  const summary = project?.summary || project?.description || 'Define the creative brief before production begins.';

  const stageData = useMemo(() => STAGES.find((item) => item.id === stage) || STAGES[0], [stage]);
  const StageIcon = stageData.icon;

  return (
    <div className="bp-workbench" data-testid="creative-studio-panel">
      <div className="bp-actions">
        {onBack && (
          <button className="bp-btn" onClick={onBack} data-testid="creative-studio-back">← Projects</button>
        )}
      </div>

      <h3 className="bp-title" style={{ color: aiColor }}>
        <Clapperboard size={15} /> Creative Studio
      </h3>
      <p className="bp-help">
        ATLAS production workspace. References inform craft; originality, Critic Council review,
        revisions, and production gates determine whether an asset becomes a master.
      </p>

      <div className="bp-section" data-testid="creative-project-brief">
        <div className="project-card-label">Project</div>
        <div className="project-card-title">{title}</div>
        <div className="bp-voice-body">{summary}</div>
      </div>

      <div className="bp-actions" data-testid="creative-stage-nav">
        {STAGES.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`bp-btn ${stage === id ? 'primary' : ''}`}
            onClick={() => setStage(id)}
            data-testid={`creative-stage-${id}`}
            style={stage === id ? { borderColor: aiColor, color: aiColor } : undefined}
          >
            <Icon size={12} /> {label}
          </button>
        ))}
      </div>

      <div className="bp-section" data-testid={`creative-stage-view-${stage}`}>
        <h4 style={{ color: aiColor, display: 'flex', alignItems: 'center', gap: 8 }}>
          <StageIcon size={14} /> {stageData.label}
        </h4>
        {stage === 'brief' && <p>Lock premise, audience, medium, tone, constraints, story/art bible, and intended emotional effect.</p>}
        {stage === 'references' && <p>Select curated creator/work references and the specific transferable craft principles ATLAS may study. Provenance and originality rules remain mandatory.</p>}
        {stage === 'create' && <p>Story, visual-development, shot, animation, and asset creation will execute here through connected production services. No placeholder generation is presented as finished work.</p>}
        {stage === 'critique' && <p>Minerva reviews meaning and emotional truth; Hermes reviews construction and technical execution; Ajani reviews impact, pacing, clarity, and audience experience.</p>}
        {stage === 'revision' && <p>Rejected work receives an explicit revision plan, revision history, and re-evaluation. Specialist objections cannot be averaged away.</p>}
        {stage === 'master' && <p>Final approval requires creative approval plus story, art-style, visual-quality, continuity, and originality gates. Failed gates block master status.</p>}
      </div>

      <div className="bp-section" data-testid="creative-studio-integration-status">
        <div className="project-card-label">Integration status</div>
        <div className="bp-voice-body">
          HUD workspace connected. Production actions remain locked until their backend Creative Intelligence endpoints are exposed to the frontend.
        </div>
      </div>
    </div>
  );
}
