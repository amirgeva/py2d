#!/usr/bin/env python3
import sys
import pygame
from engine import *
from engine.utils import vector2
from platform import generate_level
from boy import Boy

class Game(Application):
    def __init__(self):
        super(Game,self).__init__()
        self.scene=Scene()
        self.view=View()
        generate_level(self.scene,3000,0.5)
        self.boy=Boy()
        self.boy.set_position(32,300)
        self.scene.add(self.boy)
        self.keys=[]

    def loop(self,dt):
        #dt=0.033
        self.scene.advance(dt)
        vy=self.view.get_position().y
        self.view.set_position(vector2(self.boy.get_position().x-300,vy))
        self.draw()
        return True

    def draw(self):
        get_screen().fill((0,0,0))
        self.scene.draw(self.view)


def main():
    game=Game()
    game.run()

if __name__=='__main__':
    main()
