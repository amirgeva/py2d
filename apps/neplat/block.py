import sys
from engine import *

blocks = None


def get_blocks_anim(i, j):
    global blocks
    if not blocks:
        blocks = load_file('blocks.json')
    a = AnimatedSprite()
    name = ','.join([str(i), str(j)])
    a.add_sequence(blocks.get_sequence_by_name(name))
    return a


class Block(Entity):
    def __init__(self, i, j):
        super().__init__(get_blocks_anim(i, j))
        self.dynamic = False
