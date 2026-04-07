# Run Tests

Run the appropriate test suite based on what was recently changed.

## Steps

1. Check which files were modified (via `git diff --name-only HEAD` or ask the user).
2. Map changed files to the tests that must pass:

   | Changed file | Required test |
   |---|---|
   | `panel_runner.py` or `storage.py` | `tests/test_retry_no_panel_growth.py` |
   | `prompt_builder.py` | `tests/test_prompt_consistency.py` |
   | `main.py` (new pipeline step) | `tests/test_run.py` |
   | Any file | Full suite: `python -m unittest discover -s tests -p "test_*.py" -v` |

3. Run the identified tests using the Bash tool with `IMAGE_PROVIDER=mock`.
4. If tests fail:
   - Show the full error output.
   - Identify which assertion failed and in which test method.
   - Propose a fix. Do not blindly modify the test to make it pass — fix the implementation unless the test itself is wrong.
5. If tests pass, confirm and summarize.

## Commands

```bash
# Full suite
python -m unittest discover -s tests -p "test_*.py" -v

# Specific test file
python -m unittest tests.test_prompt_consistency -v

# Smoke test (no input required)
python -m comic_maker.test_run
```

## Rules
- Always run with `IMAGE_PROVIDER=mock` (set in env or confirm it's the default).
- Never modify a test to suppress a real failure — fix the code.
- `test_prompt_consistency.py` must cover: character-anchor presence, empty-beat inheritance, LLM anchor reinforcement, active-character subset tracking.
