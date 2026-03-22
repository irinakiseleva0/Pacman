from __future__ import annotations

import pyray

from assets.assets import Assets
from core.context import GameContext
from menu import Menu
from game_scene import GameScene
from result_scene import ResultScene


class Game:
    def __init__(self) -> None:
        self.ctx = GameContext()

        self.current_scene_index = 0
        self.scenes = [
            Menu(self.ctx),         # 0
            GameScene(self.ctx),    # 1
            ResultScene(self.ctx),  # 2
        ]

    @property
    def current_scene(self):
        return self.scenes[self.current_scene_index]

    def run(self) -> None:
        cfg = self.ctx.cfg

        pyray.init_window(cfg.window_width, cfg.window_height, "Pacman")
        pyray.set_target_fps(cfg.fps)

        self.current_scene_index = 0
        self.current_scene.enter_tree()

        try:
            while not pyray.window_should_close():
                dt = pyray.get_frame_time()

                self.current_scene.update(dt)

                nxt = self.current_scene.consume_switch_request()
                if nxt is not None:
                    if nxt == -1:
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