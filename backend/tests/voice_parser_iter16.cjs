// Iteration 16 — Voice command parser unit tests
// Tests Ingest-URL detection + regression on existing intents.

const path = require('path');
const Module = require('module');

// The parser is an ESM file. Use a minimal shim: copy the regex/logic at top is
// not needed — we transpile by reading + evaluating, replacing `export function`.
const fs = require('fs');
const SRC = fs.readFileSync('/app/frontend/src/utils/voiceCommands.js', 'utf8');
const transformed = SRC.replace('export function parseVoiceCommand', 'function parseVoiceCommand') +
  '\nmodule.exports = { parseVoiceCommand };';

const tmp = '/tmp/voiceCommands.cjs';
fs.writeFileSync(tmp, transformed);
const { parseVoiceCommand } = require(tmp);

let passed = 0, failed = 0;
function t(name, fn) {
  try { fn(); console.log(`PASS ${name}`); passed++; }
  catch (e) { console.log(`FAIL ${name}\n      ${e.message}`); failed++; }
}
function eq(a, b, msg) {
  const ja = JSON.stringify(a), jb = JSON.stringify(b);
  if (ja !== jb) throw new Error(`${msg || ''} expected ${jb}, got ${ja}`);
}

// 1. Plain ingest with full URL
t('ingest https URL', () => {
  const r = parseVoiceCommand('ingest https://github.com/openai/whisper');
  eq(r.type, 'ingest-url');
  eq(r.url, 'https://github.com/openai/whisper');
  eq(r.source, 'voice');
});

// 2. Works with wake phrase
t('hey atlas ingest URL', () => {
  const r = parseVoiceCommand('hey atlas ingest https://github.com/openai/whisper');
  eq(r.type, 'ingest-url');
  eq(r.url, 'https://github.com/openai/whisper');
});

// 3. Scheme-less URL: github.com/openai/whisper → promoted to https://
t('ingest scheme-less github URL', () => {
  const r = parseVoiceCommand('ingest github.com/openai/whisper');
  eq(r.type, 'ingest-url');
  eq(r.url, 'https://github.com/openai/whisper');
});

// 4. www. prefix → promoted to https://www.
t('ingest www.example.com', () => {
  const r = parseVoiceCommand('ingest www.example.com');
  eq(r.type, 'ingest-url');
  eq(r.url, 'https://www.example.com');
});

// 5. Trailing punctuation stripped
t('ingest URL with trailing period', () => {
  const r = parseVoiceCommand('ingest https://github.com/openai/whisper.');
  eq(r.type, 'ingest-url');
  eq(r.url, 'https://github.com/openai/whisper');
});

// 6. Existing intent regression — open projects
t('open projects (no wake)', () => {
  const r = parseVoiceCommand('open projects');
  eq(r.type, 'open-section');
  eq(r.id, 'projects');
  eq(r.ring, 'outer');
});

// 7. Persona alias regression — minerva
t('persona alias minerva', () => {
  const r = parseVoiceCommand('minerva');
  eq(r.type, 'select-ai');
  eq(r.ai, 'minerva');
});

// 8. Wake phrase + tile alias regression
t('hey atlas show memory bank', () => {
  const r = parseVoiceCommand('hey atlas memory bank');
  eq(r.type, 'open-section');
  eq(r.id, 'memory');
});

// 9. requireWake with no wake → noop
t('requireWake without wake → noop', () => {
  const r = parseVoiceCommand('open projects', { requireWake: true });
  eq(r.type, 'noop');
});

// 10. requireWake honored for ingest (ingest works irrespective of wake)
t('ingest works without wake even with requireWake=true', () => {
  const r = parseVoiceCommand('ingest https://example.com', { requireWake: true });
  eq(r.type, 'ingest-url');
});

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
