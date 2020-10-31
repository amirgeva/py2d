import pygame


class Subsheet:
    def __init__(self, surface, rect):
        self.surface = surface
        self.rect = rect

    def width(self):
        return self.rect.width()

    def height(self):
        return self.rect.height()

    def blit(self, target, pos):
        target.blit(self.surface, pos.as_tuple(), self.rect.as_tuple())
