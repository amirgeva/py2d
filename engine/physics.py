from engine.utils import vector2


# EXPORT
class RigidBody(object):
    def __init__(self):
        self._acceleration = vector2(0.0, 0.0)
        self._velocity = vector2(0.0, 0.0)
        self._position = vector2(0.0, 0.0)
        self._previous_position = vector2(0.0, 0.0)

    def get_external_force(self):
        return vector2(0, 0)

    def advance(self, dt):
        self._previous_position = self._position
        self._position = self._position + self._velocity.scaled(dt)
        self._velocity += (self._acceleration + self.get_external_force()).scaled(dt)

    def get_position(self):
        return vector2(int(self._position.x), int(self._position.y))

    def set_position(self, *args):
        self._position = vector2(*args)

    def get_velocity(self):
        return vector2(self._velocity.x, self._velocity.y)

    def set_velocity(self, *args):
        self._velocity = vector2(*args)

    def get_acceleration(self):
        return vector2(self._acceleration.x, self._acceleration.y)

    def set_acceleration(self, ax, ay):
        self._acceleration = vector2(ax, ay)
