import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, ShieldCheck, Volume2, Loader2, Cpu, Hammer, Brain, Leaf, Atom, Radio } from 'lucide-react';
import { Slider } from '../ui/slider';
import { useTTS } from '../../hooks/useTTS';

/**
 * InteractiveSandbox — the architect-in-chief's hands-on lab. Used by
 * the teaching engine when a topic is best learned by doing: tweak
 * sliders, watch the score & stability move, then read what each
 * mentor (Ajani · Minerva · Hermes) says about the design.
 *
 * Each lab is tuned so that its failure modes map directly to the lead
 * core's Hard Rule — failing the design teaches the doctrine.
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

  // --- Bio-genesis (Minerva) — Living Ecosystem Lab -----------------------
  // Teaches Minerva's Hard Rule: "No irreversible harm in the name of
  // optimization." Push any species past its threshold and the whole
  // ecosystem unwinds.
  ecosystem: {
    title: 'Living Ecosystem Lab',
    mission: 'Balance predators, plants, water, climate. Push too far and life unwinds.',
    icon: Leaf,
    accent: '#28C8BE', // Minerva teal
    lead: 'minerva',
    controls: [
      { key: 'predators', label: 'Predator Density',  min: 0, max: 100, unit: '%', default: 25 },
      { key: 'plants',    label: 'Plant Coverage',    min: 0, max: 100, unit: '%', default: 60 },
      { key: 'water',     label: 'Water Cycle',       min: 0, max: 100, unit: '%', default: 65 },
      { key: 'climate',   label: 'Climate Stress',    min: 0, max: 100, unit: '%', default: 30 },
    ],
    evaluate(v) {
      // Herbivore population implied by plants vs. predation pressure.
      const herbivores = Math.max(0, v.plants * 0.7 - v.predators * 0.55);
      // Biodiversity peaks when no single dial dominates and water is healthy.
      const balance = 100 - (Math.abs(v.predators - 30) + Math.abs(v.plants - 55)) * 0.55;
      const biodiversity = Math.max(0, Math.min(100,
        balance * 0.6 + v.water * 0.35 - v.climate * 0.45 + herbivores * 0.15
      ));
      // Stability is fragile — high climate stress + low water cracks it.
      const stability = Math.max(0, Math.min(100,
        100 - v.climate * 0.65 - Math.max(0, 50 - v.water) * 1.1 - Math.max(0, v.predators - 70) * 0.9
      ));
      const score = Math.round(biodiversity * 0.55 + stability * 0.45);
      // Hard-rule failure: irreversible harm = species collapse.
      const fail =
        v.plants < 15 ||                            // habitat lost
        v.water < 20 ||                             // drought
        v.predators > 85 ||                         // over-predation
        v.climate > 80 ||                           // climate runaway
        (herbivores < 5 && v.predators > 30);       // prey extinction
      return {
        score: Math.max(0, Math.min(100, score)),
        output: biodiversity.toFixed(1),
        stability: stability.toFixed(1),
        failure: fail,
      };
    },
  },

  // --- Nano-synthesis (Hermes) — Nano-Medic Swarm Lab ---------------------
  // Teaches Hermes' Hard Rule: "Never design nanobots capable of
  // self-replication." Large uncoordinated swarms become uncontainable.
  nanoswarm: {
    title: 'Nano-Medic Swarm Lab',
    mission: 'Deploy a medical swarm into the bloodstream. Coordinate, target, contain.',
    icon: Atom,
    accent: '#E0E0EA', // Hermes silver
    lead: 'hermes',
    controls: [
      { key: 'swarmSize',    label: 'Swarm Size',         min: 10, max: 1000, unit: '',    default: 250 },
      { key: 'coordination', label: 'Coordination Proto', min: 0,  max: 100,  unit: '%',   default: 70  },
      { key: 'precision',    label: 'Target Precision',   min: 0,  max: 100,  unit: '%',   default: 75  },
      { key: 'battery',      label: 'Battery Life',       min: 5,  max: 120,  unit: 'min', default: 45  },
    ],
    evaluate(v) {
      // Effectiveness rises with swarm size BUT only if coordination keeps up.
      const coordPenalty = Math.max(0, (v.swarmSize / 100) - v.coordination / 20);
      const effectiveness = Math.max(0, Math.min(100,
        (v.swarmSize / 10) * 0.5 +
        v.precision * 0.45 -
        coordPenalty * 5
      ));
      // Containment = can you recall every bot before the battery dies?
      const containment = Math.max(0, Math.min(100,
        v.battery * 0.55 + v.coordination * 0.45 - (v.swarmSize / 14)
      ));
      const score = Math.round(effectiveness * 0.5 + containment * 0.5);
      const fail =
        (v.swarmSize > 800 && v.coordination < 70) ||  // uncontainable
        v.coordination < 40 ||                         // chaos / friendly fire
        v.precision < 40 ||                            // hits healthy tissue
        v.battery < 15;                                // strands the swarm
      return {
        score: Math.max(0, Math.min(100, score)),
        output: effectiveness.toFixed(1),
        stability: containment.toFixed(1),
        failure: fail,
      };
    },
  },

  // --- Energy harvesting (Ajani) — Resonance Energy Lab -------------------
  // Maps to Ajani's RESONANCE-ENGINE / WAVE-RIDER work. Hard Rule:
  // never an energy system you can't safely shut down.
  resonance: {
    title: 'Resonance Energy Lab',
    mission: 'Tune harvesters to ambient vibration. Over-amplify and the structure fails.',
    icon: Radio,
    accent: '#F03246', // Ajani crimson
    lead: 'ajani',
    controls: [
      { key: 'sensors',   label: 'Sensor Count',    min: 1, max: 200, unit: '',  default: 60 },
      { key: 'tuning',    label: 'Frequency Match', min: 0, max: 100, unit: '%', default: 55 },
      { key: 'amplifier', label: 'Amplifier Gain',  min: 0, max: 100, unit: '%', default: 40 },
      { key: 'damping',   label: 'Damping Buffer',  min: 0, max: 100, unit: '%', default: 50 },
    ],
    evaluate(v) {
      // Harvested wattage scales with sensors × tuning × amplifier — capped.
      const harvested = Math.max(0, Math.min(100,
        (v.sensors / 200) * 50 +
        (v.tuning / 100) * 30 +
        (v.amplifier / 100) * 25 -
        (100 - v.damping) * 0.15
      ));
      // Containment / structural integrity collapses if you over-amplify.
      const containment = Math.max(0, Math.min(100,
        100 - Math.max(0, v.amplifier - 60) * 1.6 -
        Math.max(0, v.sensors - 150) * 0.3 +
        v.damping * 0.25
      ));
      const score = Math.round(harvested * 0.55 + containment * 0.45);
      const fail =
        (v.amplifier > 85 && v.damping < 40) ||   // resonant collapse
        v.tuning < 25 ||                          // off-frequency, no yield
        harvested < 12;                           // not worth running
      return {
        score: Math.max(0, Math.min(100, score)),
        output: harvested.toFixed(1),
        stability: containment.toFixed(1),
        failure: fail,
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
  { id: 'ajani',   name: 'AJANI',   role: 'Strategy & Engineering',    color: '#F03246', lang: 'zu' },
  { id: 'minerva', name: 'MINERVA', role: 'Reflection & Human Impact', color: '#28C8BE', lang: 'yo' },
  { id: 'hermes',  name: 'HERMES',  role: 'Code & Systems Analyst',    color: '#E0E0EA', lang: 'maa' },
];

// Per-mentor feedback derived from the run state. The lead core gets a
// domain-specific message that ties failure modes to the Hard Rule.
function mentorMessage(mentorId, lab, result) {
  const f = result.failure;
  const isLead = lab.lead === mentorId;

  if (mentorId === 'ajani') {
    if (isLead && lab === LABS.power) {
      return f
        ? 'The grid will not hold under load. Drop temperature, raise battery, then nudge sunlight. Strength before flash.'
        : 'A workable station. Now improve it without burning more battery — efficient design is balance, not brute force.';
    }
    if (isLead && lab === LABS.bridge) {
      return f
        ? 'A bridge that fails has consequences a project never can. Add supports, raise material quality, then re-test.'
        : 'Solid build. Cost can still be trimmed — every beam you remove without breaking safety is one earned.';
    }
    if (isLead && lab === LABS.resonance) {
      return f
        ? 'Resonance can shatter the very structure it powers. Drop the amplifier, raise damping, tune cleanly.'
        : 'Steady harvest. Test the failure mode anyway — push amplifier high with low damping so you feel where the cliff is.';
    }
    return f
      ? `The ${lab.title.toLowerCase()} has a weak point. Stabilise the foundation before you push for more. Strength before flash.`
      : 'A workable design. Now refine it without wasting resources. Good engineering is balance, not brute force.';
  }

  if (mentorId === 'minerva') {
    if (isLead && lab === LABS.ecosystem) {
      return f
        ? 'Life does not negotiate with optimisation. Restore water, soften the climate, and let plants grow back before you adjust predators.'
        : 'The ecosystem is breathing again. Tell its story — who lives because of this balance? That is mastery.';
    }
    return f
      ? 'Ask who depends on this system. A failed grid, bridge, or program does not just break parts — it changes lives.'
      : 'This solution is becoming responsible. Now explain it in plain words — true mastery means you can teach it.';
  }

  // hermes
  if (isLead && lab === LABS.nanoswarm) {
    return f
      ? 'The swarm is past your control. Shrink it, raise coordination, sharpen precision. A nanobot you cannot recall is a weapon.'
      : 'Clean coordination. Save this configuration, stress-test it at the edges, and confirm every unit can still be recalled.';
  }
  if (isLead && lab === LABS.code) {
    return f
      ? 'Failure detected. Log the weakest variable, run the test again, compare the score delta. Data first, ego last.'
      : 'Clean run. Save this configuration, stress-test edge cases, and see if the design survives worse conditions.';
  }
  return f
    ? 'Failure detected. Log the weakest variable, run the test again, compare the score delta. Data first, ego last.'
    : 'Clean run. Save this configuration, stress-test edge cases, and see if the design survives worse conditions.';
}

// Heuristic — given a teaching topic, pick the matching lab (if any).
export function pickLabForTopic(topic) {
  if (!topic) return null;
  const t = topic.toLowerCase();
  if (/(resonance|vibration|wave[- ]?rider|kinetic[- ]harvest|harvest|rf|electromagnetic)/.test(t)) return 'resonance';
  if (/(bridge|beam|structur|architectur|span|load|construction)/.test(t)) return 'bridge';
  if (/(power|solar|grid|battery|reactor|fuel cell|hydrogen)/.test(t)) return 'power';
  if (/(ecosystem|biodivers|species|ecology|biome|permaculture|forest|wildlife|climate)/.test(t)) return 'ecosystem';
  if (/(nano|nanobot|swarm|atomic|molecul|cell repair)/.test(t)) return 'nanoswarm';
  if (/(code|program|algorithm|software|complexity|optimi|debug)/.test(t)) return 'code';
  if (/(dna|gene|regenerat|biolog|life|organism)/.test(t)) return 'ecosystem';
  if (/(energy)/.test(t)) return 'resonance';
  return null;
}

// --- Component ---------------------------------------------------------------
export default function InteractiveSandbox({ initialLabKey = 'power', topic }) {
  const safeInitial = LABS[initialLabKey] ? initialLabKey : 'power';
  const [labKey, setLabKey] = useState(safeInitial);
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
              title={LABS[k].title}
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
            ? 'This system is likely to fail under real pressure. Lower the risky variable, raise the buffer, then re-test.'
            : 'No major failure detected yet. Stress-test it — make the environment harsher and watch which number collapses first.'}
        </div>
      )}

      {/* Mentor cards */}
      <div className="sandbox-mentors">
        {MENTORS.map((m) => {
          const text = mentorMessage(m.id, lab, result);
          const speaking = speakingId === m.id;
          const isLead = lab.lead === m.id;
          return (
            <div
              key={m.id}
              className={`sandbox-mentor ${isLead ? 'lead' : ''}`}
              style={{ borderColor: m.color }}
              data-testid={`sandbox-mentor-${m.id}`}
            >
              <div className="sandbox-mentor-head">
                <div className="sandbox-mentor-name" style={{ color: m.color }}>
                  {m.name}{isLead ? ' · LEAD' : ''}
                </div>
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
        <div className="sandbox-footer">Six labs · the failure modes teach the doctrine.</div>
      )}
    </div>
  );
}
