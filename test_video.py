"""Offline contract checks: python -m unittest -v test_video."""
import json
import unittest
from unittest.mock import patch

import kie_server as server


class VideoTests(unittest.TestCase):
    def call(self, name, arguments):
        status, response = server.process_request_body(json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": arguments}}))
        self.assertEqual(status, 200)
        return response["result"]

    @patch.dict("os.environ", {"KIE_API_KEY": "test-only"})
    def test_submit_returns_id_without_polling(self):
        options = {"duration": 15, "resolution": "720p", "aspect_ratio": "16:9",
                   "generate_audio": False,
                   "reference_image_urls": ["https://example.com/image.png"]}
        with patch.object(server, "_http", return_value=(200, {
                "code": 200, "data": {"taskId": "video-123"}})) as http:
            result = self.call("kie_generate_video", {"prompt": "A moving sculpture", "input": options})
        http.assert_called_once_with("POST", server.CREATE_URL, {
            "model": "bytedance/seedance-2-5",
            "input": dict(options, prompt="A moving sculpture")})
        self.assertIn("task_id=video-123", result["content"][0]["text"])
        self.assertNotIn("isError", result)

    @patch.dict("os.environ", {"KIE_API_KEY": "test-only"})
    def test_invalid_input_does_not_submit(self):
        with patch.object(server, "_http") as http:
            for args in ({"prompt": " "}, {"prompt": "x", "input": []},
                         {"prompt": "x", "model": 42},
                         {"prompt": "x", "input": {"prompt": "override"}}):
                self.assertTrue(self.call("kie_generate_video", args)["isError"])
        http.assert_not_called()

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_key(self):
        with patch.object(server, "_http") as http:
            self.assertTrue(self.call("kie_generate_video", {"prompt": "x"})["isError"])
        http.assert_not_called()

    @patch.dict("os.environ", {"KIE_API_KEY": "test-only", "KIE_SAVE_DIR": ""})
    def test_status_and_result(self):
        for record, expected in [
            ({"state": "waiting"}, "state=waiting"),
            ({"state": "success", "resultJson": json.dumps({"resultUrls": [
                "https://example.com/movie.mp4"]})}, "https://example.com/movie.mp4"),
            ({"state": "fail", "failMsg": "Rejected", "failCode": "400"}, "Rejected")
        ]:
            with patch.object(server, "_http", return_value=(200, {"code": 200, "data": record})):
                result = self.call("kie_get_task", {"task_id": "video-123"})
            self.assertIn(expected, result["content"][0]["text"])

    @patch.dict("os.environ", {"KIE_API_KEY": "test-only"})
    def test_api_errors_are_reported(self):
        for name, args in [("kie_generate_video", {"prompt": "x"}),
                           ("kie_get_task", {"task_id": "video-123"})]:
            with patch.object(server, "_http", return_value=(200, {"code": 402, "msg": "No credits"})):
                result = self.call(name, args)
            self.assertTrue(result["isError"])
            self.assertIn("No credits", result["content"][0]["text"])

    def test_image_payload_unchanged(self):
        with patch.object(server, "_http", return_value=(200, {"data": {"taskId": "image-123"}})) as http:
            self.assertEqual(server.create_task("cat", "nano-banana-2", "1:1", "1K", "png", []), "image-123")
        self.assertEqual(http.call_args.args[2], {"model": "nano-banana-2", "input": {
            "prompt": "cat", "aspect_ratio": "1:1", "resolution": "1K", "output_format": "png"}})


if __name__ == "__main__":
    unittest.main()
