from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from utils import profile_storage, score_storage


class ProfileStorageTests(unittest.TestCase):
    def test_profile_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile_file = root / "profile.json"
            legacy_file = root / "legacy_profile.json"
            payload = deepcopy(profile_storage.DEFAULT_PROFILE)
            payload["total_runs"] = 7
            payload["settings"]["theme_name"] = "Cool Summer"

            with (
                patch.object(profile_storage, "PROFILE_FILE", profile_file),
                patch.object(profile_storage, "LEGACY_PROFILE_FILE", legacy_file),
            ):
                profile_storage.save_profile(payload)
                loaded = profile_storage.load_profile()

            self.assertEqual(loaded["total_runs"], 7)
            self.assertEqual(loaded["settings"]["theme_name"], "Cool Summer")
            self.assertTrue(profile_file.exists())

    def test_profile_load_migrates_legacy_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile_file = root / "profile.json"
            legacy_file = root / "legacy_profile.json"
            legacy_payload = deepcopy(profile_storage.DEFAULT_PROFILE)
            legacy_payload["best_score"] = 4321
            legacy_file.write_text(json.dumps(legacy_payload), encoding="utf-8")

            with (
                patch.object(profile_storage, "PROFILE_FILE", profile_file),
                patch.object(profile_storage, "LEGACY_PROFILE_FILE", legacy_file),
            ):
                loaded = profile_storage.load_profile()

            self.assertEqual(loaded["best_score"], 4321)
            self.assertTrue(profile_file.exists())


class ScoreStorageTests(unittest.TestCase):
    def test_high_score_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            score_file = root / "scores.json"
            legacy_file = root / "legacy_scores.json"

            with (
                patch.object(score_storage, "SCORE_FILE", score_file),
                patch.object(score_storage, "LEGACY_SCORE_FILE", legacy_file),
            ):
                score_storage.save_high_score(9999)
                loaded = score_storage.load_high_score()

            self.assertEqual(loaded, 9999)
            self.assertTrue(score_file.exists())

    def test_high_score_load_migrates_legacy_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            score_file = root / "scores.json"
            legacy_file = root / "legacy_scores.json"
            legacy_file.write_text(json.dumps({"high_score": 5555}), encoding="utf-8")

            with (
                patch.object(score_storage, "SCORE_FILE", score_file),
                patch.object(score_storage, "LEGACY_SCORE_FILE", legacy_file),
            ):
                loaded = score_storage.load_high_score()

            self.assertEqual(loaded, 5555)
            self.assertTrue(score_file.exists())
