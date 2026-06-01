import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ShieldCheck, Volume2, Loader2, Cpu, Hammer, Brain } from 'lucide-react';
import { Slider } from '../ui/slider';
import { useTTS } from '../../hooks/useTTS';

/**
 * InteractiveSandbox — the architect-in-chief's hands-on lab. Used by
 * the teaching engine when a topic is best learned by doing: tweak
 * sliders, watch the score & stability move, then read what each
 * mentor (Ajani · Minerva · Hermes) says about the design.
 *
 * Visuals deliberately match the HUD vocabulary:
 *   - dark glass panels, no purple gradient bg
 *   - persona-coloured borders (Ajani red, Minerva teal, Hermes silver)
 *   - tiny Orbitron labels, accent neon on metrics
 *
 * Hosted inside <TeachingWorkbench> via a "Try a hands-on lab" toggle.
 */

// --- Lab definitions ---------------------------------------------------------
const LABS = {
  power: {
    title: 'Solar Power Lab',
    mission: 'Tune a small solar station so it produces enough power without overheating.',
    icon: Cpu,
    accent: '#F03246', // Ajani — engineering domain
    lead: 'ajani',
    controls: [
      { key: 'sunlight',    label: 'Sunlight',    min: 0, max: 100, unit: '%',   default: 70 },
      { key: 'angle',       label: 'Panel Angle', min: 0, max: 90,  unit: '°',   default: 45 },
      { key: 'temperature', label: 'Temperature', min: 0, max: 120, unit: '°F',  default: 82 },
      { key: 'battery',     label: 'Battery Size',min: 1, max: 20,  unit: 'kWh', default: 8  },
    ],
    evaluate(v) {
      const angleEff = Math.max(0.2, 1 - Math.abs(v.angle - 35) / 70);
      const heat = v.temperature > 85 ? (v.temperature - 85) * 0.012 : 0;
      const output = Math.max(0, v.sunlight * angleEff * (1 - heat));
      const stability = Math.min(100, v.battery * 4 + output * 0.45 - Math.max(0, v.temperature - 90));
      const score = Math.round(output * 0.65 + stability * 0.35);
      return {
        score: Math.max(0, Math.min(100, score)),
        output: output.toFixed(1),
        stability: Math.max(0, Math.min(100, stability)).toFixed(1),
        failure: v.temperature > 100 || v.battery < 4 || output < 35,
      };
    },
  },
  bridge: {
    title: 'Bridge Failure Lab',
    mission: 'Design a basic bridge — balance strength, cost, and safety.',
    icon: Hammer,
    accent: '#F03246',
    lead: 'ajani',
    controls: [
      { key: 'supports', label: 'Support Beams',     min: 1,  max: 12,  unit: '',    default: 5   },
      { key: 'span',     label: 'River Span',        min: 50, max: 500, unit: 'ft',  default: 180 },
      { key: 'material', label: 'Material Quality',  min: 1,  max: 10,  unit: '/10', default: 6   },
      { key: 'load',     label: 'Traffic Load',      min: 1,  max: 100, unit: '%',   default: 55  },
    ],
    evaluate(v) {
      const strength = v.supports * v.material * 9;
      const stress = v.span * 0.75 + v.load * 3.2;
      const safety = Math.max(0, Math.min(100, (strength / stress) * 100));
      const costPenalty = v.supports * 2 + v.material * 3;
      const score = Math.round(safety * 0.8 - costPenalty * 0.25);
      return {
        score: Math.max(0, Math.min(100, score)),
        output: safety.toFixed(1),
        stability: Math.max(0, Math.min(100, 100 - costPenalty * 0.5)).toFixed(1),
        failure: safety < 70,
      };
    },
  },
  code: {
    title: 'Hermes Code Logic Lab',
    mission: 'Balance speed, memory, and safety in a small AI module.',
    icon: Brain,
    accent: '#E0E0EA', // Hermes silver
    lead: 'hermes',
    controls: [
      { key: 'speed',      label: 'Processing Speed', min: 1, max: 100, unit: '%', default: 65 },
      { key: 'memory',     label: 'Memory Usage',     min: 1, max: 100, unit: '%', default: 50 },
      { key: 'safety',     label: 'Safety Checks',    min: 1, max: 100, unit: '%', default: 80 },
      { key: 'complexity', label: 'Code Complexity',  min: 1, max: 100, unit: '%', default: 40 },
    ],
    evaluate(v) {
      const efficiency = v.speed * 0.5 + (100 - v.memory) * 0.25 + (100 - v.complexity) * 0.25;
      const reliability = v.safety * 0.7 + (100 - v.complexity) * 0.3;
      const score = Math.round(efficiency * 0.45 + reliability * 0.55);
      return {
        score: Math.max(0, Math.min(100, score)),
        output: efficiency.toFixed(1),
        stability: reliability.toFixed(1),
        failure: v.safety < 55 || v.complexity > 85 || v.memory > 90,
      };
    },
  },
};

