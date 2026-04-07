# Load Project Context

Read all authoritative project documents and internalize their rules before doing any work.

## Steps

1. Check if `CLAUDE.md` exists in the project root.
   - If yes: read `CLAUDE.md`.
   - If no: read `agent.md` and immediately warn the user:
     > ⚠️ `agent.md` should be renamed to `CLAUDE.md` so it auto-loads in every conversation.
     > Run: `mv agent.md CLAUDE.md` (or rename in your file explorer).

2. Read `docs/architecture.md` in full.

3. Read `README.md` in full (skip if it does not exist).

4. Read `.gitignore` (skip if it does not exist).

5. Output a compact summary structured as follows — keep each section to 3–5 bullet points:

   **Pipeline stages** (order, what each produces)
   **Key files** (config, models, storage, providers — one line each)
   **Hard constraints** (things I must never do — pull from "What NOT To Do" and architecture rules)
   **Active config** (current IMAGE_PROVIDER default, LLM_BACKEND, PANELS_PER_PAGE)
   **Test commands** (the exact commands to run tests)

6. Confirm: "Context loaded. Ready to work."

## Rules
- Do not modify any file during this skill.
- Do not ask the user any questions; this skill is read-only.
- If a file is missing, note it and continue — do not stop.
