import os
import tempfile
import unittest
from unittest.mock import patch

from comic_maker.core import page_builder, panel_runner, storage
from comic_maker.core.models import PanelJob


class RetryNoPanelGrowthTest(unittest.TestCase):
    def test_retry_does_not_increase_manifest_panel_count(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = os.path.join(tmp_dir, "panel_manifest.json")
            page_manifest_path = os.path.join(tmp_dir, "page_manifest.json")
            panels_dir = os.path.join(tmp_dir, "panels")
            os.makedirs(panels_dir, exist_ok=True)
            storage.save_json(manifest_path, [])

            def append_to_temp_manifest(record):
                storage.append_panel_manifest(record, path=manifest_path)

            with patch("comic_maker.core.panel_runner.append_panel_manifest", side_effect=append_to_temp_manifest), patch(
                "comic_maker.core.panel_runner.append_log", lambda _message: None
            ), patch("comic_maker.core.panel_runner.config.PANELS_DIR", panels_dir):
                first = PanelJob(panel_id="p001", beat_id="b001", prompt="first prompt")
                second = PanelJob(panel_id="p002", beat_id="b002", prompt="second prompt")

                panel_runner.run_panel_job(first)
                panel_runner.retry_panel_job(first, "fix-action")
                panel_runner.run_panel_job(second)

            manifest = storage.load_json(manifest_path, [])

            self.assertEqual(len(manifest), 2, "retry should update existing panel record instead of appending")
            self.assertEqual([item["panel_id"] for item in manifest], ["p001", "p002"])
            self.assertEqual(manifest[0]["retry_count"], 1)
            self.assertIn("[Retry fix: fix-action]", manifest[0]["prompt"])

            pages = page_builder.build_page_manifest(
                panel_manifest_path=manifest_path,
                output_path=page_manifest_path,
            )
            total_panels_in_pages = sum(len(page) for page in pages)
            self.assertEqual(total_panels_in_pages, 2)


if __name__ == "__main__":
    unittest.main()
