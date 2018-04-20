import engine.sprite
from engine.physics import RigidBody

ids = 0


def generate_id():
    global ids
    ids += 1
    return ids


# EXPORT
class Entity(RigidBody):
    def __init__(self, anim):
        super(Entity, self).__init__()
        self.anim = anim
        self.id = generate_id()
        self.dynamic = True

    def get_type(self):
        return 'Entity'

    def is_dynamic(self):
        return self.dynamic

    def advance(self, dt):
        super(Entity, self).advance(dt)
        self.anim.advance(dt, self.velocity)
        return True

    def draw(self, view):
        self.anim.draw(view.relative_position(self.get_position()))

    def get_rect(self):
        r = self.anim.get_rect()
        ofs = self.get_position()
        r.move(ofs)
        return r

    def get_id(self):
        return self.id

    def collision(self, other, col_point):
        pass
