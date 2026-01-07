from pyray import draw_texture_ex
from raylib import colors


class Sprite:
    def __init__(self, texture_dictionary={}):
        self.texture_dictionary = texture_dictionary
        self.current_key = ""
        self.frame_index = 0

    # Получение текстуры на основании текущей анимации и кадра
    def get_texture(self):
        return self.texture_dictionary[self.current_key][self.frame_index]

    # Отрисовка, совать в draw функцию клетки
    def draw(self, position, rotation=0.0, scale=1.0):
        draw_texture_ex(self.get_texture(), position, rotation, scale, colors.WHITE)

    def draw_specified(self,key,frame,position,rotation=0,scale=1):
        draw_texture_ex(self.texture_dictionary[key][frame], position, rotation, scale, colors.WHITE)

    # Получить следующий кадр анимации, совать в process функцию клетку по надобности
    def move_forward(self):
        self.frame_index = (self.frame_index + 1) % len(self.texture_dictionary[self.current_key])

    # Добавить анимацию, обязательно массив
    def add_animation(self, key, frames):
        self.texture_dictionary[key] = frames

    # Изменить текущую анимацию с возможностью сбросить текущий кадр
    def set_key(self, key, reset_index):
        if reset_index:
            self.frame_index = 0
        self.current_key = key
