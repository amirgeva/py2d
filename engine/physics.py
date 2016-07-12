from pygame.math import Vector2

#EXPORT
class RigidBody(object):
    def __init__(self):
        self.accel=Vector2(0.0,0.0)
        self.velocity=Vector2(0.0,0.0)
        self.position=Vector2(0.0,0.0)
        self.prepos=Vector2(0.0,0.0)

    def advance(self,dt):
        self.velocity+=dt*self.accel
        self.prepos=self.position
        self.position=self.position+dt*self.velocity
        
    def get_position(self):
        return Vector2(int(self.position.x),int(self.position.y))
        
    def set_position(self,x,y):
        self.position=Vector2(x,y)
        
    def set_velocity(self,vx,vy):
        self.velocity=Vector2(vx,vy)
        
    def set_accel(self,ax,ay):
        self.accel=Vector2(ax,ay)
        
        