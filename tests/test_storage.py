from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path
from shutil import rmtree
from unittest.mock import patch
from uuid import uuid4

from utils import profile_storage, score_storage, storage


def _workspace_temp_root() -> Path:
    root = Path("data") / "saves" / ".test_tmp"
    root.mkdir(parents=True, exist_ok=True)
    return root


class WorkspaceTempDir:
    def __enter__(self) -> str:
        self.path = _workspace_temp_root() / f"tmp-{uuid4().hex}"
        self.path.mkdir(parents=True, exist_ok=True)
        return str(self.path)

    def __exit__(self, exc_type, exc, tb) -> None:
        rmtree(self.path, ignore_errors=True)


class ProfileStorageTests(unittest.TestCase):
    def test_profile_load_returns_defaults_when_file_missing(self) -> None:
        with WorkspaceTempDir() as tmp:
            root = Path(tmp)
            profile_file = root / "profile.json"
            legacy_file = root / "legacy_profile.json"

            with (
                patch.object(profile_storage, "PROFILE_FILE", profile_file),
                patch.object(profile_storage, "LEGACY_PROFILE_FILE", legacy_file),
            ):
                loaded = profile_storage.load_profile()

            self.assertEqual(loaded["total_runs"], profile_storage.DEFAULT_PROFILE["total_runs"])
            self.assertEqual(loaded["settings"]["theme_name"], profile_storage.DEFAULT_PROFILE["settings"]["theme_name"])

    def test_profile_save_and_load_roundtrip(self) -> None:
        with WorkspaceTempDir() as tmp:
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
        with WorkspaceTempDir() as tmp:
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
        with WorkspaceTempDir() as tmp:
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
        with WorkspaceTempDir() as tmp:
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


class DailyScoreStorageTests(unittest.TestCase):
    def test_daily_score_save_and_load_roundtrip(self) -> None:
        with WorkspaceTempDir() as tmp:
            root = Path(tmp)
            score_file = root / "daily_scores.json"
            legacy_file = root / "legacy_daily_scores.json"

            with (
                patch.object(storage, "DAILY_SCORE_FILE", score_file),
                patch.object(storage, "LEGACY_DAILY_SCORE_FILE", legacy_file),
            ):
                storage.record_daily_score("2026-05-17", 20260517, 4200, "A", "game_won")
                loaded = storage.load_daily_scores()

            self.assertEqual(loaded["scores"][0]["date"], "2026-05-17")
            self.assertEqual(loaded["scores"][0]["seed"], 20260517)
            self.assertEqual(loaded["scores"][0]["score"], 4200)
