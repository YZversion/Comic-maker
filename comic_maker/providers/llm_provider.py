"""LLM provider for Comic-maker (DeepSeek only)."""

import json
import os

try:
    from comic_maker import config
    from comic_maker.core.models import Beat
    from comic_maker.core.storage import append_log
except ModuleNotFoundError:
    import config
    from core.models import Beat
    from core.storage import append_log

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_prompt(filename: str) -> str:
    with open(os.path.join(_PROMPTS_DIR, filename), encoding="utf-8") as f:
        return f.read()


def _strip_fences(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned.startswith("```"):
        return cleaned
    cleaned = cleaned.split("```", 2)[1]
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]
    return cleaned.rsplit("```", 1)[0].strip()


def _warn(message: str) -> None:
    if config.LOG_FALLBACKS:
        append_log(f"[WARN][LLM] {message}")


def _default_enrich() -> dict:
    return {
        "characters": [],
        "location": "",
        "time": "",
        "actions": [],
        "emotion": "",
        "visual_priority": "medium",
    }


class LLMProvider:
    def __init__(self):
        self.model = config.LLM_MODEL

    def segment_text(self, chapter_text: str):
        _ = chapter_text
        return []

    def enrich_beat(self, beat_text: str) -> dict:
        template = _load_prompt("segment_chapter.txt")
        prompt = template.replace("{text}", beat_text)
        try:
            raw = self._call_llm(system="你是漫画分镜助手，只输出 JSON。", user=prompt)
        except Exception as exc:
            _warn(f"enrich_beat call failed: {exc}; beat={beat_text[:80]!r}")
            return _default_enrich()

        cleaned = _strip_fences(raw)
        try:
            data = json.loads(cleaned)
            if not isinstance(data, dict):
                raise ValueError("parsed payload is not a JSON object")
        except Exception as exc:
            _warn(f"enrich_beat JSON parse failed: {exc}; beat={beat_text[:80]!r}")
            return _default_enrich()

        characters = data.get("characters", [])
        actions = data.get("actions", [])
        if not isinstance(characters, list):
            characters = []
        if not isinstance(actions, list):
            actions = []

        visual_priority = data.get("visual_priority", "medium")
        if visual_priority not in {"low", "medium", "high"}:
            visual_priority = "medium"

        return {
            "characters": characters,
            "location": data.get("location", ""),
            "time": data.get("time", ""),
            "actions": actions,
            "emotion": data.get("emotion", ""),
            "visual_priority": visual_priority,
        }

    def plan_shot(self, beat: Beat) -> dict:
        template = _load_prompt("plan_shot.txt")
        prompt = (
            template
            .replace("{text}", beat.text)
            .replace("{characters}", ", ".join(beat.characters) if beat.characters else "none")
            .replace("{emotion}", beat.emotion or "neutral")
            .replace("{location}", beat.location or "unknown")
        )
        try:
            raw = self._call_llm(system="你是漫画分镜导演，只输出 JSON。", user=prompt)
        except Exception as exc:
            _warn(f"plan_shot call failed: {exc}; beat_id={beat.beat_id}")
            return {}

        cleaned = _strip_fences(raw)
        try:
            data = json.loads(cleaned)
            if not isinstance(data, dict):
                raise ValueError("parsed payload is not a JSON object")
        except Exception as exc:
            _warn(f"plan_shot JSON parse failed: {exc}; beat_id={beat.beat_id}")
            return {}

        return {
            "shot_type": data.get("shot_type", ""),
            "subject_focus": data.get("subject_focus", ""),
            "composition": data.get("composition", ""),
            "mood": data.get("mood", ""),
        }

    def build_panel_prompt(self, payload: dict) -> str:
        template = _load_prompt("build_prompt.txt")
        prompt = (
            template
            .replace("{character_anchor}", payload.get("character_anchor", ""))
            .replace("{scene_anchor}", payload.get("scene_anchor", ""))
            .replace("{action}", payload.get("action", ""))
            .replace("{camera}", payload.get("camera", ""))
        )
        raw = self._call_llm(
            system="You are a manga image prompt writer. Output only the prompt, nothing else.",
            user=prompt,
        )
        text = raw.strip()
        if not text:
            _warn("build_panel_prompt returned empty text; fallback will be used by caller")
        return text

    def _call_llm(self, system: str, user: str) -> str:
        return self._call_deepseek(system, user)

    def _call_deepseek(self, system: str, user: str) -> str:
        if not config.DEEPSEEK_API_KEY:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Missing dependency 'openai'. Run: pip install openai") from exc

        client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content
