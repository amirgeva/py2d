from engine.utils import vector2


# EXPORT
class RigidBody(object):
    def __init__(self):
        self.accel = vector2(0.0, 0.0)
        self.velocity = vector2(0.0, 0.0)
        self.position = vector2(0.0, 0.0)
        self.prepos = vector2(0.0, 0.0)

    def get_external_force(self):
        return vector2(0, 0)

    def advance(self, dt):
        self.prepos = self.position
        self.position = self.position + self.velocity.scaled(dt)
        self.velocity += (self.accel + self.get_external_force()).scaled(dt)

    def get_position(self):
        return vector2(int(self.position.x), int(self.position.y))

    def set_position(self, x, y):
        self.position = vector2(x, y)

    def get_velocity(self):
        return vector2(self.velocity.x, self.velocity.y)

    def set_velocity(self, vx, vy):
        self.velocity = vector2(vx, vy)

    def get_accel(self):
        return vector2(self.accel.x, self.accel.y)

    def set_accel(self, ax, ay):
        self.accel = vector2(ax, ay)
