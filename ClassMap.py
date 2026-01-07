import GlobalScope
import Pacman
from cell import *
from wall import *
from Pacman import *
from door import *
from Teleport import *
from seeds import *
from cherry import *
class Map:

    # Для сокращения затрат памяти
    empty = Cell()

    def __init__(self):
        self.s_layer = []
        self.dynamic_cells = []

        self.load("pacman_map.txt")

    def load(self, path):
        file = open(path)
        self.s_layer.clear()
        self.dynamic_cells.clear()

        file_lines = file.readlines()

        for y in range(len(file_lines)):
            s_layer_strip = []

            for x in range(len(file_lines[y])):
                cell = None
                if file_lines[y][x] == '#':
                    cell = Wall()
                elif file_lines[y][x] == 't':
                    cell = Teleport()
                elif file_lines[y][x] == 'd':
                    cell = Door()
                elif file_lines[y][x] == 's':
                    cell = LargeSeed()
                elif file_lines[y][x] == '.':
                    cell = Seed()
                elif file_lines[y][x] == 'c':
                    cell = Cherry()
                else:
                    cell = Map.empty

                if file_lines[y][x] == "\n":
                    continue

                cell.x = x
                cell.y = y

                s_layer_strip.append(cell)

                if file_lines[y][x] == "p":
                    pacman = Pacman.Pacman()
                    GlobalScope.pacman = pacman
                    pacman.x, pacman.y = x, y
                    self.dynamic_cells.append(pacman)
                elif file_lines[y][x] == "g":
                    ghost = Map.empty
                    ghost.x, ghost.y = x, y
                    self.dynamic_cells.append(ghost)

            self.s_layer.append(s_layer_strip)

        file.close()



    def reset_processed(self):
        for dynamic in self.dynamic_cells:
            dynamic.processed = False

        for y in range(len(self.s_layer)):
            for x in range(len(self.s_layer[y])):
                self.s_layer[y][x].processed = False


    def draw(self):
        for y in range(len(self.s_layer)):
            for x in range(len(self.s_layer[y])):
                self.s_layer[y][x].draw()

        for dynamic in self.dynamic_cells:
            dynamic.draw()


    def process(self):
        for dynamic in self.dynamic_cells:
            dynamic.process()
            dynamic.processed = True
        self.reset_processed()

        for y in range(len(self.s_layer)):
            for x in range(len(self.s_layer[y])):
                if not self.s_layer[y][x].processed:
                    self.s_layer[y][x].process()
                    self.s_layer[y][x].processed = True

    def frame(self):
        for dynamic in self.dynamic_cells:
            x = dynamic.x % GlobalScope.WIDTH
            y = dynamic.y % GlobalScope.HEIGHT
            dynamic.frame(x, y)

        for y in range(len(self.s_layer)):
            for x in range(len(self.s_layer[y])):
                self.s_layer[y][x].frame(x, y)
