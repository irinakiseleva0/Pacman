import core.raylib_api as pyray
from raylib import colors

from utils.score_storage import SCORE_FILE, load_high_score

WINDOW_W = 500
WINDOW_H = 600
FPS = 30


class HighscoreTableDraw:
    def table_draw(self):
        pyray.init_window(WINDOW_W, WINDOW_H, "Highscore Table")
        pyray.set_target_fps(FPS)

        high_score = load_high_score()
        if SCORE_FILE.exists():
            data = f"High score\n\n{high_score}"
        else:
            data = "No scores yet.\nPlay the game to create scores.json"

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
