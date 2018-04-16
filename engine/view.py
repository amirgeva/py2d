import pygame

#EXPORT
class View(object):
    def __init__(self,target,rect=None):
        self.target=target
        if rect:
            self.rect=rect
        else:
            self.rect=target.get_rect()
        
    def offset(self,d):
        self.rect.move_ip(d.x,d.y)
        
    def set_position(self,pos):
        self.rect=pygame.Rect(pos.x,pos.y,self.rect.width,self.rect.height)
        
    def relative_position(self,pos):
        return pos-self.rect.topleft
        
    def get_rect(self):
        return self.rect
