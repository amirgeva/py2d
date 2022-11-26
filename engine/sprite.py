import pygame
from typing import Optional, List, Dict
from engine.app import get_screen
from engine.cache import get_sheet, get_sheet_name, get_mask
from engine.utils import Rect
from engine.subsheet import Subsheet
import json
import os


# EXPORT
class Sprite:
    def __init__(self, surface, rect, duration=0.0):
        self._pixels = Subsheet(surface, rect)
        self._mask = get_mask(surface, rect.as_tuple())
        self._duration = duration

    def draw(self, position):
        self._pixels.blit(get_screen(), position)

    def width(self):
        return self._pixels.width()

    def height(self):
        return self._pixels.height()

    def get_duration(self):
        return self._duration

    def set_duration(self, duration: float):
        self._duration = duration

    def get_rect(self):
        return Rect(0, 0, self.width(), self.height())

    def serialize(self):
        obj = {
            'Rect': self.get_rect(),
            'Duration': self._duration
        }
        return obj

    @staticmethod
    def deserialize(texture, obj):
        r = obj['Rect']
        dur = obj['Duration']
        rect = Rect(r[0], r[1], r[2], r[3])
        return Sprite(texture, rect, dur)


# EXPORT
class AnimationSequence(object):
    def __init__(self, name: str, base_velocity: float = 1.0):
        self._name = name
        self._base_velocity = base_velocity
        self._sprites: List[Sprite] = []

    def get_name(self) -> str:
        return self._name

    def get_base_velocity(self) -> float:
        return self._base_velocity

    def add_sprite(self, sprite: Sprite):
        self._sprites.append(sprite)

    def serialize(self):
        frames = []
        for s in self._sprites:
            frames.append(s.serialize())
        return {
            'Name': self._name,
            'BaseVelocity': self._base_velocity,
            'Frames': frames
        }

    def deserialize(self, surface: pygame.Surface, seq):
        self._sprites = []
        for frame in seq['Frames']:
            self.add_sprite(Sprite.deserialize(surface, frame))

    def __getitem__(self, index):
        return self._sprites[index]

    def __len__(self):
        return len(self._sprites)


# EXPORT
class AnimatedSprite(object):
    def __init__(self):
        self._sheet = None
        self._sequences = {}
        self._flags = {}
        self._active_sequence: Optional[AnimationSequence] = None
        self._cur_sprite = 0
        self._dt = 0.0
        self._anim_dir = ''

    def clear(self):
        self._sheet: Optional[pygame.Surface] = None
        self._sequences: Dict[str, AnimationSequence] = {}
        self._flags = {}
        self._active_sequence: Optional[AnimationSequence] = None
        self._cur_sprite = 0
        self._dt = 0.0
        self._anim_dir = ''

    def add_flag(self, name, value):
        if name == 'AnimDir':
            self._anim_dir = value
        self._flags[name] = value

    def get_longest_sequence(self):
        mx = 0
        res = None
        for name in self._sequences:
            seq = self._sequences.get(name)
            if len(seq) > mx:
                mx = len(seq)
                res = seq
        return res

    def get_sequence_by_name(self, name):
        return self._sequences.get(name)

    def get_sequence_by_index(self, index):
        for name in self._sequences.keys():
            if index == 0:
                return self._sequences.get(name)
            index -= 1
        return None

    def get_active_sequence_name(self):
        if not self._active_sequence:
            return ''
        return self._active_sequence.get_name()

    def set_active_sequence(self, name):
        if name != self.get_active_sequence_name() and name in self._sequences:
            self._active_sequence = self._sequences.get(name)
            self._dt = 0.0
            self._cur_sprite = 0

    def add_sequence(self, seq):
        self._sequences[seq.get_name()] = seq
        if not self._active_sequence:
            self._active_sequence = seq

    def calculate_axial_velocity(self, velocity):
        if self._anim_dir == 'X':
            return abs(velocity.x)
        if self._anim_dir == 'Y':
            return abs(velocity.y)
        return velocity.length()

    def advance(self, dt, velocity):
        axial_velocity = self.calculate_axial_velocity(velocity)
        # print "axial={}".format(axial_velocity)
        if self._active_sequence and len(self._active_sequence) > 0:
            mult = 1.0
            if hasattr(self._active_sequence, 'base_vel'):
                if self._active_sequence.get_base_velocity() > 0 and axial_velocity > 0.001:
                    mult = axial_velocity / self._active_sequence.get_base_velocity()
            # print "mult={}".format(mult)
            self._dt = self._dt + dt * mult
            # print "self.dt={}".format(self.dt)
            if self._cur_sprite >= len(self._active_sequence):
                self._cur_sprite = 0
            spr = self._active_sequence[self._cur_sprite]
            while self._dt >= spr.get_duration():
                self._dt = self._dt - spr.get_duration()
                self._cur_sprite += 1
                if self._cur_sprite >= len(self._active_sequence):
                    self._cur_sprite = 0
        return True

    def get_current_sprite(self):
        if self._active_sequence:
            return self._active_sequence[self._cur_sprite]
        return None

    def get_current_height(self):
        spr = self.get_current_sprite()
        if spr:
            return spr.height()
        return 0

    def draw(self, position):
        spr = self.get_current_sprite()
        if spr:
            spr.draw(position)

    def get_rect(self):
        spr = self.get_current_sprite()
        if spr:
            return spr.get_rect()
        return Rect(0, 0, 1, 1)

    def serialize(self):
        sequences = [s.serialize() for s in self._sequences.values()]
        obj = {
            'Image': get_sheet_name(self._sheet),
            'Sequences': sequences,
            'Flags': self._flags
        }
        return json.dumps(obj, indent=4)

    def deserialize(self, obj):
        self.clear()
        self._sheet = get_sheet(obj['Image'])
        flags = obj['Flags']
        for key in flags:
            self.add_flag(key, flags[key])
        for seq in obj['Sequences']:
            s = AnimationSequence(seq['Name'], seq['BaseVelocity'])
            s.deserialize(self._sheet, seq)
            self.add_sequence(s)
        return self

    def load(self, filename):
        self.deserialize(json.load(open(filename, "r")))


# EXPORT
def load_json_file(filename):
    obj = json.load(open(filename, "r"))
    a = AnimatedSprite()
    a.deserialize(obj)
    return a


# EXPORT
def load_json_str(s):
    obj = json.loads(s)
    return AnimatedSprite().deserialize(obj)


# EXPORT
def load_file(filename):
    return load_json_file(filename)


# EXPORT
def load_str(s):
    return load_json_str(s)


# # EXPORT
# def generate_blocks_sprite(filename, w, h, x0, y0, padx, pady):
#     s = get_surface(filename)
#     x = x0
#     y = y0
#     anim = AnimatedSprite(filename)
#     i = 0
#     j = 0
#     while (y + h) < s.height():
#         while (x + w) < s.width():
#             name = '{},{}'.format(i, j)
#             print(name)
#             seq = AnimationSequence(name)
#             seq.add_sprite(Sprite(s, pygame.Rect(x, y, w, h)))
#             anim.add_sequence(seq)
#             x += (w + padx)
#             j += 1
#         x = x0
#         y += (h + pady)
#         i += 1
#         j = 0
#     return anim

if __name__ == '__main__':
    print(os.getcwd())
    # oglblit.init(800, 600, 1)
    # ship = load_file('ship.json')
    # open('fff.json', 'w').write(ship.serialize())
    # oglblit.deinit()
