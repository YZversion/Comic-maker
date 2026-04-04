# CLAUDE.md - Agent Instructions for Comic-Maker

## Project Purpose

Comic-Maker is a 7-stage pipeline that converts raw novel chapter text into structured comic production assets (panel images, page manifests, chapter bundles). It is not a web app or service; it is a batch processing CLI tool.

## Quick Start

```bash
# Install (editable)
pip install -e .

# Run interactive pipeline
python -m comic_maker.main

# Run in batch mode (no human review prompts)
python -m comic_maker.main --batch

# Run fully offline/mocked (no API calls)
python -m comic_maker.main --offline

# Smoke test (no input required)
python -m comic_maker.test_run

# Unit tests
python -m unittest discover -s tests -p "test_*.py" -v
```

## Environment Setup

Copy `.env.example` -> `.env` and fill in secrets. Never commit `.env`.

Required keys: `DEEPSEEK_API_KEY`, and at least one image backend key (`LIBLIB_ACCESS_KEY` + `LIBLIB_SECRET_KEY` for production, or set `IMAGE_PROVIDER=mock` for testing).

## Architecture in One Paragraph

`main.py` orchestrates the pipeline sequentially: `segmenter` splits text into `Beat` objects -> `planner` adds a `ShotPlan` to each beat -> `prompt_builder` assembles and refines English image prompts into `PanelJob` objects while maintaining chapter-level character anchor continuity -> `panel_runner` calls the image provider -> `reviewer` handles human approval/retry -> `page_builder` groups panels -> `exporter` bundles the chapter. All intermediate state is persisted as JSON in `comic_maker/data/`. All generated assets go to `comic_maker/output/`.

## Key Files

| File | Purpose |
|------|---------|
| `comic_maker/config.py` | All constants, paths, API keys; change config here first |
| `comic_maker/core/models.py` | `Beat`, `ShotPlan`, `PanelJob`, `CharacterProfile`; the data contracts |
| `comic_maker/core/storage.py` | All JSON reads/writes; touch this if schema changes |
| `comic_maker/providers/llm_provider.py` | DeepSeek integration; swap LLM backend here |
| `comic_maker/providers/image_provider.py` | Multi-backend image generation (mock/siliconflow/liblib) |
| `comic_maker/data/character_db.json` | Character appearance profiles; hand-editable source data |
| `comic_maker/data/scene_db.json` | Location descriptions; hand-editable source data |
| `comic_maker/prompts/*.txt` | LLM system prompts (Chinese narrative analysis + English image prompts) |

## Data Flow

```text
chapter text
    -> Beat[]            (segmenter + LLM enrichment)
    -> ShotPlan[]        (planner + LLM or rule-based fallback)
    -> PanelJob[]        (prompt_builder + LLM refinement + character-state continuity + anchor validation + STYLE_LOCK)
    -> images + manifest (panel_runner -> image provider)
    -> page_manifest     (page_builder, PANELS_PER_PAGE=4)
    -> exports/<chapter_id>/ (exporter, final bundle)
```

## Coding Conventions

- All config constants live in `config.py`. No magic strings/numbers in core logic.
- Every pipeline stage must be independently testable with mocked providers.
- LLM calls must have a rule-based fallback so the pipeline never hard-fails on LLM errors.
- `append_panel_manifest()` in `storage.py` upserts by `panel_id`; never duplicates on retry.
- Each `PanelJob` gets a deterministic seed via `md5(panel_id)` for reproducibility.
- `STYLE_LOCK` is always appended last in `prompt_builder.py`; never let stage code override it.
- `prompt_builder.py` owns chapter-level character continuity. A beat with no detected characters inherits the most recent active character subset, not an arbitrary previous full prompt.
- LLM prompt rewriting is not trusted for identity preservation. If rewritten text drops any required character anchor entry, `prompt_builder.py` must restore it before appending `STYLE_LOCK`.

## Testing Rules

- Always test retry logic with `test_retry_no_panel_growth.py` when touching `panel_runner.py` or `storage.py`.
- Always test prompt consistency with `test_prompt_consistency.py` when touching `prompt_builder.py`.
- `test_prompt_consistency.py` must cover character-anchor presence, empty-beat inheritance, LLM anchor reinforcement, and active-character subset tracking.
- New features that add LLM calls must work in `--offline` mode (mock the call).

## What NOT To Do

- Do not add a new data directory outside `comic_maker/data/` or `comic_maker/output/`.
- Do not hardcode API keys or model names; use `config.py` variables.
- Do not let any pipeline stage import from a later stage (no circular deps).
- Do not write to `panel_manifest.json` by overwriting the whole file; always use `append_panel_manifest()`.
- Do not add GUI or web server code; this is a CLI tool.
- Do not use `print()` for runtime output in core modules; use `storage.append_log()` or `config.DEBUG`.
