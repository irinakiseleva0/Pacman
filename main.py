from __future__ import annotations

import pyray

from assets.assets import Assets
from core.context import GameContext
from core.scene_ids import EXIT_SCENE, GAME_SCENE, MENU_SCENE, PAUSE_SCENE, RESULT_SCENE
from menu import Menu
from game_scene import GameScene
from result_scene import ResultScene
from pause_scene import PauseScene


class Game:
    def __init__(self) -> None:
        self.ctx = GameContext()

        self.current_scene_index = MENU_SCENE
        self.scenes = [
            Menu(self.ctx),
            GameScene(self.ctx),
            ResultScene(self.ctx),
            PauseScene(self.ctx),
        ]

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    def run(self) -> None:
        cfg = self.ctx.cfg

        pyray.init_window(cfg.window_width, cfg.window_height, "Pacman")
        pyray.set_target_fps(cfg.fps)

        self.current_scene_index = MENU_SCENE
        self.current_scene.enter_tree()

        try:
            while not pyray.window_should_close():
                dt = pyray.get_frame_time()

                self.current_scene.update(dt)

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
            Assets.unload_all()
            pyray.close_window()

    def switch_scene(self, index: int) -> None:
        if index < 0 or index >= len(self.scenes):
            raise IndexError(f"Scene index out of range: {index}")

        self.current_scene.exit_tree()
        self.current_scene_index = index
        self.current_scene.enter_tree()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
