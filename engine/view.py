from engine.utils import Rect


# EXPORT
class View(object):
    def __init__(self, target, rect=None):
        self.target = target
        if rect:
            self.rect = rect
        else:
            self.rect = target.get_rect()

    def offset(self, d):
        self.rect.move_ip(d[0], d[1])

    def get_position(self):
        return self.rect.topleft

    def set_position(self, pos):
        self.rect = Rect(pos.x, pos.y, self.rect.width, self.rect.height)

    def relative_position(self, pos):
        return pos - self.rect.topleft

    def get_rect(self):
        return self.rect
