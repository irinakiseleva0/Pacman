from __future__ import annotations

import core.raylib_api as pyray
import ui.ui as ui_theme

from assets.assets import Assets
from core.context import GameContext
from core.scene_ids import EXIT_SCENE, MENU_SCENE
from scenes.registry import SCENE_MUSIC, build_scene_table
from ui.layout import DEFAULT_LAYOUT
from utils.audio_manager import AudioManager


class Game:
    def __init__(self) -> None:
        self.ctx = GameContext()
        self.ctx.apply_layout(DEFAULT_LAYOUT)
        self.audio = AudioManager()
        self.ctx.audio_manager = self.audio

        self.current_scene_index = MENU_SCENE
        self.scenes = build_scene_table(self.ctx)

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
        if index not in self.scenes:
            raise IndexError(f"Scene index out of range: {index}")

        self.current_scene.exit_tree()
        self.current_scene_index = index
        self.current_scene.enter_tree()
        self._sync_scene_audio()

    def _sync_scene_audio(self) -> None:
        scene_music = SCENE_MUSIC.get(self.current_scene_index, "menu")
        self.audio.set_scene_music(scene_music, self.ctx)


def main() -> None:
    Game().run()



if __name__ == "__main__":
    main()
