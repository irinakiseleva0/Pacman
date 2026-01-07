import GlobalScope
import pyray
from raylib import colors
import cell
import Pacman
from seeds import Seed

class Cherry(Seed):
    def __init__(self):
        super().__init__()
        self.respawn_time = 0
        self.image = pyray.load_texture("sprites/consumables/cherry.png")

    def process(self):
        if GlobalScope.pacman.x == self.x and GlobalScope.pacman.y == self.y:
            if self.enabled == 1:
                self.enabled = 0
                GlobalScope.score += 500
                self.respawn_time = 150

        if self.respawn_time > 0:
            self.respawn_time -= 1
        if self.respawn_time == 0:
            self.enabled = 1

