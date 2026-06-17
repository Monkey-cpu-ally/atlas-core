/**
 * Voice command parser — Phase 4.
 *
 * Turns a free-form transcript ("hey atlas open projects" or
 * "minerva let's talk") into a structured action the HUD orchestrator
 * can execute:
 *
 *   { type: 'select-ai', ai: 'minerva' }
 *   { type: 'open-section', ring: 'outer'|'middle', id: 'projects' }
 *   { type: 'noop' }
 *
 * Wake-phrase handling: when `requireWake` is true, only transcripts
 * starting with one of the recognised wake phrases are honoured; the
 * phrase is stripped before parsing the command body.
 */

const WAKE_PHRASES = [
  'hey atlas', 'hi atlas', 'okay atlas', 'ok atlas',
  'atlas core', 'atlas',
];

const AI_ALIASES = {
  ajani:   ['ajani', 'a jani', 'ageni', 'ageny'],
  minerva: ['minerva', 'minerva core', 'mineva'],
  hermes:  ['hermes', 'hermies', 'her me'],
  trinity: ['trinity', 'council', 'the council', 'tri counsel'],
};

// Maps every recognised tile id to the ring it lives on.
const TILE_ALIASES = {
  // Middle ring
  manual:        { ring: 'middle', aliases: ['manual', 'the manual', 'help'] },
  encyclopedia:  { ring: 'middle', aliases: ['encyclopedia', 'cyclopedia', 'subjects list', 'reference'] },
  memory:        { ring: 'middle', aliases: ['memory', 'memories', 'recall', 'memory bank'] },
  systems:       { ring: 'middle', aliases: ['systems', 'diagnostics', 'system status'] },
  customization: { ring: 'middle', aliases: ['customization', 'customize', 'customise', 'settings', 'configuration'] },
  // Outer ring
  subjects:      { ring: 'outer',  aliases: ['subjects', 'subject', 'learn', 'teach me', 'lesson', 'lessons'] },
  lab:           { ring: 'outer',  aliases: ['lab', 'laboratory', 'sandbox', 'hands on', 'try'] },
  projects:      { ring: 'outer',  aliases: ['projects', 'project', 'my projects'] },
  blueprints:    { ring: 'outer',  aliases: ['blueprints', 'blueprint', 'design', 'plan'] },
  archive:       { ring: 'outer',  aliases: ['archive', 'archives', 'history'] },
  explore:       { ring: 'outer',  aliases: ['explore', 'explore mode', 'intake', 'youtube', 'upload knowledge'] },
};

function _normalise(text) {
  return (text || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function _stripWake(text) {
  const t = _normalise(text);
  for (const phrase of WAKE_PHRASES) {
    if (t.startsWith(phrase + ' ')) return t.slice(phrase.length + 1).trim();
    if (t === phrase) return '';
  }
  return null;     // no wake phrase found
}

/**
 * @param {string} transcript     raw transcript
 * @param {object} opts
 * @param {boolean} opts.requireWake     if true, return noop unless transcript starts with a wake phrase
 * @returns {object}              command intent
 */
export function parseVoiceCommand(transcript, { requireWake = false } = {}) {
  if (!transcript) return { type: 'noop' };
  const stripped = _stripWake(transcript);
  let body;
  if (stripped !== null) {
    body = stripped;                     // wake phrase was present
  } else if (requireWake) {
    return { type: 'noop', reason: 'no-wake-phrase' };
  } else {
    body = _normalise(transcript);
  }
  if (!body) return { type: 'noop' };

  // 1) Persona name match
  for (const [aiKey, aliases] of Object.entries(AI_ALIASES)) {
    for (const al of aliases) {
      if (body === al || body.startsWith(al + ' ') || body.endsWith(' ' + al)) {
        return { type: 'select-ai', ai: aiKey, source: 'alias', body };
      }
    }
  }

  // 2) Tile alias match (greedy — longest wins)
  let best = null;
  for (const [tileId, info] of Object.entries(TILE_ALIASES)) {
    for (const al of info.aliases) {
      // need word boundary on at least one side
      const re = new RegExp(`(^|\\s)${al}(\\s|$)`);
      if (re.test(body)) {
        if (!best || al.length > best.matchLen) {
          best = { tileId, ring: info.ring, matchLen: al.length };
        }
      }
    }
  }
  if (best) {
    return { type: 'open-section', ring: best.ring, id: best.tileId, body };
  }

  // 3) Verb-based generic intents
  if (/(stop|cancel|close|nevermind|never mind)/.test(body)) {
    return { type: 'close-panel', body };
  }

  return { type: 'noop', reason: 'unrecognised', body };
}
