import sys
from engine import *
from engine.utils import vector2
import random

from block import Block
from ogre import Ogre

def generate_platform(scene,x,y,l):
    for i in range(0,l):
        j=random.randint(6,9)
        if i==0: j=5
        if i==(l-1): j=10
        b=Block(1,j)
        b.set_position(x,y)
        x+=32
        scene.add(b)

def generate_level(scene,xlen,difficulty,seed=1):
    random.seed(seed)
    y=416
    generate_platform(scene,0,y,6)
    x=192
    ogre_done=False
    while y>100:
        while x<xlen:
            if random.random()>difficulty:
                l=random.randint(3,7)
                generate_platform(scene,x,y,l)
                if random.random()<(difficulty-0.4):
                    ogre_done=True
                    monster=Ogre(x,x+l*32-40,50)
                    monster.set_position(x+20,y-54)
                    scene.add(monster)
                x+=32*(l+2)
            else:
                x+=32
        x=128
        y-=96


