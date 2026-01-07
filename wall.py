import cell
import animated_sprite
import pyray
import GlobalScope
import ClassMap


class Wall(cell.Cell):
    def __init__(self):
        super().__init__()
        self.sprite = animated_sprite.Sprite({
            "00000000": [pyray.load_texture("sprites/walls/0/0000/wall_00000000.png")]
        })
        self.sprite.set_key("main",True)


    def draw(self):
        #                    Запись вида ######## означает:
        #                    0 - На этом месте нет стены
        #                    1 - На этом месте есть стена
        #
        #                    Расположение соседних стен:
        #
        #                            812
        #                            7■3
        #                            654

        _1, _2, _3, _4, _5, _6, _7, _8 = None, None, None, None, None, None, None, None

        # Base
        if self.x == 0:
            _6 = 0
            _7 = 0
            _8 = 0
        if self.x == GlobalScope.WIDTH-1:
            _2 = 0
            _3 = 0
            _4 = 0
        if self.y == 0:
            _1 = 0
            _2 = 0
            _8 = 0
        if self.y == GlobalScope.HEIGHT-1:
            _4 = 0
            _5 = 0
            _6 = 0

        # Other
        def processed_neighbour(var, sy, sx):
            if var is None:
                if isinstance(GlobalScope.game_map.s_layer[self.y+sy][self.x+sx],Wall):
                    var = 1
                else:
                    var = 0
            return var

        _1 = processed_neighbour(_1, -1, 0)
        _2 = processed_neighbour(_2, -1, 1)
        _3 = processed_neighbour(_3, 0, 1)
        _4 = processed_neighbour(_4, 1, 1)
        _5 = processed_neighbour(_5, 1, 0)
        _6 = processed_neighbour(_6, 1, -1)
        _7 = processed_neighbour(_7, 0, -1)
        _8 = processed_neighbour(_8, -1, -1)

        # Load
        _cars = _1 + _3 + _5 + _7  # cardinal sum
        _car = f"{_1}{_3}{_5}{_7}"  # just cardinals
        _all = f"{_1}{_2}{_3}{_4}{_5}{_6}{_7}{_8}"  # all

        if _all not in self.sprite.texture_dictionary:
            self.sprite.texture_dictionary[_all] = [
                pyray.load_texture(f"sprites/walls/{_cars}/{_car}/wall_{_all}.png")]

        # Draw
        self.sprite.draw_specified(_all, 0, pyray.Vector2(self.x * GlobalScope.RES, self.y * GlobalScope.RES))