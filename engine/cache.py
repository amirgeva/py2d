import pygame

surfaces={}

def get_surface(filename):
    if filename in surfaces:
        return surfaces.get(filename)
    s=pygame.image.load(filename)
    s=s.convert_alpha()
    surfaces[filename]=s
    return s
