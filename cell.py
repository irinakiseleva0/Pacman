class Cell:
    def __init__(self):
        self.processed = False
        self.x = 0
        self.y = 0

    def start(self):
        pass

    # Метод, вызываемый когда игра совершает "тик"
    def process(self):
        pass

    # Метод, вызываемый когда игра запрашивает отрисовку у объекта. Вызывается после "тика"
    def draw(self):
        pass

    # Метод, вызываемый каждый кадр
    def frame(self, x, y):
        self.x = x
        self.y = y
