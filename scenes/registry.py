from __future__ import annotations

from core.scene_ids import (
    ACHIEVEMENTS_SCENE,
    CAREER_SCENE,
    CHALLENGE_SCENE,
    DIALOGUE_SCENE,
    GAME_SCENE,
    JOURNAL_SCENE,
    MENU_SCENE,
    MODES_SCENE,
    OPTIONS_SCENE,
    PAUSE_SCENE,
    REPLAY_VIEWER_SCENE,
    RESULT_SCENE,
    RUN_HISTORY_SCENE,
    THEMES_SCENE,
)
from scenes.achievements_scene import AchievementsScene
from scenes.career_scene import CareerScene
from scenes.challenge_scene import ChallengeScene
from scenes.dialogue import DialogueScene
from scenes.game_scene import GameScene
from scenes.journal_scene import JournalScene
from scenes.menu import Menu
from scenes.modes_scene import ModesScene
from scenes.options_scene import OptionsScene
from scenes.pause_scene import PauseScene
from scenes.replay_viewer import ReplayViewerScene
from scenes.result_scene import ResultScene
from scenes.run_history_scene import RunHistoryScene
from scenes.themes_scene import ThemesScene


SCENE_FACTORIES = {
    MENU_SCENE: Menu,
    GAME_SCENE: GameScene,
    RESULT_SCENE: ResultScene,
    PAUSE_SCENE: PauseScene,
    OPTIONS_SCENE: OptionsScene,
    MODES_SCENE: ModesScene,
    CAREER_SCENE: CareerScene,
    ACHIEVEMENTS_SCENE: AchievementsScene,
    CHALLENGE_SCENE: ChallengeScene,
    RUN_HISTORY_SCENE: RunHistoryScene,
    THEMES_SCENE: ThemesScene,
    JOURNAL_SCENE: JournalScene,
    DIALOGUE_SCENE: DialogueScene,
    REPLAY_VIEWER_SCENE: ReplayViewerScene,
}


SCENE_MUSIC = {
    MENU_SCENE: "menu",
    GAME_SCENE: "game",
    RESULT_SCENE: "result",
    PAUSE_SCENE: "pause",
    OPTIONS_SCENE: "options",
    MODES_SCENE: "menu",
    CAREER_SCENE: "options",
    ACHIEVEMENTS_SCENE: "options",
    CHALLENGE_SCENE: "menu",
    RUN_HISTORY_SCENE: "options",
    THEMES_SCENE: "options",
    JOURNAL_SCENE: "options",
    DIALOGUE_SCENE: "result",
    REPLAY_VIEWER_SCENE: "result",
}


def build_scene_table(ctx) -> dict[int, object]:
    return {scene_id: factory(ctx) for scene_id, factory in SCENE_FACTORIES.items()}
