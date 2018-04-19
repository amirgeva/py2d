#!/usr/bin/env python
import sys
sys.path.append('../..')
#sys.path.append('.')
from engine import *
import pygame
from pygame.math import Vector2
from platform import generate_level
from boy import Boy

class Game(Application):
    def __init__(self):
        super(Game,self).__init__()
        self.scene=Scene()
        self.view=View(self.screen)
        generate_level(self.scene,3000,0.5)
        self.boy=Boy()
        self.boy.set_position(32,300)
        self.scene.add(self.boy)

    def loop(self,dt):
        dt=0.033
        self.boy.set_keys(self.keys)
        self.scene.advance(dt)
        vy=self.view.get_position()[1]
        self.view.set_position(Vector2(self.boy.get_position().x-300,vy))
        self.draw()

    def draw(self):
        self.screen.fill(pygame.Color(64,128,255))
        self.scene.draw(self.view)


def main():
    game=Game()
    game.run()

if __name__=='__main__':
    main()