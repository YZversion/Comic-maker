# Check Pipeline

Inspect the current state of the pipeline for a chapter — what's done, what's pending, what failed.

## Steps

1. Read `comic_maker/data/project_state.json` — show chapter ID, total beats, current stage.
2. Read `comic_maker/data/panel_manifest.json` — tally panels by `status`:
   - `done`: how many
   - `pending` / `running`: how many (still in progress)
   - `failed` / `error`: how many (need attention)
3. If any panels are failed, list their `panel_id` and `retry_count`.
4. Read the most recent log file in `comic_maker/output/logs/` and surface any ERROR-level lines.
5. Show a summary table:

   ```
   Chapter: <id>
   Stage reached: <stage>
   Panels: X done / Y pending / Z failed
   ```

6. If everything looks healthy, suggest the next command to run.
7. If there are failures, suggest running `/debug-panel` for details.

## Pipeline stage resume commands

```bash
# Resume from where it stopped (re-runs all pending stages)
python -m comic_maker.main --batch

# Offline/mock run for validation
python -m comic_maker.main --offline

# Smoke test
python -m comic_maker.test_run
```
