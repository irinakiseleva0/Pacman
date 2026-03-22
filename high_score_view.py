import pyray
from raylib import colors


SCORES_PATH = "scores.txt"
WINDOW_W = 500
WINDOW_H = 600
FPS = 30


class HighscoreTableDraw:
    def table_draw(self):
        pyray.init_window(WINDOW_W, WINDOW_H, "Highscore Table")
        pyray.set_target_fps(FPS)

        try:
            with open(SCORES_PATH, "r", encoding="utf-8") as file:
                data = file.read().strip()
        except FileNotFoundError:
            data = "No scores yet.\nPlay the game to create scores.txt"

        while not pyray.window_should_close():
            x, y = 50, 100

            pyray.begin_drawing()
            pyray.clear_background(colors.WHITE)

            pyray.draw_text("Best Results", 120, 29, 40, colors.BLACK)
            pyray.draw_text(data, x, y, 30, colors.BLACK)

            pyray.end_drawing()

        pyray.close_window()


def main():
    view = HighscoreTableDraw()
    view.table_draw()


if __name__ == "__main__":
    main()
