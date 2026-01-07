import GlobalScope
import pyray
from game_scene import *
from menu import *

class Game:
    def __init__(self):
        self.current_scene_index = 0
        self.scenes = []
        GlobalScope.game = self

    def main(self):
        pyray.set_target_fps(GlobalScope.FPS)

        pyray.init_window(GlobalScope.WINDOW_WIDTH, GlobalScope.WINDOW_HEIGHT, "Pacman")

        self.scenes.append(Menu())
        self.scenes.append(GameScene())

        self.scenes[self.current_scene_index].enter_tree()

        while not pyray.window_should_close():
            self.scenes[self.current_scene_index].process()

        pyray.close_window()

    def switch_scene(self,index):
        self.scenes[self.current_scene_index].exit_tree()
        self.current_scene_index = index
        self.scenes[self.current_scene_index].enter_tree()


if __name__ == "__main__":
    game = Game()
    game.main()