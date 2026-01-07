import scene
import GlobalScope
from ClassMap import Map
import pyray
from raylib import colors

class GameScene(scene.Scene):
    def __init__(self):
        self.current_tick = 0
        self.tickrate = 0

    def enter_tree(self):
        self.current_tick = 0
        self.tickrate = 3
        GlobalScope.game_map = Map()

    def process(self):
        self.current_tick += 1

        # Кадр
        GlobalScope.game_map.frame()

        # Тик
        if self.current_tick % self.tickrate == 0:
            self.current_tick = 0

            GlobalScope.game_map.process()

        # Отрисовка
        pyray.begin_drawing()

        pyray.clear_background(colors.BLACK)

        GlobalScope.game_map.draw()

        pyray.end_drawing()
