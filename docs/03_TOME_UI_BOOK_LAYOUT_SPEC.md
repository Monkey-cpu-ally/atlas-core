# 03 — TOME UI / BOOK LAYOUT SPEC

## Document Control
- Product Surface: **Polymath Forge Tome UI**
- Status: Draft v1
- Last Updated: 2026-02-17
- Scope: Visual and interaction layout specification (no logic changes)

---

## 1. Design Intent

Style direction:
- Futuristic-minimal
- High contrast
- Clean cards and restrained depth
- Strong hierarchy
- No neon overload

The interface should feel like a modern technical codex: deliberate, quiet, and structured.

---

## 2. Primary Layout Model

### 2.1 Desktop Structure
- **Left Rail**: Projects, subjects, and quick navigation
- **Center Pane**: Active tome page (lesson/build/spec/artifact)
- **Right Rail**: Atlas panel stack (Ajani / Minerva / Hermes)
- **Bottom Strip**: Progress state, stage tracker, and validation status

### 2.2 Mobile Structure
- Collapsible rail pattern
- Center pane remains primary
- Persona outputs become tabbed sections

---

## 3. Tome Page Anatomy

Each page follows:
1. Title block
2. Metadata row (subject, level, version, status)
3. Main content body
4. Action panel (next step, tests, references)
5. Footer (history and last update)

Spacing uses an 8px rhythm baseline.

---

## 4. Typography Hierarchy

- **H1**: Page title only
- **H2**: Major section boundaries
- **H3**: Subsections
- **Body**: default reading text
- **Meta/Caption**: status, tags, timestamps

Rules:
- Avoid font-size jumps that break reading flow
- Maintain consistent line-height for dense technical content
- Max reading width should preserve scanability

---

## 5. Component Standards

### 5.1 Cards
- Uniform border radius and border weight
- Subtle elevation; no exaggerated glow
- Clear heading, body, and action zones

### 5.2 Buttons
- Primary, secondary, and ghost hierarchy
- Consistent sizing across contexts
- Distinct hover, active, and disabled states

### 5.3 Inputs
- Explicit label, helper text, and error text
- Strong focus outline for keyboard users
- High readability in dark surfaces

### 5.4 Empty States
- Informative, not decorative
- Must include:
  - what is missing
  - why it matters
  - immediate next action

---

## 6. Navigation Contract

- Navigation must be predictable and location-aware.
- Current location always visible in breadcrumbs or highlighted rail item.
- Back/forward behavior must preserve reading context.
- No hidden critical actions behind ambiguous icons.

---

## 7. Persona Panel Stack (Right Rail)

Order is fixed:
1. Ajani (structure/build framing)
2. Minerva (teaching/clarity)
3. Hermes (validation/safety)

Each panel should show:
- summary
- confidence/validation indicator
- actionable takeaway

---

## 8. Accessibility Requirements

- Keyboard navigable end-to-end
- Focus-visible states always present
- Contrast meets readability standards in all themes
- Text should remain legible at 200% zoom
- Motion effects must be minimal and non-essential

---

## 9. Visual Consistency Checklist

- [ ] 8px spacing rhythm applied consistently
- [ ] Typography hierarchy is unambiguous
- [ ] Button and card styles are standardized
- [ ] Form fields are visually and functionally consistent
- [ ] Empty states are present and actionable
- [ ] Navigation paths are clear and stable
- [ ] Focus and contrast accessibility checks pass

---

## 10. Non-Goals

- No business logic changes
- No API contract changes
- No schema changes
- No route behavior changes
