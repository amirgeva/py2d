import pygame
import itertools

def same_rect(r1,r2):
    return r1.left==r2.left and r1.top==r2.top and r1.right==r2.right and r1.bottom==r2.bottom

def format_rect(r):
    return "{},{},{},{}".format(r.x,r.y,r.x+r.w,r.y+r.h)

def parse_rect(s):
    try:
        c=s.split(',')
        x0=int(c[0])
        y0=int(c[1])
        x1=int(c[2])
        y1=int(c[3])
        return pygame.Rect(x0,y0,x1-x0,y1-y0)
    except ValueError:
        return pygame.Rect(0,0,1,1)
    
def parse_float(s):
    try:
        return float(s)
    except ValueError:
        return 0.0

#EXPORT
def is_transparent(s):
    w=s.get_width()
    h=s.get_height()
    for y in xrange(0,h):
        for x in xrange(0,w):
            c=s.get_at((x,y))
            if c.a < 255:
                return True
    return False
    
#EXPORT
def parse_point(s):
    c=s.split(',')
    return (int(c[0]),int(c[1]))
    
#EXPORT
def parse_color(s):
    c=s.split(',')
    a=255
    if len(c)>3:
        a=int(c[3])
    return pygame.Color(int(c[0]),int(c[1]),int(c[2]),a)
    
#EXPORT
def all_pixels(s):
    return itertools.product(xrange(0,s.get_width()),xrange(0,s.get_height()))
    