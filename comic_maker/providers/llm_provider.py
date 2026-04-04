"""LLM provider for Comic-maker."""

import json
import os

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")


def _load_prompt(filename: str) -> str:
    with open(os.path.join(_PROMPTS_DIR, filename), encoding="utf-8") as f:
        return f.read()


class LLMProvider:
    def __init__(self):
        self.model = config.LLM_MODEL

    def segment_text(self, chapter_text: str):
        _ = chapter_text
        return []

    def enrich_beat(self, beat_text: str) -> dict:
        template = _load_prompt("segment_chapter.txt")
        prompt = template.replace("{text}", beat_text)
        raw = self._call_llm(system="你是漫画分镜助手，只输出 JSON。", user=prompt)
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0].strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "characters": [],
                "location": "",
                "time": "",
                "actions": [],
                "emotion": "",
                "visual_priority": "medium",
            }
        return {
            "characters": data.get("characters", []),
            "location": data.get("location", ""),
            "time": data.get("time", ""),
            "actions": data.get("actions", []),
            "emotion": data.get("emotion", ""),
            "visual_priority": data.get("visual_priority", "medium"),
        }

    def plan_shot(self, beat_text: str) -> dict:
        _ = beat_text
        return {}

    def build_prompt(self, payload: dict) -> str:
        _ = payload
        return ""

    def _call_llm(self, system: str, user: str) -> str:
        if config.LLM_BACKEND == "gemini":
            return self._call_gemini(system, user)
        if config.LLM_BACKEND == "deepseek":
            return self._call_deepseek(system, user)
        return self._call_claude(system, user)

    def _call_deepseek(self, system: str, user: str) -> str:
        from openai import OpenAI

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

    def _call_gemini(self, system: str, user: str) -> str:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=self.model,
            contents=user,
            config=types.GenerateContentConfig(system_instruction=system),
        )
        return response.text

    def _call_claude(self, system: str, user: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return message.content[0].text
