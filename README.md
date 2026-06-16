# Atlas Core
Safety-first environmental robotics framework with AI persona-based educational assistant system.

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
