"""
Consistency regression tests:
- Every prompt must contain the main character anchor.
- Every prompt must contain the fixed style lock.
- A beat with no characters must inherit the previous panel's character anchor.
"""

import unittest
from unittest.mock import patch

from comic_maker.core.models import Beat
from comic_maker.core.planner import plan_shots
from comic_maker.core.prompt_builder import build_panel_jobs

_CHAR_DB = {
    "林晓": {
        "appearance": "teenage girl, short black hair, school uniform, slim",
        "aliases": ["晓", "她"],
    }
}
_SCENE_DB: dict = {}
_PROP_DB: dict = {}

_CHAR_ANCHOR_FRAGMENT = "short black hair"  # always present when 林晓 is in beat


def _make_beats_with_char(n: int = 4) -> list[Beat]:
    return [
        Beat(
            beat_id=f"b{i:03d}",
            text=f"beat {i}",
            characters=["林晓"],
            emotion="neutral",
            location="classroom",
        )
        for i in range(1, n + 1)
    ]


def _build_jobs(beats):
    with patch("comic_maker.core.context_manager.load_character_db", return_value=_CHAR_DB), \
         patch("comic_maker.core.context_manager.load_scene_db", return_value=_SCENE_DB), \
         patch("comic_maker.core.context_manager.load_prop_db", return_value=_PROP_DB):
        shots = plan_shots(beats)
        return build_panel_jobs(beats, shots)


class CharacterAnchorConsistencyTest(unittest.TestCase):
    def test_every_prompt_contains_character_anchor(self):
        jobs = _build_jobs(_make_beats_with_char(5))
        for job in jobs:
            self.assertIn(
                _CHAR_ANCHOR_FRAGMENT,
                job.prompt,
                f"{job.panel_id} is missing the character anchor",
            )

    def test_every_prompt_contains_style_lock(self):
        jobs = _build_jobs(_make_beats_with_char(5))
        for job in jobs:
            self.assertIn("manga panel", job.prompt, f"{job.panel_id} missing style lock")
            self.assertIn("lineart", job.prompt, f"{job.panel_id} missing lineart keyword")

    def test_empty_character_beat_inherits_prev_anchor(self):
        """A beat with no characters must carry forward the previous panel's anchor."""
        beats = [
            Beat(beat_id="b001", text="beat 1", characters=["林晓"], emotion="neutral"),
            Beat(beat_id="b002", text="beat 2", characters=[]),  # no characters
        ]
        jobs = _build_jobs(beats)
        self.assertIn(
            _CHAR_ANCHOR_FRAGMENT,
            jobs[1].prompt,
            "second panel should inherit character anchor from first panel",
        )

    def test_seed_is_deterministic(self):
        """Same panel_id must always produce the same seed."""
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
