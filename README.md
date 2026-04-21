# Atlas Core
Safety-first environmental robotics framework with AI persona-based educational assistant system.

## Play the SID build on the web (GitHub Pages)

This repository can auto-deploy the Godot SID project in `game/` to GitHub Pages.

1. In GitHub, go to **Settings -> Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push to `main` (or run the workflow manually from Actions).
4. Your live URL will be:

   `https://monkey-cpu-ally.github.io/atlas-core/`

The deploy workflow is in `.github/workflows/deploy-godot-web.yml`.

## Local secret setup

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and set your real API key:
   ```bash
   OPENAI_API_KEY=sk-...
   ```
3. Start the app as usual. The package now auto-loads `.env` at import time.

Notes:
- Do **not** commit `.env`.
- `OPENAI_API_KEY` is the preferred variable.
- `AI_INTEGRATIONS_OPENAI_API_KEY` is still supported for backward compatibility.
