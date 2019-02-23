import pygame
from engine.utils import Rect
from engine.app import get_screen_size

# EXPORT
class View(object):
    def __init__(self, rect=None):
        if rect:
            self.rect = rect
        else:
            res = get_screen_size()
            self.rect = Rect(0,0,res[0],res[1])

    def offset(self, d):
        self.rect.move(d[0], d[1])

    def get_position(self):
        return self.rect.tl

    def set_position(self, pos):
        self.rect = Rect(pos.x, pos.y, pos.x+self.rect.width(), pos.y+self.rect.height())

    def relative_position(self, pos):
        return pos - self.rect.tl

    def get_rect(self):
        return Rect(self.rect)
