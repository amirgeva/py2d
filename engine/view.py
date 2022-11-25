from engine.utils import Rect, build_point
from engine.app import get_screen_size


# EXPORT
class View:
    def __init__(self, rect=None):
        if rect:
            self.rect = rect
        else:
            res = get_screen_size()
            self.rect = Rect(0, 0, res[0], res[1])

    def offset(self, *args):
        self.rect.move(build_point(*args))

    def get_position(self):
        return self.rect.tl

    def set_position(self, *args):
        pos = build_point(*args)
        self.rect = Rect(pos.x, pos.y, pos.x + self.rect.width(), pos.y + self.rect.height())

    def relative_position(self, *args):
        pos = build_point(*args)
        return pos - self.rect.tl

    def get_rect(self):
        return Rect(self.rect)
