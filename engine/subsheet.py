import pygame
from engine.utils import Rect


class Subsheet:
    def __init__(self, surface: pygame.Surface, rect: Rect):
        self.surface = surface
        self.rect = rect

    def width(self):
        return self.rect.width()

    def height(self):
        return self.rect.height()

    def blit(self, target, pos):
        target.blit(self.surface, pos.as_tuple(), self.rect.as_tuple())
