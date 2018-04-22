#!/usr/bin/env python3
import sys
import oglblit
import random
import time
#import json
from engine import *
from engine.utils import vector2

sheet=None

class Blocker(Entity):
    def __init__(self):
        super(Blocker,self).__init__(load_json_file("blockers.json"))
        self.anim.set_active_sequence("b1")

class SmallMonster(Entity):
    def __init__(self,type=-1):
        super(SmallMonster,self).__init__(load_json_file("smalls.json"))
        self.alive = True
        if type<=0:
            type=random.randint(1,12)
        self.anim.set_active_sequence("m{}".format(type))

    def advance(self, dt):
        super(SmallMonster,self).advance(dt)
        return self.alive

    def get_type(self):
        return 'Monster'

class MonsterGroup(object):
    def __init__(self,scene):
        self.monsters=[]
        self.dir=1
        for row in range(0,5):
            for col in range(0,10):
                m=SmallMonster()
                m.set_position(64*col+10,64*row+10)
                m.set_velocity(16.0,0.0)
                self.monsters.append(m)
                scene.add(m)

    def step_down(self):
        self.dir=-self.dir
        for m in self.monsters:
            m.set_position(m.get_position()+vector2(0,10))
            m.set_velocity(-m.get_velocity().scaled(1.1))

    def advance(self,dt):
        for m in self.monsters:
            if m.alive:
                if self.dir>0 and m.get_position().x > 760:
                    self.step_down()
                    break
                if self.dir<0 and m.get_position().x < 10:
                    self.step_down()
                    break

class Missile(Entity):
    def __init__(self):
        super(Missile,self).__init__(load_json_file("missile.json"))
        self.alive=True

    def advance(self, dt):
        super(Missile,self).advance(dt)
        return self.alive

    def collision(self,other,col_pt):
        self.alive = False
        if other.get_type()=='Monster':
            other.alive=False



class Ship(Entity):
    def __init__(self,scene):
        super(Ship,self).__init__(load_json_file("ship.json"))
        self.set_position(10,550)
        self.anim.set_active_sequence("ship")
        self.scene = scene
        self.last_shoot = -100.0

    def set_keys(self,keys):
        vx=0
        if KeyCodes['RIGHT'] in keys:
            vx+=250
        if KeyCodes['LEFT'] in keys:
            vx-=250
        if KeyCodes['SPACE'] in keys:
            cur = time.time()
            if (cur-self.last_shoot)>0.5:
                self.last_shoot=cur
                m=Missile()
                m.set_position(self.get_position()+vector2(10,-30))
                m.set_velocity(0,-300)
                self.scene.add(m)
        self.set_velocity(vx,0)

    def advance(self, dt):
        super(Ship,self).advance(dt)
        p=self.get_position()
        if p.x>750:
            self.set_position(750,p.y)
        if p.x<10:
            self.set_position(10,p.y)
        return True

class Game(Application):
    def __init__(self):
        super(Game,self).__init__(res=(1200,900), scale=1.5)
        self.keys=[]
        global sheet
        sheet = oglblit.load_sprites('tinvader.png')
        self.scene=Scene()
        self.space = load_json_file("space.json")
        self.view=View()
        for i in range(0,5):
            b=Blocker()
            b.set_position(i*150+75,500)
            self.scene.add(b)
        self.monster_group=MonsterGroup(self.scene)
        self.ship = Ship(self.scene)
        self.scene.add(self.ship)

    def loop(self,dt):
        #dt=0.01
        self.ship.set_keys(self.keys)
        self.scene.advance(dt)
        self.monster_group.advance(dt)
        vy=self.view.get_position().y
        #self.view.set_position(vector2(self.boy.get_position().x-300,vy))
        self.draw()
        return True

    def draw(self):
        self.space.draw(vector2(0,0))
        self.scene.draw(self.view)
        time.sleep(0.01)

def main():
    game=Game()
    game.run()

if __name__=='__main__':
    main()
