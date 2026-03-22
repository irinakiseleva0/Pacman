# main.py
from __future__ import annotations

import pyray

from assets.assets import Assets
from core.context import GameContext, Config
from menu import Menu
from game_scene import GameScene


class Game:
    def __init__(self):
        self.ctx = GameContext(cfg=Config())
        self.ctx.game = self

        self.current_scene_index = 0
        self.scenes = [Menu(self.ctx), GameScene(self.ctx)]

    def _current_scene(self):
        return self.scenes[self.current_scene_index]

    def run(self):
        cfg = self.ctx.cfg
        pyray.init_window(self.ctx.cfg.window_width, self.ctx.cfg.window_height, "Pacman")
        pyray.set_target_fps(self.ctx.cfg.fps)


        self.current_scene_index = 0
        self._current_scene().enter_tree()

        try:
            while not pyray.window_should_close():
                dt = pyray.get_frame_time()

                # update
                self._current_scene().update(dt)

                # switch request
                nxt = self._current_scene().consume_switch_request()
                if nxt is not None:
                    if nxt == -1:
                        break
                    self.switch_scene(nxt)

                # draw
                pyray.begin_drawing()
                pyray.clear_background(pyray.BLACK)
                self._current_scene().draw()
                pyray.end_drawing()

        finally:
            Assets.unload_all()
            pyray.close_window()

    def switch_scene(self, index: int) -> None:
        if index < 0 or index >= len(self.scenes):
            raise IndexError(f"Scene index out of range: {index}")

        self._current_scene().exit_tree()
        self.current_scene_index = index
        self._current_scene().enter_tree()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
