"""LLM provider stub for Day1/Day2."""

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config


class LLMProvider:
    def __init__(self):
        self.model = config.LLM_MODEL

    def segment_text(self, chapter_text: str):
        _ = chapter_text
        return []

    def enrich_beat(self, beat_text: str) -> dict:
        _ = beat_text
        return {
            "characters": [],
            "location": "",
            "time": "",
            "actions": [],
            "emotion": "",
            "visual_priority": "medium",
        }

    def plan_shot(self, beat_text: str) -> dict:
        _ = beat_text
        return {}

    def build_prompt(self, payload: dict) -> str:
        _ = payload
        return ""

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
