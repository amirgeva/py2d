import sys
from engine import *
from engine.utils import vector2
from walker import Walker


class Boy(Walker):
    def __init__(self):
        super().__init__('boy.json')
        self.anim.set_active_sequence('sright')
        self.alive = True

    def advance(self, dt):
        self.handle_keys()
        if self.get_position().y > 500:
            return False
        return super().advance(dt)

    def collision(self, other, col_pt):
        if other.get_type() == 'Monster':
            self.alive = False
        if self.alive:
            return super().collision(other, col_pt)

    def handle_keys(self):
        acc = self.get_acceleration()
        v = self.get_velocity()
        if self.onground > 0:
            if key_down('RIGHT'):
                acc.x = 350
            elif key_down('LEFT'):
                acc.x = -350
            else:
                acc.x = 0
        else:
            acc.x = 0
        if key_down('UP') and self.onground > 0:
            self.set_velocity(v.x, -220)
        self.set_acceleration(acc.x, acc.y)
