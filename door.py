import cell
import animated_sprite
import pyray
import GlobalScope

class Door(cell.Cell):
    def __init__(self):
        super().__init__()
        self.sprite = animated_sprite.Sprite({
            "door": [pyray.load_texture("sprites/walls/ghost_door_full.png")]
        })
        self.sprite.set_key("main", True)

    def draw(self):
        self.sprite.draw_specified("door", 0, pyray.Vector2(self.x * GlobalScope.RES, self.y * GlobalScope.RES))

