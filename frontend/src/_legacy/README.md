# Legacy frontend components — preserved, not imported.

The four files in this folder were used by the **pre-luxury HUD** but
removed when the luxury reskin shipped in Feb 2026. They are kept here
so the architect can restore them later if needed, without polluting
the active component tree.

| File | What it was |
|---|---|
| `ChatPanel.js` | Floating chat FAB with EN/ZU/YO/MAA language picker |
| `FileBrowserPanel.js` | Side popover listing uploaded files (superseded by `HUD/ArchiveBrowser.js`) |
| `FileUploadModal.js` | Chunked upload + AI categorisation modal |
| `useVoiceRecognition.js` | "Hey Atlas" wake-word hook (Web Speech API) |

**To restore any of these:**
1. `git mv frontend/src/_legacy/<file> frontend/src/components/<file>`
2. Re-add the import in `HUDInterface.js`
3. Re-add the matching CSS (still present in `App.css` — never removed)
4. Wire the FAB or top-bar button back into the luxury HUD

**Do not import directly from `_legacy/`.** The path is intentionally
non-standard so we never accidentally re-introduce these as live UI
without thinking. If you want them, move them out.
