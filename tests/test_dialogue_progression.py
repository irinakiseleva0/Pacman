from __future__ import annotations

import unittest

from core.context import GameContext
from core.progression import dialogue_for_level, load_dialogue_entries


class DialogueProgressionTests(unittest.TestCase):
    def test_dialogue_json_contains_required_triggers(self) -> None:
        entries = load_dialogue_entries()
        triggers = {entry.level_trigger for entry in entries}

        self.assertGreaterEqual(len(entries), 5)
        self.assertTrue({1, 3, 5, 8, "boss1"}.issubset(triggers))

    def test_level_five_queues_boss_dialogue_after_level_scene(self) -> None:
        entries = dialogue_for_level(5)

        self.assertEqual([entry.level_trigger for entry in entries], [5, "boss1"])

    def test_context_queues_and_consumes_dialogue_on_level_clear(self) -> None:
        ctx = GameContext()
        ctx.current_level = 1

        self.assertTrue(ctx.queue_dialogue_for_level_clear())

        queued = ctx.consume_pending_dialogue()
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0]["character"], "SYSTEM_AI")
        self.assertEqual(ctx.run.pending_dialogue, [])


if __name__ == "__main__":
    unittest.main()