const LAB_KEYS = Object.keys(LABS);

const MASTERY = ['Aware', 'Understand', 'Apply', 'Design', 'Teach'];
const rankFor = (score) =>
  score >= 90 ? 4 :
  score >= 75 ? 3 :
  score >= 55 ? 2 :
  score >= 35 ? 1 : 0;

// Mentor colours match the HUD personas (see AI_PERSONAS).
const MENTORS = [
  { id: 'ajani',   name: 'AJANI',   role: 'Strategy & Engineering', color: '#F03246', lang: 'zu' },
  { id: 'minerva', name: 'MINERVA', role: 'Reflection & Human Impact', color: '#28C8BE', lang: 'yo' },
  { id: 'hermes',  name: 'HERMES',  role: 'Code & Systems Analyst', color: '#E0E0EA', lang: 'maa' },
];

// Per-mentor feedback derived from the run state. Mirrors the ATLAS
// teaching law: failure → diagnose root cause, success → push to mastery.
function mentorMessage(mentorId, lab, result) {
  const f = result.failure;
  if (mentorId === 'ajani') {
    return f
      ? `The ${lab.title.toLowerCase()} has a weak point. Stabilise the foundation before you push power or speed. Strength before flash.`
      : 'A workable design. Now improve it without burning more resources. Good engineering is balance, not brute force.';
  }
  if (mentorId === 'minerva') {
    return f
      ? 'Ask who depends on this system. A failed grid, bridge, or program does not just break parts — it changes lives.'
      : 'This solution is becoming responsible. Now explain it in plain words — true mastery means you can teach it.';
  }
  // hermes
  return f
    ? 'Failure detected. Log the weakest variable, run the test again, compare the score delta. Data first, ego last.'
    : 'Clean run. Save this configuration, stress-test edge cases, and see if the design survives worse conditions.';
}

// Heuristic — given a teaching topic, pick the matching lab (if any).
export function pickLabForTopic(topic) {
  if (!topic) return null;
  const t = topic.toLowerCase();
  if (/(power|solar|grid|energy|battery|reactor|kinetic)/.test(t)) return 'power';
  if (/(bridge|beam|structur|architectur|load|span|construction)/.test(t)) return 'bridge';
  if (/(code|program|algorithm|software|complexity|optimi|debug)/.test(t)) return 'code';
  return null;
}

