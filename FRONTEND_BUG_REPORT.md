# Frontend Bug Report — Atlas Core

A systematic audit of all files in `atlas_core_new/static/` and `atlas_core_new/static/viewer/`.

---

## Critical Bugs (Will cause runtime errors or completely broken features)

### 1. Broken DOM references in `showLessonStep()` — `index.html` ~line 2583–2600

The LEGO-lesson viewer (`openLesson` → `showLessonStep`) references three DOM element IDs that **do not exist** anywhere in the HTML:

| JS reference (line)                            | Expected ID        | Actual ID in HTML          |
|------------------------------------------------|--------------------|----------------------------|
| `document.getElementById('lessonTitle')` (2583)  | `lessonTitle`      | `lessonViewerTitle` (1362) |
| `document.getElementById('lessonContent')` (2585)| `lessonContent`    | `lessonText` (1385)        |
| `document.getElementById('lessonNextBtn')` (2600)| `lessonNextBtn`    | `nextChapterBtn` (1452)    |

**Impact:** Clicking any LEGO-style lesson throws `TypeError: Cannot set properties of null`. The entire old lesson viewer is non-functional. Setting `.textContent` or `.innerHTML` on `null` crashes `showLessonStep()`.

---

### 2. Broken DOM references for voice toggle — `index.html` ~lines 2474, 2480, 2500

The `toggleVoice()` speech recognition handlers reference:

- `document.getElementById('voiceBtn')` — **No element with `id="voiceBtn"` exists.**
- `document.getElementById('voiceIcon')` — **No element with `id="voiceIcon"` exists.**

The voice button in the chat input area at line 108 is:
```html
<button class="hex-icon hex-green" onclick="toggleVoice()" title="Voice Input">🎤</button>
```
It has no `id` attribute.

**Impact:** When voice recognition starts/stops/errors, attempts to add/remove the `listening` class or change the icon text hit `null`, producing console errors. The visual feedback for voice recording state is completely broken.

---

### 3. `showNotification()` function overridden — triple definition — `index.html` lines 5050, 5328, 5570

Three `function showNotification(...)` declarations exist in the same `<script>` scope:

| Line | Signature | Purpose |
|------|-----------|---------|
| 5050 | `(message, type = 'info')` | Console-only stub |
| 5328 | `(message, type = 'info')` | Creates in-page visual toast |
| 5570 | `(title, body, icon = null)` | Creates browser `Notification` |

Due to JavaScript function hoisting, **the last declaration (line 5570) wins**. All call sites using the `(message, type)` pattern (e.g., `showNotification('Lesson Complete!', 'success')`) invoke the browser notification version instead.

Since the browser notification version first checks `if (!notificationsEnabled || Notification.permission !== 'granted') return;`, and most users haven't granted notification permission, **all ~40+ in-page notification calls silently do nothing**. Users never see toast feedback for actions like "Lesson Complete!", "Notifications Enabled", "Project saved!", etc.

---

### 4. `updateSystemMetrics()` signature mismatch — `index.html` lines 1658 vs 15797

`ForgeEngine.syncToUI()` (line 1658) calls:
```js
updateSystemMetrics(m.stability, m.memoryLoad, m.logicFlow, m.riskLevel);
```
passing **4 positional number arguments**.

But `updateSystemMetrics` (line 15797) expects:
```js
function updateSystemMetrics(data = {}) {
    const stability = data.stability || ...;
    const memory = data.memory || ...;
    const logic = data.logic || ...;
    const risk = data.risk || ...;
}
```
a **single object** with properties `stability`, `memory`, `logic`, `risk`.

**Impact:** The first number argument becomes `data`. Then `data.stability` (a property on a Number) is `undefined`, and all metrics fall back to random values. The system status pane never reflects actual ForgeEngine state.

---

## Moderate Bugs (Broken features, non-functional code paths)

### 5. `switchPersona` hook never activates — `index.html` ~line 16762

```js
const originalSwitchPersona = window.switchPersona;
if (typeof originalSwitchPersona === 'function') {
    window.switchPersona = function(persona) { ... };
}
```

`window.switchPersona` is **never defined**. The actual persona-switching function used throughout the app is `selectPersona()` (line 1882). The condition is always `false`, so `updateAIPresence()` is never called.

**Impact:** The AI presence indicators in the system status pane (`#aiAjani`, `#aiMinerva`, `#aiHermes`) never update when the user switches personas. The `addSystemLog()` calls like "TACTICAL MODE ENGAGED" never fire.

---

### 6. Missing `static/images/` directory — referenced by multiple files

The directory `atlas_core_new/static/images/` does not exist. **No image files are present.** Yet many files reference images from this path:

| File | References |
|------|-----------|
| `manifest.json` | `/static/images/icon-192.png`, `/static/images/icon-512.png` |
| `index.html` (head) | `/static/images/icon-192.png`, `/static/images/icon-512.png` |
| `sw.js` (STATIC_ASSETS) | `/static/images/ajani_bg.png`, `/static/images/counsel_bg.png`, `/static/images/icon-192.png`, `/static/images/icon-512.png` |
| `sw.js` (push handler) | `/static/images/icon-192.png`, `/static/images/icon-72.png` |
| `index.html` (notification) | `/static/icons/icon-72x72.png`, `/static/icons/icon-192x192.png` |

**Impact:**
- PWA install will show broken/missing icons
- Service worker `install` event may fail when caching static assets (though code filters out `icon-` URLs)
- Push notifications will have missing icons
- `apple-touch-icon` and favicon are broken

---

