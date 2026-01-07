import GlobalScope
from animated_sprite import Sprite
from cell import Cell
import ClassMap

import pyray
import time

import wall
import door

# Состояния пакмана
class State:
    UP = "UP"
    RIGHT = "RIGHT"
    DOWN = "DOWN"
    LEFT = "LEFT"
    DEAD = "DEATH"
    NONE = "NONE"

class Pacman(Cell):

    DEATH_FPS = 1
    def __init__(self):
        super().__init__()

        # Направление в начальном положение
        self.state = State.UP

        # В начале пакман спокоен
        self.rage = False

        self.rage_timer = 0

        self.death_timer = 0


        path = "sprites/pacman/"  # Путь для всех спрайтова пакмана

        # Состояния и анимации, а также, соотвествующие им, картинки
        pacman_image_paths = {
            "UP": [f"{path}pacman_pos_1_up.png", f"{path}pacman_pos_2_up.png"],
            "DOWN": [f"{path}pacman_pos_1_down.png", f"{path}pacman_pos_2_down.png"],
            "LEFT": [f"{path}pacman_pos_1_left.png", f"{path}pacman_pos_2_left.png"],
            "RIGHT": [f"{path}pacman_pos_1_right.png", f"{path}pacman_pos_2_right.png"],
            "DEATH": [f"{path}death/death_1.png", f"{path}death/death_2.png", f"{path}death/death_3.png",
                      f"{path}death/death_4.png", f"{path}death/death_5.png", f"{path}death/death_6.png",
                      f"{path}death/death_7.png", f"{path}death/death_8.png", f"{path}death/death_9.png",
                      f"{path}death/death_10.png"]
        }

        pacman_images = {}
        for key in pacman_image_paths:
            pacman_images[key] = []
            for path in pacman_image_paths[key]:
                pacman_images[key].append(pyray.load_texture(path))
        pacman_images["NONE"] = []

        # Спрайт пакмана
        self.pacman_sprite = Sprite(pacman_images)

        # Начальный вид пакмана
        self.pacman_sprite.set_key(self.state,True)


    # Отрисовка пакмана
    def draw(self):
        if self.state == State.NONE:
            return
        self.pacman_sprite.draw(pyray.Vector2(self.x * GlobalScope.RES, self.y * GlobalScope.RES))

    # Движение пакмана при каждом "тике"
    def process(self):
        if self.state == State.NONE:
            return
        # Проверка пакмана на смерть
        if self.state == State.DEAD:
            return

        if self.state == State.RIGHT:
            if self.x + 1 < len(GlobalScope.game_map.s_layer[self.y]):  # Проверка не выходит ли за границы массива(карты)
                if not isinstance(GlobalScope.game_map.s_layer[self.y][self.x+1], wall.Wall):  # Проверка нет ли стены
                    self.x += 1

        if self.state  == State.LEFT:
            if self.x - 1 > -1:  # Проверка не выходит ли за границы массива(карты)
                if not isinstance(GlobalScope.game_map.s_layer[self.y][self.x-1], wall.Wall):  # Проверка нет ли стены
                   self.x -= 1

        if self.state == State.UP:
            if self.y - 1 > -1:  # Проверка не выходит ли за границы массива(карты)
                if not isinstance(GlobalScope.game_map.s_layer[self.y-1][self.x], wall.Wall):  # Проверка нет ли стены
                    self.y -= 1

        if self.state == State.DOWN:
            if self.y + 1 < len(GlobalScope.game_map.s_layer):  # Проверка не выходит ли за границы массива(карты)
                if not isinstance(GlobalScope.game_map.s_layer[self.y+1][self.x], wall.Wall) and not(isinstance(GlobalScope.game_map.s_layer[self.y+1][self.x],door.Door)):
                    self.y += 1
        self.processed = True
        self.pacman_sprite.move_forward()

    # Обработка данных с клавиатуры
    def frame(self, x, y):
        super().frame(x, y)
        if self.state == State.NONE:
            return

        # Проверка пакмана на смерть
        if self.state == State.DEAD:
            if self.death_timer % Pacman.DEATH_FPS == 0:
                self.pacman_sprite.move_forward()
                if self.pacman_sprite.frame_index == len(self.pacman_sprite.texture_dictionary[self.state])-1:

                    self.state = State.NONE

            return

        self.rage_timer -= 1
        if self.rage_timer < 0:
            self.rage = False


        # Клавиши управления пакманом
        keys = {
            pyray.KeyboardKey.KEY_W: State.UP,
            pyray.KeyboardKey.KEY_A: State.LEFT,
            pyray.KeyboardKey.KEY_S: State.DOWN,
            pyray.KeyboardKey.KEY_D: State.RIGHT
        }

        # Изменение направления пакмана
        for key in keys:
            if pyray.is_key_pressed(key):
                self.state = keys[key]
                self.pacman_sprite.set_key(self.state,False)


