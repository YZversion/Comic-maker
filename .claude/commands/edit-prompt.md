# Edit Prompt

View and edit the LLM system prompts in `comic_maker/prompts/`.

## Steps

1. List all `.txt` files in `comic_maker/prompts/` and show the user what each one does:
   - Chinese narrative analysis prompts (used by `segmenter`, `planner`)
   - English image prompt refinement prompts (used by `prompt_builder`)
2. Ask which prompt to view or edit.
3. Read the selected file and display it in full.
4. If the user wants to edit:
   - Clarify the intent (e.g. "make shot types more dynamic", "add emphasis on lighting direction").
   - Make the edit using the Edit tool.
   - Highlight what changed and why.
5. Warn about side effects:
   - Changes to segmenter/planner prompts affect `Beat` and `ShotPlan` structure — run `test_prompt_consistency.py` after.
   - Changes to `prompt_builder` prompts affect character anchor injection — always verify `STYLE_LOCK` is still appended last.
   - Existing `project_state.json` data was produced by the old prompt; re-running affected stages will produce different output.

## Rules
- Do not move prompt logic into Python code — keep system prompts in `.txt` files.
- Do not remove the character anchor injection instructions from the prompt_builder prompt.
- Prompts that expect JSON output must keep the JSON schema specification intact.
