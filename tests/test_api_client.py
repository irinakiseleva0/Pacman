from __future__ import annotations

import unittest
from pathlib import Path
from shutil import rmtree
from unittest.mock import patch
from uuid import uuid4

import requests

from utils import score_storage
from utils.api_client import LeaderboardClient


def _workspace_temp_root() -> Path:
    root = Path("data") / "saves" / ".test_tmp"
    root.mkdir(parents=True, exist_ok=True)
    return root


class _Response:
    def __init__(self, payload, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}")

    def json(self):
        return self.payload


class LeaderboardClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = _workspace_temp_root() / f"api-{uuid4().hex}"
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.score_file = self.temp_root / "scores.json"
        self.legacy_file = self.temp_root / "legacy_scores.json"
        self.score_patch = patch.object(score_storage, "SCORE_FILE", self.score_file)
        self.legacy_patch = patch.object(score_storage, "LEGACY_SCORE_FILE", self.legacy_file)
        self.score_patch.start()
        self.legacy_patch.start()

    def tearDown(self) -> None:
        self.score_patch.stop()
        self.legacy_patch.stop()
        rmtree(self.temp_root, ignore_errors=True)

    def test_submit_score_posts_with_jwt(self) -> None:
        captured = {}

        def fake_post(url, **kwargs):
            captured["url"] = url
            captured["kwargs"] = kwargs
            return _Response({"id": 1, "value": 9000})

        client = LeaderboardClient("http://api.test", token="jwt-token")
        with patch("utils.api_client.requests.post", side_effect=fake_post):
            result = client.submit_score("Arcade", 9000, 123456)
        client.close()

        self.assertEqual(result["value"], 9000)
        self.assertEqual(captured["url"], "http://api.test/api/scores/")
        self.assertEqual(captured["kwargs"]["headers"]["Authorization"], "Bearer jwt-token")
        self.assertNotIn("username", captured["kwargs"]["json"])

    def test_fetch_leaderboard_returns_limited_rows(self) -> None:
        payload = [{"value": 300}, {"value": 200}, {"value": 100}]

        def fake_get(url, **kwargs):
            self.assertEqual(kwargs["params"], {"mode": "time_attack"})
            return _Response(payload)

        client = LeaderboardClient("http://api.test")
        with patch("utils.api_client.requests.get", side_effect=fake_get):
            rows = client.fetch_leaderboard("Time Attack", limit=2)
        client.close()

        self.assertEqual(rows, payload[:2])

    def test_offline_submit_saves_local_high_score(self) -> None:
        client = LeaderboardClient("http://api.test")
        with patch("utils.api_client.requests.post", side_effect=requests.ConnectionError("offline")):
            result = client.submit_score("Arcade", 777, 1)
        client.close()

        self.assertTrue(result["offline"])
        self.assertEqual(score_storage.load_high_score(), 777)

    def test_offline_fetch_uses_local_high_score(self) -> None:
        score_storage.save_high_score(444)
        client = LeaderboardClient("http://api.test", username="iris")
        with patch("utils.api_client.requests.get", side_effect=requests.Timeout("offline")):
            rows = client.fetch_leaderboard("Arcade")
        client.close()

        self.assertEqual(rows[0]["value"], 444)
        self.assertEqual(rows[0]["player"]["username"], "iris")


if __name__ == "__main__":
    unittest.main()
