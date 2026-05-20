from __future__ import annotations

import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch

from utils import replay
from utils.replay import ReplayPlayer, ReplayRecorder, list_replays


class ReplayTests(unittest.TestCase):
    def _ctx(self):
        pacman = type("Pacman", (), {"kind": "pacman", "x": 1, "y": 2, "state": "RIGHT"})()
        ghost = type("Ghost", (), {"kind": "ghost", "x": 3, "y": 4, "state": "CHASE"})()
        game_map = type("Map", (), {"dynamic_actors": [pacman, ghost]})()
        runtime = type("Runtime", (), {"game_map": game_map, "pacman": pacman, "replay_input": None})()
        return type("Ctx", (), {"runtime": runtime, "score": 100, "current_level": 1})()

    def test_recorder_delta_compresses_repeated_frames(self) -> None:
        ctx = self._ctx()
        recorder = ReplayRecorder()
        recorder.start(seed=123, mode="Arcade", map_name="map")

        recorder.record_tick(ctx)
        recorder.record_tick(ctx)
        ctx.runtime.pacman.x = 2
        recorder.record_tick(ctx)

        self.assertEqual(len(recorder.frames), 2)
        self.assertEqual(recorder.frames[0]["frame"], 0)
        self.assertEqual(recorder.frames[1]["frame"], 2)

    def test_save_list_and_playback_roundtrip(self) -> None:
        ctx = self._ctx()
        with TemporaryDirectory() as temp_dir:
            with patch.object(replay, "REPLAY_DIR", Path(temp_dir)):
                recorder = ReplayRecorder()
                recorder.start(seed=123, mode="Arcade", map_name="map")
                recorder.record_tick(ctx)
                path = recorder.save(score=9000)

                self.assertTrue(path.name.endswith(".replay"))
                self.assertEqual(list_replays(1)[0].score, 9000)

                player = ReplayPlayer(path)
                state = player.seek_next()
                self.assertEqual(state["pacman_pos"]["x"], 1)
                player.apply_to_context(ctx)
                self.assertIsInstance(ctx.runtime.replay_input, dict)

                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["metadata"]["seed"], 123)


if __name__ == "__main__":
    unittest.main()
