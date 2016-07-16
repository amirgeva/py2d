import pygame


def swapRB(surface):
    w=surface.get_width()
    h=surface.get_height()
    for y in xrange(0,h):
        for x in xrange(0,w):
            p=surface.get_at((x,y))
            s=pygame.Color(p.b,p.g,p.r,p.a)
            surface.set_at((x,y),s)

def generateBackground(size):
    s=pygame.Surface(size)
    w=s.get_width()
    h=s.get_height()
    for y in xrange(0,h):
        iy=(y/8)&1
        for x in xrange(0,w):
            ix=(x/8)&1
            g=192 if ix==iy else 128
            s.set_at((x,y),pygame.Color(g,g,g,255))
    return s
    