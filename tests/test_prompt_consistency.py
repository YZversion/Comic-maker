"""
Consistency regression tests:
- Every prompt must contain the main character anchor.
- Every prompt must contain the fixed style lock.
- A beat with no characters must inherit the previous panel's active character anchor.
- LLM rewrites must not be allowed to drop the character anchor.
- Character state must not leak inactive characters into later panels.
"""

import unittest
from unittest.mock import patch

from comic_maker.core.models import Beat
from comic_maker.core.planner import plan_shots
from comic_maker.core.prompt_builder import build_panel_jobs

_CHAR_DB = {
    "Lin": {
        "appearance": "teenage girl, short black hair, school uniform, slim",
        "aliases": ["Xiao Lin", "she"],
        "refs": [],
    },
    "Zhou": {
        "appearance": "teenage boy, messy dark hair, glasses, casual clothes",
        "aliases": ["he", "Ah Zhou"],
        "refs": [],
    },
}
_SCENE_DB: dict = {}
_PROP_DB: dict = {}

_LIN_ANCHOR_FRAGMENT = "short black hair"
_ZHOU_ANCHOR_FRAGMENT = "glasses"


def _make_beats_with_char(n: int = 4) -> list[Beat]:
    return [
        Beat(
            beat_id=f"b{i:03d}",
            text=f"beat {i}",
            characters=["Lin"],
            emotion="neutral",
            location="classroom",
        )
        for i in range(1, n + 1)
    ]


def _passthrough_llm(payload: dict) -> str:
    """Test double: echoes the structured sections back as a flat string."""
    return " ".join(v for v in payload.values() if v)


def _build_jobs(beats, prompt_builder_side_effect=None):
    side_effect = prompt_builder_side_effect or _passthrough_llm
    with patch("comic_maker.core.context_manager.load_character_db", return_value=_CHAR_DB), \
         patch("comic_maker.core.context_manager.load_scene_db", return_value=_SCENE_DB), \
         patch("comic_maker.core.context_manager.load_prop_db", return_value=_PROP_DB), \
         patch("comic_maker.core.prompt_builder.LLMProvider") as MockPromptLLM, \
         patch("comic_maker.core.planner.LLMProvider") as MockPlannerLLM:
        MockPromptLLM.return_value.build_panel_prompt.side_effect = side_effect
        MockPlannerLLM.return_value.plan_shot.return_value = {}
        shots = plan_shots(beats, use_llm=True)
        return build_panel_jobs(beats, shots)


class CharacterAnchorConsistencyTest(unittest.TestCase):
    def test_every_prompt_contains_character_anchor(self):
        jobs = _build_jobs(_make_beats_with_char(5))
        for job in jobs:
            self.assertIn(
                _LIN_ANCHOR_FRAGMENT,
                job.prompt,
                f"{job.panel_id} is missing the character anchor",
            )

    def test_every_prompt_contains_style_lock(self):
        jobs = _build_jobs(_make_beats_with_char(5))
        for job in jobs:
            self.assertIn("manga panel", job.prompt, f"{job.panel_id} missing style lock")
            self.assertIn("lineart", job.prompt, f"{job.panel_id} missing lineart keyword")

    def test_empty_character_beat_inherits_prev_anchor(self):
        beats = [
            Beat(beat_id="b001", text="beat 1", characters=["Lin"], emotion="neutral"),
            Beat(beat_id="b002", text="beat 2", characters=[]),
        ]
        jobs = _build_jobs(beats)
        self.assertIn(
            _LIN_ANCHOR_FRAGMENT,
            jobs[1].prompt,
            "second panel should inherit character anchor from first panel",
        )

    def test_llm_output_cannot_drop_character_anchor(self):
        beats = [Beat(beat_id="b001", text="beat 1", characters=["Lin"], emotion="neutral")]
        jobs = _build_jobs(
            beats,
            prompt_builder_side_effect=lambda _payload: "close up, soft lighting, neutral expression",
        )
        self.assertIn(
            _LIN_ANCHOR_FRAGMENT,
            jobs[0].prompt,
            "prompt builder should reinforce the character anchor after LLM rewrite",
        )

    def test_character_state_tracks_active_subset(self):
        beats = [
            Beat(beat_id="b001", text="beat 1", characters=["Lin", "Zhou"], emotion="neutral"),
            Beat(beat_id="b002", text="beat 2", characters=["Zhou"], emotion="neutral"),
            Beat(beat_id="b003", text="beat 3", characters=[]),
        ]
        jobs = _build_jobs(beats)

        self.assertIn(_LIN_ANCHOR_FRAGMENT, jobs[0].prompt)
        self.assertIn(_ZHOU_ANCHOR_FRAGMENT, jobs[0].prompt)
        self.assertIn(_ZHOU_ANCHOR_FRAGMENT, jobs[1].prompt)
        self.assertNotIn(
            _LIN_ANCHOR_FRAGMENT,
            jobs[1].prompt,
            "single-character beat should not inherit inactive characters",
        )
        self.assertIn(
            _ZHOU_ANCHOR_FRAGMENT,
            jobs[2].prompt,
            "empty beat should inherit the most recent active character subset",
        )
        self.assertNotIn(
            _LIN_ANCHOR_FRAGMENT,
            jobs[2].prompt,
            "empty beat should inherit only the most recent active character subset",
        )

    def test_seed_is_deterministic(self):
        jobs_a = _build_jobs(_make_beats_with_char(3))
        jobs_b = _build_jobs(_make_beats_with_char(3))
        for a, b in zip(jobs_a, jobs_b):
            self.assertEqual(a.seed, b.seed, f"{a.panel_id} seed is not deterministic")

    def test_negative_prompt_is_set(self):
        jobs = _build_jobs(_make_beats_with_char(3))
        for job in jobs:
            self.assertTrue(job.negative_prompt, f"{job.panel_id} missing negative_prompt")


if __name__ == "__main__":
    unittest.main()
