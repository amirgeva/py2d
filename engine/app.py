import pygame
from pygame.locals import *

#EXPORT
class Application(object):
    def __init__(self,res=(640,480)):
        pygame.init()
        self.screen=pygame.display.set_mode(res, DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps=30

    def calc_dt(self):
        return 0.001*self.clock.tick(self.fps)        
        
    def flip(self):
        pygame.display.flip()

    def clear(self,color=(192,128,255)):
        self.screen.fill(color)
        
    def onKey(self,key):
        pass
    
    def onClick(self,pos):
        pass

    def handleEvents(self):
        for event in pygame.event.get():
            if hasattr(event, 'key'):
                if event.key == K_ESCAPE:
                    return False
                else:
                    if event.type==2:
                        self.onKey(event.key)
            elif event.type==pygame.MOUSEBUTTONDOWN:
                self.onClick(event.pos)
            #elif hasattr(event,)
        return True
        
    def loop(self,dt):
        pass
        
    def run(self):
        while self.handleEvents():
            self.loop(self.calc_dt())
            self.flip()
