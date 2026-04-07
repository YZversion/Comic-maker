# Add LLM Backend

Scaffold a new LLM backend into the pipeline.

## Steps

1. Read `comic_maker/providers/llm_provider.py` in full to understand the existing pattern (DeepSeek via OpenAI-compatible client).
2. Read `comic_maker/config.py` to see `LLM_BACKEND` values and model name constants.
3. Ask the user for:
   - Backend name (e.g. `openai`, `qwen`, `gemini`, `ollama`) — becomes the `LLM_BACKEND` config value
   - API endpoint (if not the standard OpenAI endpoint)
   - Model name(s) to use by default
   - Authentication method (API key, local, etc.)
4. Implement a new function `_<name>_call(prompt: str, system: str, **kwargs) -> str` in `llm_provider.py`.
   - Must return the raw text content of the LLM response.
   - Must raise a descriptive exception on hard failure (callers fall back to rule-based logic on any exception).
   - Must work in `--offline` mode when `LLM_BACKEND=mock`.
5. Wire it into the main `call_llm()` dispatcher.
6. Add required constants (`LLM_BACKEND`, model name, API key) to `config.py`.
7. Add the new key to `.env.example`.
8. Confirm that `python -m comic_maker.main --offline` still passes after the change.

## Rules
- Do not add a new provider file — everything goes in `llm_provider.py`.
- The `mock` backend must be unaffected by this change.
- LLM responses used for structured output must remain parseable as JSON; the fallback logic in the calling stage handles parse failures.
- Never hardcode model names; use `config.py` constants.
