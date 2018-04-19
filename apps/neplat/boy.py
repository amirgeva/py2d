import sys
sys.path.append('../..')
#sys.path.append('.')
from engine import *
import pygame
from pygame.math import Vector2
from walker import Walker

class Boy(Walker):
    def __init__(self):
        super(Boy,self).__init__('boy.json')
        self.anim.set_active_sequence('sright')
        self.alive=True
        
    def advance(self,dt):
        if self.get_position().y>500:
            return False
        return super(Boy,self).advance(dt)
        
    def collision(self,other,col_pt):
        if other.get_type()=='Monster':
            self.alive=False
        if self.alive:
            return super(Boy,self).collision(other,col_pt)
        
    def set_keys(self,keys):
        acc=self.get_accel()
        v=self.get_velocity()
        if self.onground>0:
            if keys[pygame.K_RIGHT]:
                acc.x=150
            elif keys[pygame.K_LEFT]:
                acc.x=-150
            else:
                acc.x=0
        else:
            acc.x=0
        if keys[pygame.K_UP] and self.onground>0:
            self.set_velocity(v.x,-136)
        self.set_accel(acc.x,acc.y)
            