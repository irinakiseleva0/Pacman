import GlobalScope
import pyray
from raylib import colors
import cell
import Pacman
class Seed(cell.Cell):
    def __init__(self):
        super().__init__()

        self.image = pyray.load_texture("sprites/consumables/small_dot.png")
        self.enabled = 1

    def draw(self):
        if self.enabled == 1:

            pyray.draw_texture_ex(self.image, pyray.Vector2(self.x * GlobalScope.RES, self.y * GlobalScope.RES), 0, 1, colors.WHITE)

    def process(self):

        if GlobalScope.pacman.x == self.x and GlobalScope.pacman.y == self.y:
            if self.enabled == 1:
                self.enabled = 0
                GlobalScope.score += 50


class LargeSeed(Seed):
    def __init__(self):
        super().__init__()
        self.image = pyray.load_texture("sprites/consumables/big_dot.png")
    def process(self):
        if GlobalScope.pacman.x == self.x and  GlobalScope.pacman.y == self.y:
            if self.enabled == 1:
                self.enabled = 0
                GlobalScope.score += 100
                GlobalScope.pacman.rage = 1
                GlobalScope.pacman.rage_timer = 10
