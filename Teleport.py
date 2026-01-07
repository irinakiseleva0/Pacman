import GlobalScope
import cell
import ClassMap
import Pacman

class Teleport(cell.Cell):
    def tp(self, x, pacman):
        if x == 0:
            pacman.x = 26

        elif x == 27:

            pacman.x = 1



    def process(self):
        if GlobalScope.pacman.x == self.x and GlobalScope.pacman.y == self.y:
            self.tp(self.x, GlobalScope.pacman)