// --- Component ---------------------------------------------------------------
export default function InteractiveSandbox({ initialLabKey = 'power', topic }) {
  const [labKey, setLabKey] = useState(initialLabKey);
  const lab = LABS[labKey];

  const defaultValues = useMemo(() => {
    const v = {};
    lab.controls.forEach((c) => { v[c.key] = c.default; });
    return v;
  }, [lab]);

  const [values, setValues] = useState(defaultValues);
  const [showFailure, setShowFailure] = useState(false);
  const [speakingId, setSpeakingId] = useState(null);
  const tts = useTTS();

  useEffect(() => {
    setValues(defaultValues);
    setShowFailure(false);
  }, [defaultValues]);

  // On the frame we switch labs, `values` still holds the old lab's keys.
  // Resolve every required key with a sensible fallback so we never feed
  // NaN into the sliders or the score formula.
  const liveValues = useMemo(() => {
    const out = {};
    for (const c of lab.controls) {
      const raw = values[c.key];
      out[c.key] = Number.isFinite(raw) ? raw : c.default;
    }
    return out;
  }, [lab, values]);

  const result = lab.evaluate(liveValues);
  const rank = rankFor(result.score);
  const LabIcon = lab.icon;

  const speakAs = (mentor, text) => {
    if (speakingId) {
      tts.stop();
      if (speakingId === mentor.id) {
        setSpeakingId(null);
        return;
      }
    }
    setSpeakingId(mentor.id);
    tts.speak(text, mentor.id, {
      language: mentor.lang,
      onEnd: () => setSpeakingId(null),
    });
  };

  return (
    <div className="sandbox" data-testid="sandbox" style={{ '--lab-accent': lab.accent }}>
      {/* Header */}
      <div className="sandbox-head">
        <div className="sandbox-head-meta">
          <LabIcon size={14} style={{ color: lab.accent }} />
          <div>
            <div className="sandbox-title">{lab.title}</div>
            <div className="sandbox-mission">{lab.mission}</div>
          </div>
        </div>
        <div className="sandbox-tabs" role="tablist">
          {LAB_KEYS.map((k) => (
            <button
              key={k}
              role="tab"
              aria-selected={k === labKey}
              className={`sandbox-tab ${k === labKey ? 'active' : ''}`}
              onClick={() => setLabKey(k)}
              data-testid={`sandbox-tab-${k}`}
              style={k === labKey ? { color: LABS[k].accent, borderColor: LABS[k].accent } : undefined}
            >
              {k}
            </button>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="sandbox-controls">
        {lab.controls.map((c) => (
          <div key={c.key} className="sandbox-control">
            <div className="sandbox-control-head">
              <span>{c.label}</span>
              <span className="sandbox-control-value">
                {liveValues[c.key]}{c.unit}
              </span>
            </div>
            <Slider
              value={[liveValues[c.key]]}
              min={c.min}
              max={c.max}
              step={1}
              onValueChange={(next) => setValues((prev) => ({ ...prev, [c.key]: next[0] }))}
              data-testid={`sandbox-slider-${c.key}`}
            />
          </div>
        ))}
      </div>

      {/* Metrics row */}
      <div className="sandbox-metrics">
        <div className="sandbox-metric" data-testid="sandbox-score">
          <div className="sandbox-metric-label">Atlas Score</div>
          <div className="sandbox-metric-value" style={{ color: lab.accent }}>{result.score}</div>
        </div>
        <div className="sandbox-metric">
          <div className="sandbox-metric-label">Output / Efficiency</div>
          <div className="sandbox-metric-value">{result.output}</div>
        </div>
        <div className="sandbox-metric">
          <div className="sandbox-metric-label">Stability / Reliability</div>
          <div className="sandbox-metric-value">{result.stability}</div>
        </div>
      </div>

      {/* Mastery rank */}
      <div className="sandbox-rank">
        <div className="sandbox-rank-head">
          <div>
            <div className="sandbox-metric-label">Mastery Rank</div>
            <div className="sandbox-rank-name">{MASTERY[rank]}</div>
          </div>
          <ShieldCheck size={16} style={{ opacity: 0.75 }} />
        </div>
        <div className="sandbox-rank-bars">
          {MASTERY.map((_, i) => (
            <div
              key={i}
              className={`sandbox-rank-pip ${i <= rank ? 'filled' : ''}`}
              style={i <= rank ? { background: lab.accent } : undefined}
            />
          ))}
        </div>
      </div>

      {/* Failure vision toggle */}
      <button
        className="sandbox-failure-btn"
        onClick={() => setShowFailure((s) => !s)}
        data-testid="sandbox-failure-toggle"
        style={{ borderColor: lab.accent, color: lab.accent }}
      >
        <AlertTriangle size={12} />
        {showFailure ? 'Hide Failure Vision' : 'Show Failure Vision'}
      </button>
      {showFailure && (
        <div className="sandbox-failure" data-testid="sandbox-failure-vision">
          {result.failure
            ? 'This system is likely to fail under real pressure. Lower the risky variable, increase stability, then re-test.'
            : 'No major failure detected yet. Stress-test it — make the environment harsher and watch which number collapses first.'}
        </div>
      )}

      {/* Mentor cards */}
      <div className="sandbox-mentors">
        {MENTORS.map((m) => {
          const text = mentorMessage(m.id, lab, result);
          const speaking = speakingId === m.id;
          return (
            <div
              key={m.id}
              className="sandbox-mentor"
              style={{ borderColor: m.color }}
              data-testid={`sandbox-mentor-${m.id}`}
            >
              <div className="sandbox-mentor-head">
                <div className="sandbox-mentor-name" style={{ color: m.color }}>{m.name}</div>
                <button
                  className="sandbox-mentor-speak"
                  onClick={() => speakAs(m, text)}
                  title={speaking ? 'Stop' : `Hear ${m.name}`}
                  data-testid={`sandbox-mentor-speak-${m.id}`}
                  style={speaking ? { color: m.color, borderColor: m.color } : undefined}
                >
                  {speaking ? <Loader2 size={11} className="spin" /> : <Volume2 size={11} />}
                </button>
              </div>
              <div className="sandbox-mentor-role">{m.role}</div>
              <div className="sandbox-mentor-msg">{text}</div>
            </div>
          );
        })}
      </div>

      {topic ? (
        <div className="sandbox-footer">
          Topic-linked lab · adjust sliders to apply what {lab.lead.toUpperCase()} just taught.
        </div>
      ) : (
        <div className="sandbox-footer">More labs coming · architect can request a new one.</div>
      )}
    </div>
  );
}
