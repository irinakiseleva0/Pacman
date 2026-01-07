import pyray

class HighscoreTableDraw:
    def TableDraw(self):
        pyray.init_window(500, 600, "Highscore Table")
        pyray.set_target_fps(10)
        with open('scores.txt', 'r') as file:
            data = file.read().replace('', '')

        while not pyray.window_should_close():
            x = 50
            y = 100
            pyray.begin_drawing()
            pyray.clear_background(pyray.WHITE)
            pyray.draw_text("Best Results", 120, 29, 40, pyray.BLACK)
            pyray.draw_text(data, x, y, 30, pyray.BLACK)
            pyray.end_drawing()
        pyray.close_window()

def main():
    pacman = HighscoreTableDraw()
    pacman.TableDraw()

if __name__ == '__main__':
    main()
