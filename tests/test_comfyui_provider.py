"""Unit tests for the ComfyUI image provider.

Runs entirely offline by mocking requests so no ComfyUI server is needed.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, call, patch


class TestComfyUIProvider(unittest.TestCase):
    """Test _comfyui_generate using a mocked requests module."""

    def _make_provider(self):
        from comic_maker.providers.image_provider import ImageProvider
        return ImageProvider(provider="comfyui")

    def _history_response(self, prompt_id: str, filename: str = "comic_panel_00001_.png"):
        """Return a fake /history response with a completed SaveImage output."""
        return {
            prompt_id: {
                "outputs": {
                    "99": {
                        "images": [
                            {"filename": filename, "subfolder": "", "type": "output"}
                        ]
                    }
                }
            }
        }

    @patch("comic_maker.providers.image_provider.config")
    @patch("comic_maker.providers.image_provider.ImageProvider._comfyui_generate")
    def test_dispatcher_routes_to_comfyui(self, mock_gen, mock_cfg):
        """generate() must call _comfyui_generate when provider='comfyui'."""
        mock_cfg.COMFYUI_URL = "http://127.0.0.1:8188"
        mock_gen.return_value = "/fake/path.png"

        provider = self._make_provider()
        result = provider.generate("test prompt", "/tmp/out")
        mock_gen.assert_called_once_with("test prompt", "/tmp/out", seed=None)
        self.assertEqual(result, "/fake/path.png")

    @patch("requests.get")
    @patch("requests.post")
    @patch("comic_maker.providers.image_provider.config")
    def test_full_generate_flow(self, mock_cfg, mock_post, mock_get):
        """_comfyui_generate submits workflow, polls history, downloads image."""
        mock_cfg.COMFYUI_URL = "http://127.0.0.1:8188"

        prompt_id = "test-prompt-id-123"

        # POST /prompt response
        post_resp = MagicMock()
        post_resp.json.return_value = {"prompt_id": prompt_id}
        mock_post.return_value = post_resp

        # GET /history: first call returns empty (still running), second returns done
        empty_hist = MagicMock()
        empty_hist.json.return_value = {}
        done_hist = MagicMock()
        done_hist.json.return_value = self._history_response(prompt_id)

        # GET /view: returns fake PNG bytes
        img_resp = MagicMock()
        img_resp.content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16  # minimal fake PNG header

        mock_get.side_effect = [empty_hist, done_hist, img_resp]

        provider = self._make_provider()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "panel_001")
            result = provider._comfyui_generate("1girl, manga style", output_path, seed=42)

        self.assertTrue(result.endswith(".png"))

        # Verify POST was to /prompt
        post_call_url = mock_post.call_args[0][0]
        self.assertIn("/prompt", post_call_url)

        # Verify prompt was injected into node 13
        submitted_workflow = mock_post.call_args[1]["json"]["prompt"]
        self.assertEqual(submitted_workflow["13"]["inputs"]["text"], "1girl, manga style")
        self.assertEqual(submitted_workflow["15"]["inputs"]["seed"], 42)

        # Verify SaveImage node 99 is present
        self.assertIn("99", submitted_workflow)
        self.assertEqual(submitted_workflow["99"]["class_type"], "SaveImage")

    @patch("requests.get")
    @patch("requests.post")
    @patch("comic_maker.providers.image_provider.config")
    def test_timeout_raises(self, mock_cfg, mock_post, mock_get):
        """_comfyui_generate must raise TimeoutError if history never completes."""
        mock_cfg.COMFYUI_URL = "http://127.0.0.1:8188"

        post_resp = MagicMock()
        post_resp.json.return_value = {"prompt_id": "abc"}
        mock_post.return_value = post_resp

        # History always returns empty
        empty = MagicMock()
        empty.json.return_value = {}
        mock_get.return_value = empty

        provider = self._make_provider()
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "panel_timeout")
            # Patch range to only iterate once so the test is fast
            with patch("builtins.range", return_value=range(1)):
                with self.assertRaises(TimeoutError):
                    provider._comfyui_generate("prompt", output_path, seed=1)

    def test_mock_provider_still_works(self):
        """Mock provider must be unaffected by the comfyui addition."""
        from comic_maker.providers.image_provider import ImageProvider
        provider = ImageProvider(provider="mock")
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "panel_mock")
            result = provider.generate("any prompt", output_path)
            self.assertTrue(os.path.exists(result))


if __name__ == "__main__":
    unittest.main()
