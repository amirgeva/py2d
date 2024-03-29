import sys
from engine import *
from engine.utils import vector2

class Walker(Entity):
    def __init__(self,spr_filename):
        super().__init__(load_file(spr_filename))
        self.set_acceleration(0, 200)
        self.onground=0

    def collision(self,other,col_pt):
        y=col_pt.y
        h=self.anim.get_current_height()
        v=self.get_velocity()
        if y>(h-8) and v.y>0:
            self.set_position(self._position.x, self._previous_position.y - (h - 1 - y))
            self.set_velocity(self._velocity.x, 0.0)
            self.onground=3
            
    def get_external_force(self):
        v=self.get_velocity().x
        if self.onground>0:
            return vector2(-2.5*v,0)
        return vector2(-0.1*v,0)

    def advance(self,dt):
        self.onground-=1
        acc=self.get_acceleration()
        v=self.get_velocity()
        # if self.onground>0:
        #     acc.x-=v.x**2
        self.set_acceleration(acc.x, acc.y)
        if v.x>10:
            self.anim.set_active_sequence('right')
        elif v.x<-10:
            self.anim.set_active_sequence('left')
        elif self.anim.get_active_sequence_name()[0]!='s':
            s='sleft' if v.x<0 else 'sright'
            self.anim.set_active_sequence(s)
            if abs(acc.x)<20:
                self.set_velocity(0.0,v.y)
        return super().advance(dt)

