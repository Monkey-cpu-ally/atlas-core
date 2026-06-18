# ATLAS V2 · Self-Improvement Report

> **2026-06-18 · Parts 2 + 3 + 5 of ATLAS V2 build.**
> Live test executed against `/app/backend` source tree.

---

## Part 2 · Self-Code Improvement System

### What was built
| Component | File | Purpose |
| --------- | ---- | ------- |
| Scanner | `services/self_code.py` (180 LOC) | AST + regex heuristics, produces proposals through existing self-improvement layer |
| Routes (4) | `routes/atlas_v2.py` (self-code section) | proposals · scan · approve · reject |

### Endpoints
```
GET   /api/self-code/proposals        → scanner-sourced proposals (filter: status, limit)
POST  /api/self-code/scan             → walk /app/backend + scan AtlasSidePanel.js, emit proposals
POST  /api/self-code/approve/{id}     → mark approved (no auto-apply)
POST  /api/self-code/reject/{id}      → mark rejected
```

### Detectors implemented (and what each is honest about)
| Detector | Honest about |
| -------- | ------------ |
| `TODO/FIXME/XXX/HACK` comment scan | regex only — catches the literal markers, nothing more |
| Bare `except: pass` (AST-based) | catches the most-common silent-failure pattern; **misses** `except Exception: ...` blocks that swallow into a logger but don't re-raise |
| Hardcoded HUD legacy lists (AtlasSidePanel.js) | direct regex against the known `Connected Devices` / `Blueprint Gallery` literals |
| Module size > LINE_BUDGET (550) | line count only — no cyclomatic complexity, no churn weighting |
| Missing test for `routes/*.py` | filename heuristic only — won't catch tests that exist with non-conventional names |

### Live test run

```
POST /api/self-code/scan
{
  "scan_root":         "/app/backend",
  "files_scanned":     63,
  "findings_total":    29,
  "proposals_created": 27       ← 2 deduped against pre-existing proposals
}
```

**Sample proposals (recent 5, scanner-sourced):**
```
- code_architecture · low  · routes/memory.py        — no matching test_memory*.py
- code_architecture · low  · routes/learning.py      — no matching test_learning*.py
- code_architecture · low  · routes/hud_surfaces.py  — no matching test_hud_surfaces*.py
- code_architecture · low  · routes/files.py         — no matching test_files*.py
- code_architecture · low  · routes/self_improve.py  — no matching test_self_improve*.py
```

All 27 proposals are sitting `status=pending` per the strict "approval-first"
rule. Even the auto-flagged `code_architecture` ones with `risk_level=high`
do NOT get auto-applied — they are queued for human review.

### What is REAL
- AST walk really executes (verified by line-number column in evidence)
- Findings are deduped against pre-existing proposals (no duplicate floods on re-scan)
- High-risk proposals are correctly forced to `approval_required=true` by the underlying `self_improvement.propose` gating

### What is SIMULATED
- "messy architecture" detector is only a line-count proxy
- `confidence_score` is hand-coded per detector, not learned
- No actual diff/patch generation yet — proposals describe the change in prose only

