import datetime

import pyray

import GlobalScope
import scene
from raylib import colors

class Menu(scene.Scene):
    def __init__(self):
        self.scene_0_button_new_geometry = None
        self.scene_0_button_exit_geometry = None

        self.background_color = colors.BLACK
    def enter_tree(self):
        # Инициализация сцены 0 (menu)
        self.scene_0_button_new_geometry = pyray.Rectangle(GlobalScope.WINDOW_WIDTH / 2 - 100 / 2, GlobalScope.WINDOW_HEIGHT / 2 - 10 - 50, 100, 50)
        self.scene_0_button_exit_geometry = pyray.Rectangle(GlobalScope.WINDOW_WIDTH / 2 - 100 / 2, GlobalScope.WINDOW_HEIGHT / 2 + 10, 100, 50)

    def process(self):

        pyray.begin_drawing()

        if pyray.gui_button(self.scene_0_button_new_geometry, 'INSERT COIN'):
            GlobalScope.game.switch_scene(1)
        if pyray.gui_button(self.scene_0_button_exit_geometry, 'PERISH'):
            pyray.close_window()

        pyray.end_drawing()