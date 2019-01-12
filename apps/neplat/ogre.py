import sys
from engine import *
from engine.utils import vector2
from walker import Walker


class Ogre(Walker):
    def __init__(self,mn,mx,v):
        super(Ogre,self).__init__('ogre.json')
        self.anim.set_active_sequence('right')
        self.range=(mn,mx)
        self.v=v
        self.set_velocity(self.v,0)
        
    def get_type(self):
        return 'Monster'
        
    def get_external_force(self):
        return vector2(0,0)
        
    def advance(self,dt):
        a=self.get_accel()
        p=self.get_position()
        v=self.get_velocity()
        if p.x>=self.range[1] and v.x>0:
            self.set_velocity(-self.v,0)
        elif p.x<=self.range[0] and v.x<0:
            self.set_velocity(self.v,0)
        return super(Ogre,self).advance(dt)
        
        
    
    
        
