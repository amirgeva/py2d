import pygame

def same_rect(r1,r2):
    return r1.left==r2.left and r1.top==r2.top and r1.right==r2.right and r1.bottom==r2.bottom

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