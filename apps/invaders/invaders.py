#!/usr/bin/env python3
import sys
import pygame
import random
import time
# import json
from engine import *
from engine.utils import vector2

sheet = None


class Blocker(Entity):
    def __init__(self):
        super().__init__(load_json_file("blockers.json"))
        self.anim.set_active_sequence("b1")

    def get_type(self):
        return 'Block'


class Bomb(Entity):
    def __init__(self):
        super().__init__(load_json_file("bomb.json"))
        self.alive = True
        self.set_velocity(0, 80)
        self.set_acceleration(0, 50)

    def advance(self, dt):
        super().advance(dt)
        if self.get_position().y > 1000:
            self.alive = False
        return self.alive

    def collision(self, other, col_pt):
        if other.get_type() == 'Monster':
            return
        self.alive = False


class Missile(Entity):
    def __init__(self):
        super().__init__(load_json_file("missile.json"))
        self.alive = True

    def get_type(self):
        return "Missile"

    def advance(self, dt):
        super().advance(dt)
        if self.get_position().y < -100:
            self.alive = False
        return self.alive

    def collision(self, other, col_pt):
        self.alive = False


class SmallMonster(Entity):
    def __init__(self, type=-1):
        super().__init__(load_json_file("smalls.json"))
        self.alive = True
        if type <= 0:
            type = random.randint(1, 12)
        self.anim.set_active_sequence("m{}".format(type))
        self.group = None

    def advance(self, dt):
        super().advance(dt)
        return self.alive

    def get_type(self):
        return 'Monster'

    def collision(self, other, col_pt):
        if other.get_type() == 'Missile':
            self.alive = False
            if self.group:
                self.group.died(self)


class MonsterGroup(object):
    def __init__(self, scene):
        self.monsters = []
        self.scene = scene
        self.dir = 1
        for row in range(0, 5):
            for col in range(0, 10):
                m = SmallMonster()
                m.set_position(64 * col + 10, 64 * row + 10)
                m.set_velocity(16.0, 0.0)
                m.group = self
                self.monsters.append(m)
                scene.add(m)

    def step_down(self):
        self.dir = -self.dir
        for m in self.monsters:
            m.set_position(m.get_position() + vector2(0, 10))
            m.set_velocity(-m.get_velocity().scaled(1.2))

    def died(self, m):
        for m in self.monsters:
            m.set_velocity(m.get_velocity().scaled(1.05))

    def advance(self, dt):
        for m in self.monsters:
            if m.alive:
                if self.dir > 0 and m.get_position().x > 760:
                    self.step_down()
                    break
                if self.dir < 0 and m.get_position().x < 10:
                    self.step_down()
                    break
                if random.random() < 0.001:
                    b = Bomb()
                    b.set_position(m.get_position() + vector2(0, 30))
                    self.scene.add(b)


class Ship(Entity):
    def __init__(self, scene):
        super().__init__(load_json_file("ship.json"))
        self.set_position(10, 550)
        self.anim.set_active_sequence("ship")
        self.scene = scene
        self.last_shoot = -100.0
        # self.shoot_sound = oglblit.load_audio('wa.wav')

    def get_type(self):
        return 'Ship'

    def handle_keys(self):
        vx = 0
        if key_down('RIGHT'):
            vx += 250
        if key_down('LEFT'):
            vx -= 250
        if key_down('SPACE'):
            cur = time.time()
            if (cur - self.last_shoot) > 0.25:
                # oglblit.play_audio(self.shoot_sound)
                self.last_shoot = cur
                m = Missile()
                m.set_position(self.get_position() + vector2(10, -30))
                m.set_velocity(0, -300)
                self.scene.add(m)
        self.set_velocity(vx, 0)

    def advance(self, dt):
        self.handle_keys()
        super().advance(dt)
        p = self.get_position()
        if p.x > 750:
            self.set_position(750, p.y)
        if p.x < 10:
            self.set_position(10, p.y)
        return True


class Game(Application):
    def __init__(self):
        super().__init__(res=(800, 600), scale=1.5)
        self.keys = []
        global sheet
        sheet = get_sheet('tinvader.png')
        self.scene = Scene()
        self.space = load_json_file("space.json")
        self.view = View()
        for i in range(0, 5):
            b = Blocker()
            b.set_position(i * 150 + 75, 500)
            self.scene.add(b)
        self.monster_group = MonsterGroup(self.scene)
        self.ship = Ship(self.scene)
        self.scene.add(self.ship)

    def loop(self, dt):
        self.scene.advance(dt)
        self.monster_group.advance(dt)
        vy = self.view.get_position().y
        # self.view.set_position(vector2(self.boy.get_position().x-300,vy))
        self.draw()
        return True

    def draw(self):
        self.space.draw(vector2(0, 0))
        self.scene.draw(self.view)
        time.sleep(0.01)


def main():
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