### 7. Inconsistent notification icon paths — `index.html` vs `sw.js`

Two different notification icon path schemas are used:

| Source | Icon path |
|--------|-----------|
| `index.html` line 5575 | `/static/icons/icon-192x192.png` |
| `index.html` line 5576 | `/static/icons/icon-72x72.png` |
| `sw.js` line 144 | `/static/images/icon-192.png` |
| `sw.js` line 145 | `/static/images/icon-72.png` |

The `index.html` uses `/static/icons/` while `sw.js` uses `/static/images/`. Neither directory exists. Even if images were added, these inconsistent paths mean at least one set of notifications would have broken icons.

---

### 8. Missing download file — `download.html` line 22

```html
<a class="btn btn-primary" href="/static/atlas_core_source.tar.gz" download>Download .tar.gz (604 KB)</a>
```

The file `atlas_core_new/static/atlas_core_source.tar.gz` **does not exist**. Clicking the download button will produce a 404.

---

## Minor Bugs / Code Quality Issues

### 9. Unused `stance` key in green_bot export preset — `projects.js` line 962

```js
return { stance: 1.0, height: 0.65, bend: 0.25 + t * 0.35, explode: t * 0.8, scale: 1.0 };
```

The `stance` key is not a defined control for `green_bot` (its controls are `explode`, `height`, `bend`, `scale`). The `buildGreenBot.update()` function ignores it. During export, `setParam("stance", 1.0)` will:
- Set `params.stance = 1.0` (harmless but unused)
- Look for `sliderEls.stance` (doesn't exist; no-op)

**Impact:** No crash, but dead data in every export step. Suggests a leftover from a removed control.

---

### 10. Service worker caches non-existent static assets — `sw.js` lines 3–9

```js
const STATIC_ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/static/images/ajani_bg.png',
  '/static/images/counsel_bg.png',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png'
];
```

Although the install handler filters out `icon-` URLs, `ajani_bg.png` and `counsel_bg.png` are still attempted. Since these files don't exist, `cache.addAll()` may throw (any single 404 causes the entire `addAll` promise to reject), potentially failing the service worker installation.

The code at line 21 filters: `STATIC_ASSETS.filter(url => !url.includes('icon-'))` — this removes the icon URLs but **leaves `ajani_bg.png` and `counsel_bg.png`** which also don't exist.

**Impact:** Service worker may fail to install, breaking offline support and caching entirely.

---

### 11. `iframe` sandbox too restrictive for generated designs — `index.html` line 435

```html
<iframe id="designIframe" sandbox="allow-same-origin" style="display: none; ..."></iframe>
```

The sandbox only allows `allow-same-origin` but not `allow-scripts`. Any AI-generated design HTML containing `<script>` tags, `onclick` handlers, or JS-driven animations will be inert. While this is labeled as intentional for security ("prevents script execution" in comment at line 7871), it means interactive design previews don't work. CSS animations still work, but any JS-based interactivity in generated designs is silently disabled.

---

### 12. `green_bot` `buildGreenBot` doesn't return `parts` — `projects.js` ~line 504

The `buildGreenBot` function returns `{ update(p) { ... } }` without a `parts` property. In the export function (`main.js` line 307), the code checks `if (stepParams.visible && currentProject.parts)`. For `green_bot`, `currentProject.parts` is `undefined`, so the visibility logic is silently skipped. This is benign for `green_bot` since its export presets don't use `visible`, but it's an inconsistency with `buildMetalFlower` which returns `{ parts, update }`.

---

### 13. CSS references undefined variables in inline styles — `index.html`

Several inline `style` attributes in the HTML reference CSS custom properties like `var(--bg-secondary)`, `var(--border-color)`, `var(--text-primary)`, etc. These are defined in the external CSS file (`main.css`) and generally work. However, the `<select>` elements at lines 996, 1254, 1269, 1292, 1302 use inline styles with:
```css
background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-color);
```
These depend on the CSS file loading. If `main.css` fails to load (network issue, wrong path), all these elements would fall back to browser defaults, breaking the dark theme appearance.

---

## Summary Table

| # | Severity | File(s) | Issue |
|---|----------|---------|-------|
| 1 | **CRITICAL** | `index.html` | `showLessonStep()` references 3 non-existent DOM IDs |
| 2 | **CRITICAL** | `index.html` | Voice toggle references non-existent `voiceBtn`/`voiceIcon` IDs |
| 3 | **CRITICAL** | `index.html` | `showNotification` overridden — 40+ in-page toasts silently broken |
| 4 | **CRITICAL** | `index.html` | `updateSystemMetrics` signature mismatch — metrics show random values |
| 5 | **MODERATE** | `index.html` | `switchPersona` hook dead code — AI presence indicators never update |
| 6 | **MODERATE** | Multiple | `static/images/` directory missing — all PWA icons, favicons broken |
| 7 | **MODERATE** | `index.html`, `sw.js` | Inconsistent notification icon paths (`/icons/` vs `/images/`) |
| 8 | **MODERATE** | `download.html` | Links to non-existent `atlas_core_source.tar.gz` |
| 9 | **MINOR** | `viewer/projects.js` | Unused `stance` key in green_bot export preset |
| 10 | **MINOR** | `sw.js` | Tries to cache non-existent image files, may break SW install |
| 11 | **MINOR** | `index.html` | Iframe sandbox blocks JS in generated designs |
| 12 | **MINOR** | `viewer/projects.js` | `buildGreenBot` missing `parts` property (inconsistency) |
| 13 | **MINOR** | `index.html` | Inline styles depend on external CSS variables loading |
