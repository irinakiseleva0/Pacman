from __future__ import annotations

import core.raylib_api as pyray
import ui.ui as ui_theme

from assets.assets import Assets
from core.context import GameContext
from core.scene_ids import ACHIEVEMENTS_SCENE, CAREER_SCENE, CHALLENGE_SCENE, EXIT_SCENE, GAME_SCENE, JOURNAL_SCENE, MENU_SCENE, MODES_SCENE, OPTIONS_SCENE, PAUSE_SCENE, RESULT_SCENE, RUN_HISTORY_SCENE, THEMES_SCENE
from scenes.menu import Menu
from scenes.game_scene import GameScene
from scenes.result_scene import ResultScene
from scenes.pause_scene import PauseScene
from scenes.options_scene import OptionsScene
from scenes.modes_scene import ModesScene
from scenes.career_scene import CareerScene
from scenes.achievements_scene import AchievementsScene
from scenes.challenge_scene import ChallengeScene
from scenes.run_history_scene import RunHistoryScene
from scenes.themes_scene import ThemesScene
from scenes.journal_scene import JournalScene
from ui.layout import DEFAULT_LAYOUT
from utils.audio_manager import AudioManager


class Game:
    def __init__(self) -> None:
        self.ctx = GameContext()
        self.ctx.apply_layout(DEFAULT_LAYOUT)
        self.audio = AudioManager()
        self.ctx.audio_manager = self.audio

        self.current_scene_index = MENU_SCENE
        self.scenes = [
            Menu(self.ctx),
            GameScene(self.ctx),
            ResultScene(self.ctx),
            PauseScene(self.ctx),
            OptionsScene(self.ctx),
            ModesScene(self.ctx),
            CareerScene(self.ctx),
            AchievementsScene(self.ctx),
            ChallengeScene(self.ctx),
            RunHistoryScene(self.ctx),
            ThemesScene(self.ctx),
            JournalScene(self.ctx),
        ]

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    def run(self) -> None:
        cfg = self.ctx.cfg

        pyray.init_window(cfg.window_width, cfg.window_height, "Pacman")
        pyray.set_target_fps(cfg.fps)
        self.ctx.screen_flash.set_size(cfg.window_width, cfg.window_height)
        self.audio.initialize()

        self.current_scene_index = MENU_SCENE
        self.current_scene.enter_tree()
        self._sync_scene_audio()

        try:
            while not pyray.window_should_close():
                dt = pyray.get_frame_time()
                ui_theme.set_visual_theme(self.ctx.theme_name())
                if pyray.is_key_pressed(pyray.KEY_F10):
                    self.ctx.set_capture_mode_enabled(not self.ctx.capture_mode_enabled())

                self.current_scene.update(dt)
                self.audio.update(self.ctx)

                nxt = self.current_scene.consume_switch_request()
                if nxt is not None:
                    if nxt == EXIT_SCENE:
                        break
                    self.switch_scene(nxt)

                pyray.begin_drawing()
                pyray.clear_background(pyray.BLACK)
                self.current_scene.draw()
                pyray.end_drawing()

        finally:
            self.audio.shutdown()
            Assets.unload_all()
            pyray.close_window()

    def switch_scene(self, index: int) -> None:
        if index < 0 or index >= len(self.scenes):
            raise IndexError(f"Scene index out of range: {index}")

        self.current_scene.exit_tree()
        self.current_scene_index = index
        self.current_scene.enter_tree()
        self._sync_scene_audio()

    def _sync_scene_audio(self) -> None:
        scene_music = {
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
        }.get(self.current_scene_index, "menu")
        self.audio.set_scene_music(scene_music, self.ctx)


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
