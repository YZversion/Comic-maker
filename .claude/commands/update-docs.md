# Update Project Docs

Keep CLAUDE.md, docs/architecture.md, README.md, and .gitignore consistent with the current state of the codebase.

## Steps

1. Read the following files in full before touching anything:
   - `CLAUDE.md` (fall back to `agent.md` if CLAUDE.md does not exist)
   - `docs/architecture.md`
   - `README.md`
   - `.gitignore`
   - `.env.example`

2. Ask the user what they want to update. Accept free-form input such as:
   - "I added a new image provider (comfyui)"
   - "I changed the default IMAGE_PROVIDER"
   - "Add the new /my-skill slash command to the README"
   - "The pipeline now has an 8th stage"
   - "Add *.bak to gitignore"
   - "Sync everything with the current code"

   If the user says "sync everything", proceed to step 3 and auto-detect changes by reading the key source files listed below.

3. **Auto-detect mode** (only when user says "sync" or "sync everything"):
   - Read `comic_maker/config.py` → check IMAGE_PROVIDER options, LLM_BACKEND, new constants.
   - Read `comic_maker/providers/image_provider.py` → check supported providers in `generate()` dispatcher.
   - Read `comic_maker/providers/llm_provider.py` → check supported backends.
   - Read `comic_maker/core/models.py` → check model fields.
   - Read `.claude/commands/` file list → check for new or removed slash commands.
   - Diff what you find against what the docs currently say. List every discrepancy before writing anything.

4. For each file that needs changes, show the user a **before/after diff** (quote the old text, show the new text) and ask for confirmation before writing.

5. Apply confirmed changes using the Edit tool — never rewrite a whole file unless the user explicitly says "rewrite".

6. After all edits, re-read each modified file and verify the changes landed correctly.

7. Output a summary: which files were changed, which sections were updated, and any discrepancies that could not be auto-resolved (flag these for the user to handle manually).

## What each file should contain

### CLAUDE.md
- Project purpose (one paragraph)
- Quick-start commands
- Environment setup (which keys are required)
- Architecture in one paragraph
- Key files table (path → purpose)
- Data flow diagram
- Coding conventions (active constraints, not aspirational)
- Testing rules
- What NOT to do

### docs/architecture.md
- Module boundary diagram (Orchestration / Core / Providers layers)
- Pipeline stage order (numbered, what each consumes and produces)
- Data model contracts (required fields per model)
- Configuration ownership rules
- Storage rules and directory layout
- Provider isolation rules (how to add a new LLM or image backend)
- Retry and idempotency rules
- Testing requirements
- Dependency constraints (allowed packages)

### README.md
- One-line project description
- Prerequisites and install steps
- How to run (interactive, batch, offline, smoke test)
- Configuration table (all .env keys, which are required, which are optional)
- Supported image providers (with brief note on each)
- Available slash commands (list all .claude/commands/*.md by name and one-line purpose)
- Project structure (top-level directories only)

### .gitignore
- `.env` (never commit secrets)
- `comic_maker/output/` (generated assets)
- `comic_maker/data/*.json` except source files that are hand-edited
- Standard Python ignores: `__pycache__/`, `*.pyc`, `*.egg-info/`, `dist/`, `.venv/`
- IDE files: `.vscode/`, `.idea/`
- OS files: `.DS_Store`, `Thumbs.db`

## Rules
- Never delete a section from CLAUDE.md or architecture.md without the user's explicit approval.
- Never commit or push — only edit local files.
- If CLAUDE.md does not exist, offer to rename `agent.md` → `CLAUDE.md` before making any edits.
- Keep all code examples in docs accurate — if a command changed, update it.
- Do not add aspirational rules that are not enforced by the current code.
