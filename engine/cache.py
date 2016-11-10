import pygame
from functools import lru_cache

def generate_checkers():
    s=pygame.Surface((1920,1080),pygame.HWSURFACE | pygame.SRCALPHA, 32)
    d=32
    b=96
    colors=[pygame.Color(b,b,b,255), pygame.Color(d,d,d,255)]
    dark=1
    for y in xrange(0,135):
        dark=1-dark
        for x in xrange(0,240):
            dark=1-dark
            pygame.draw.rect(s,colors[dark],pygame.Rect(x*8,y*8,8,8))
    return s
            

#EXPORT
@lru_cache(32)
def get_surface(filename):
    if filename=='checkers':
        s=generate_checkers()
    else:
        s=pygame.image.load(filename)
        s=s.convert_alpha()
    return s
