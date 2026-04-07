# Update Style

Safely update the global art style anchor (`STYLE_LOCK`) or the negative prompt (`NEGATIVE_PROMPT`) in `config.py`.

## Steps

1. Read `comic_maker/config.py` and show the user the current `STYLE_LOCK` and `NEGATIVE_PROMPT` values.
2. Ask which one to update and what the new value should be.
3. Remind the user of the contract:
   - `STYLE_LOCK` is appended **last** to every panel prompt, after all character, scene, action, and camera content. No pipeline stage overrides it.
   - `NEGATIVE_PROMPT` is passed directly to the image provider. Keep it in the same language/format as the current value.
4. Apply the change to `config.py` using the Edit tool.
5. Warn the user: existing panels already in `panel_manifest.json` with `status = "done"` used the old style. If they want visual consistency across the whole chapter, they should reset those panels and re-run `panel_runner`.
6. Show the diff of the change.

## Rules
- Only edit the constant values in `config.py` — do not touch surrounding logic.
- Do not truncate or move `STYLE_LOCK` in the prompt assembly chain; only change its content here.