### What needs user approval
- Every `risk_level: medium|high` proposal · or any `category: code_architecture|agent_personality` proposal — both gates baked into `services/self_improvement.propose`
- Among the 27 fresh proposals, **0 are HUD-layout** (AtlasSidePanel hardcoded-list detector also flagged but de-duped against the earlier session's proposal)
- Among the 27 fresh proposals, **6 are `code_architecture` requiring approval**

### What is NOT in this build
- ❌ No diff/patch generation — the scanner describes the change in prose only
- ❌ No automatic test execution before/after a proposed change
- ❌ No git-blame churn weighting (some files may be 600 lines and stable)
- ❌ No package outdatedness check (would need `pip list --outdated` integration)
- ❌ No broken-import detection beyond Python's own `ast.parse` raising

---

## Part 3 · Personal Learning Adaptation

### What was built
| Component | File | Purpose |
| --------- | ---- | ------- |
| Service | `services/adaptation.py` (≈180 LOC) | Single-doc `user_learning_profile` keyed `id="default"` |
| Routes (4) | `routes/atlas_v2.py` (learning section) | profile read/update · log-confusion · log-success |

### Endpoints
```
GET   /api/learning/profile             → current learning profile (creates default if absent)
POST  /api/learning/profile             → patch fields (whitelist-validated)
POST  /api/learning/log-confusion       → record a topic the user keeps re-asking
POST  /api/learning/log-success         → record a lesson pattern that worked
```

### Default profile (auto-created on first read)
```json
{
  "id": "default",
  "preferred_explanation_level": "6-9grade",
  "hands_on_examples": true,
  "preferred_lesson_format": "lego_steps",
  "preferred_visual_style": "futuristic-holographic",
  "explanation_rules": [
    "Explain hard topics at 6th-9th grade level first",
    "Then give the deeper advanced explanation",
    "Use hands-on Lego-style steps",
    "Include wrong/right examples",
    "Include mini quizzes",
    "Connect lessons to ATLAS projects"
  ],
  "favorite_project_types": [],
  "confusing_topics": [],
  "successful_lesson_patterns": [],
  "repeated_questions": [],
  "coding_mistakes": []
}
```

### Live test run
```
POST /api/learning/log-confusion {topic:"IDA* heuristic admissibility", weight:2}
→ confusing_topics: [{topic:"IDA* heuristic admissibility", count:2, last_seen:"2026-06-18T14:47:43Z"}]

POST /api/learning/log-success {lesson_id:"e3b15139...", pattern:"hands-on PDB project worked"}
→ successful_lesson_patterns last entry: {lesson_id:"e3b15139...", pattern:"hands-on PDB project worked", ts:"…"}
```

### What is REAL
- Profile read/write round-trip persisted in Mongo
- Whitelist patching (unknown fields silently dropped — no schema attacks)
- Confusion counter is a real running tally (idempotent topic merge)

### What is SIMULATED
- Lesson generator does NOT YET read the learning profile to bias its output. The profile is collected but not yet consumed. **This is the integration gap.**
- No auto-detection of "repeated question" from chat history — must be logged explicitly via `/log-confusion`

### What needs user approval
Nothing in Part 3 needs approval — all changes are user-supplied.

---

## Part 5 · Visual Style Memory

### What was built
| Component | File | Purpose |
| --------- | ---- | ------- |
| Service | `services/adaptation.py` (style section) | Single-doc `visual_style_memory` keyed `id="default"` |
| Routes (4) | `routes/atlas_v2.py` (style section) | preferences read/update · note · warning |

### Endpoints
```
GET   /api/style/preferences            → current visual style memory
POST  /api/style/preferences            → patch (whitelist-validated)
POST  /api/style/note                   → append a reference-image note
POST  /api/style/warning                → increment too_plain or too_messy
```

### Default style memory
```json
{
  "preferred_themes": ["atlas_hud_v2"],
  "rejected_themes": [],
  "color_preferences": {
    "ajani":   "#E63946",
    "minerva": "#2EC4B6",
    "hermes":  "#F4EFE4",
    "council": "#9B6BD8"
  },
  "layout_preferences": {
    "density": "spacious",
    "ring_motion": "slow_with_snap_back",
    "panel_position": "right_dock"
  },
  "animation_preferences": {
    "snap_back": true,
    "breathing": true,
    "ring_idle_drift_seconds": 24
  },
  "reference_image_notes": [],
  "too_plain_warnings": 0,
  "too_messy_warnings": 0
}
```

### Live test run
```
POST /api/style/warning {kind:"too_plain"}
→ too_plain_warnings: 1   (real Mongo $inc)
```

### What is REAL
- Persistence + warning counter increment
- Theme file lookup via `/api/themes/list` returns the 4 JSON files on disk
- Agent color tokens match `atlas_hud_v2.theme.json` (single source of truth)

### What is SIMULATED
- No closed-loop yet: increment of `too_plain_warnings` doesn't yet change anything in the HUD render
- "Rejected themes" list is read-only at runtime — no auto-rejection logic exists

### What needs user approval
Nothing in Part 5 needs approval — preferences are user-driven.

---

## Cross-part summary

| Part | Endpoints live | DB collection | Verified by curl in this run |
| ---: | -------------: | ------------- | ---------------------------- |
| 2 (self-code) | 4 | re-uses `self_improvements` | ✅ 27 new proposals created |
| 3 (learning) | 4 | `user_learning_profile` | ✅ confusion + success logged |
| 5 (style) | 4 | `visual_style_memory` | ✅ warning counter incremented |

---

_Sister documents: `ATLAS_WORLDWATCH_REPORT.md` (Part 1) ·
`ATLAS_HUD_V2_STYLE_GUIDE.md` (Part 4)._
