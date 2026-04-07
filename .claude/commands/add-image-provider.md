# Add Image Provider

Scaffold a new image generation backend into the pipeline.

## Steps

1. Read `comic_maker/providers/image_provider.py` in full to understand the existing provider pattern (mock, siliconflow, liblib).
2. Read `comic_maker/config.py` to see existing `IMAGE_PROVIDER` values and required config constants.
3. Ask the user for:
   - Provider name (e.g. `openai`, `comfyui`, `sd_webui`) — this becomes the `IMAGE_PROVIDER` config value
   - API endpoint and authentication method
   - Any provider-specific parameters (model name, sampler, resolution, etc.)
4. Implement `_<name>_generate(job: PanelJob) -> str` in `image_provider.py` following the contract:
   - Must accept a `PanelJob` and use `job.prompt`, `job.seed`, and `job.panel_id`
   - Must save the output image to `comic_maker/output/panels/<panel_id>.png` (use the path from `config.py`)
   - Must return the absolute file path on success
   - Must raise on failure (panel_runner handles retry)
5. Wire it into the `generate_panel_image()` dispatcher with the new `IMAGE_PROVIDER` branch.
6. Add required API key constants to `config.py` (read from `.env` via `os.getenv`).
7. Add the new key to `.env.example` with a placeholder value.
8. Write a unit test in `tests/` that runs the new provider with `IMAGE_PROVIDER=mock` substituted — or if the provider has its own mock mode, use that.

## Rules
- Never add a new provider file — everything goes in `image_provider.py`.
- Never hardcode API keys or model names; always use `config.py` constants.
- The mock backend must still run the entire pipeline offline after this change.
