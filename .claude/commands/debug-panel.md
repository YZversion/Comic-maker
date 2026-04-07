# Debug Panel

Diagnose why a specific panel failed or produced unexpected output.

## Steps

1. Read `comic_maker/data/panel_manifest.json`. Find all panels with `status != "done"` or ask the user for a specific `panel_id`.
2. For the target panel, show:
   - `panel_id`, `beat_id`, `status`, `retry_count`
   - The full `prompt` field
   - The `seed`
3. Read the corresponding `Beat` and `ShotPlan` from `comic_maker/data/project_state.json` (match by `beat_id`) to understand what the panel was supposed to depict.
4. Read the latest log from `comic_maker/output/logs/` to find error messages associated with this panel.
5. Diagnose the likely cause:
   - `retry_count >= MAX_RETRY` → hard failure after exhausting retries; inspect the last log error
   - Prompt missing character anchor → `prompt_builder.py` character continuity issue
   - Image provider HTTP error → network/auth issue; check API key in `.env`
   - JSON parse error in LLM response → LLM fallback not firing; check `llm_provider.py`
6. Propose a concrete fix and ask if the user wants you to apply it.
7. If the fix requires re-running a stage, show the exact command.

## Common fixes
- Reset a panel for retry: set `status = "pending"` and `retry_count = 0` in the manifest via `storage.append_panel_manifest()` logic (never edit the JSON directly in code — remind the user of this rule if relevant).
- Missing character: check `character_db.json` has the character name matching what the beat detected.
