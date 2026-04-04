# Architecture Constraints - Comic-Maker

## Module Boundaries

The project is divided into three layers. Dependencies only flow downward:

```text
Orchestration   -> main.py                 -> Entry point only; no business logic
Pipeline Core   -> comic_maker/core/       -> Pure transformation logic
Providers       -> comic_maker/providers/  -> External API isolation layer
```

Constraint: `core/` must not import from `providers/` directly. The provider interface is injected by `main.py` or passed as a callable. This allows `--offline` mode to swap providers without modifying core logic.

---

## Pipeline Stage Order

Each stage consumes the output of the previous stage. The order must not change:

```text
1. segmenter      -> produces Beat[]
2. planner        -> consumes Beat[], produces ShotPlan[]
3. prompt_builder -> consumes Beat[] + ShotPlan[], produces PanelJob[]
4. panel_runner   -> consumes PanelJob[], produces image files + updates manifest
5. reviewer       -> consumes manifest, may trigger panel_runner retry
6. page_builder   -> consumes manifest, produces page_manifest
7. exporter       -> consumes all manifests, produces exports/<chapter_id>/
```

A stage may only be skipped, not reordered. Stages 5+ may be skipped in `--batch` mode (`reviewer`) or when re-running a partial pipeline.

### Prompt Builder Contract

`prompt_builder` owns prompt-level character consistency. It is responsible for:

- Resolving the current beat's character anchor from canonical character context.
- Maintaining chapter-level character state so empty-character beats inherit the most recent active character subset.
- Rejecting silent identity drift from LLM rewrites by restoring any required character anchor entries before appending `STYLE_LOCK`.
- Appending `STYLE_LOCK` last, after all character, scene, action, and camera content.

---

## Data Model Contracts

Data classes in `comic_maker/core/models.py` are the single source of truth. Any change to a model must be reflected in:

- `storage.py` (serialization)
- The corresponding LLM prompt in `prompts/` (if the field is LLM-populated)
- `tests/test_prompt_consistency.py`

### Required Fields

| Model | Required fields |
|-------|-----------------|
| `Beat` | `beat_id`, `text`, `characters`, `location`, `emotion`, `visual_priority` |
| `ShotPlan` | `beat_id`, `shot_type`, `composition` |
| `PanelJob` | `panel_id`, `beat_id`, `prompt`, `status`, `retry_count`, `seed` |
| `CharacterProfile` | `name`, `static.appearance` |

---

## Configuration Ownership

All tuneable constants belong in `config.py`. No other module may define magic values for:

- Directory paths
- API endpoints or model names
- Pipeline parameters (`PANELS_PER_PAGE`, `MAX_RETRY`)
- The `STYLE_LOCK` string
- The `NEGATIVE_PROMPT` string

`STYLE_LOCK` is a global art style anchor. It must be appended last in every panel prompt, after all character, scene, action, and camera sections. No pipeline stage may override or truncate it.

---

## Storage Rules

All persistence goes through `comic_maker/core/storage.py`. No module may write JSON files directly.

Panel manifest upsert rule: `append_panel_manifest(panel: PanelJob)` updates an existing record if `panel_id` already exists, otherwise appends. This guarantees retry does not duplicate entries. Any code that mutates panel state must go through this function.

Directory layout:

```text
comic_maker/
|- data/               # Source + runtime state (JSON only)
|  |- character_db.json
|  |- scene_db.json
|  |- prop_db.json
|  |- panel_manifest.json
|  `- project_state.json
`- output/             # All generated assets
   |- panels/
   |- pages/
   |- exports/
   `- logs/
```

No new top-level directories. Do not create `data/` or `output/` at the project root.

---

## Provider Isolation

`comic_maker/providers/` contains adapters for all external services. Rules:

1. Each provider module exposes a single callable matching the interface used by `main.py`.
2. The `mock` backend must be able to run the entire pipeline without network access.
3. LLM provider responses must be parseable as JSON where the caller expects structured output. If parsing fails, the calling stage falls back to rule-based logic; it must not raise an exception.
4. Prompt-writing LLM output is advisory only. `prompt_builder` must validate that required character anchor entries survive any rewrite.
5. Image provider must save the output file and return its path. On failure it may raise; `panel_runner.py` handles the retry.

Adding a new LLM backend: add a new function in `llm_provider.py`, gate it behind a new `LLM_BACKEND` value in `config.py`. Do not add a new provider file.

Adding a new image backend: add a new `_<name>_generate()` function in `image_provider.py`, gate it behind a new `IMAGE_PROVIDER` value in `config.py`. Do not add a new provider file.

---

## Retry And Idempotency

- Max retries: `config.MAX_RETRY` (default 3). Hard limit; never override per-call.
- Retry prompt modification: append `"[Retry fix: <reason>]"` to the existing prompt. Never replace the prompt wholesale.
- Seed: deterministic per `panel_id` (`int(md5(panel_id), 16) % (2**32)`). A retry uses the same seed; only the prompt changes.
- Re-running the pipeline on the same chapter must produce the same panel IDs and seeds.

---

## Testing Requirements

Every new pipeline stage or provider must have:

1. A unit test that runs with `IMAGE_PROVIDER=mock` and mocked LLM calls.
2. The test must pass with `python -m unittest discover -s tests`.

`test_prompt_consistency.py` is the regression suite for prompt-level identity guarantees. Changes to `prompt_builder.py`, character anchoring, or prompt LLM behavior must preserve:

- Character-anchor presence in every prompt that should contain a character.
- Empty-beat inheritance from the most recent active character subset.
- Reinforcement of character anchors when LLM rewrites omit them.
- Stable deterministic seeds and negative prompts.

The `--offline` flag in `main.py` is the integration-test harness. Any new `main.py` pipeline step must be covered by `test_run.py`.

---

## Dependency Constraints

Allowed external dependencies (see `requirements.txt`):

- `openai` - DeepSeek API client (OpenAI-compatible)
- `python-dotenv` - environment loading
- `requests` - HTTP for image provider polling
- `pillow` - image file handling

Do not add heavy frameworks (`FastAPI`, `SQLAlchemy`, `Celery`, etc.). This is a CLI batch tool; keep the dependency surface minimal.
