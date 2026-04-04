"""Image provider. Day1/Day2 defaults to mock output."""

import os


class ImageProvider:
    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def generate(self, prompt: str, output_path: str) -> str:
        if self.provider == "mock":
            return self._mock_generate(prompt, output_path)
        raise NotImplementedError(f"Provider '{self.provider}' not implemented yet")

    def _mock_generate(self, prompt: str, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        placeholder = output_path + ".txt"
        with open(placeholder, "w", encoding="utf-8") as f:
            f.write(f"[MOCK IMAGE]\n\nPrompt:\n{prompt}\n")
        return placeholder
