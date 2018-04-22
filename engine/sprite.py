import oglblit
from engine.cache import get_sheet, get_sheet_name
from engine.utils import Rect, Point, parse_rect, parse_float
import json
import os


#EXPORT
class Sprite(object):
    def __init__(self, sprite_id, duration=0.0):
        self.sprite_id = sprite_id
        self.rect=Rect(0,0,oglblit.get_sprite_width(sprite_id),oglblit.get_sprite_height(sprite_id))
        self.duration=duration

    def draw(self, position):
        oglblit.draw_sprite(self.sprite_id, False, position)

    def get_height(self):
        return self.rect.height()

    def get_rect(self):
        return Rect(self.rect)

    def serialize(self):
        obj = {
            'Rect': self.rect,
            'Duration' : self.duration
        }
        return obj

    @staticmethod
    def deserialize(texture, obj):
        r = obj['Rect']
        dur = obj['Duration']
        sprite_id = oglblit.create_sprite(texture,r[0],r[1],r[2],r[3])
        return Sprite(sprite_id,dur)


# EXPORT
class AnimationSequence(object):
    def __init__(self, name, base_vel=1.0):
        self.name = name
        self.base_vel = base_vel
        self.sprites = []

    def add_sprite(self, sprite):
        self.sprites.append(sprite)

    def serialize(self):
        frames = []
        for s in self.sprites:
            frames.append(s.serialize())
        return {
            'Name': self.name,
            'BaseVelocity': self.base_vel,
            'Frames': frames
        }

    def deserialize(self, texture, seq):
        self.sprites=[]
        for frame in seq['Frames']:
            self.add_sprite(Sprite.deserialize(texture,frame))

    def __getitem__(self, index):
        return self.sprites[index]

    def __len__(self):
        return len(self.sprites)


# EXPORT
class AnimatedSprite(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.sheet = None
        self.sequences = {}
        self.flags = {}
        self.active_sequence = None
        self.cur_sprite = 0
        self.dt = 0.0
        self.anim_dir = ''

    def add_flag(self, name, value):
        if name == 'AnimDir':
            self.anim_dir = value
        self.flags[name] = value

    def get_longest_sequence(self):
        mx = 0
        res = None
        for name in self.sequences:
            seq = self.sequences.get(name)
            if len(seq) > mx:
                mx = len(seq)
                res = seq
        return res

    def get_sequence_by_name(self, name):
        return self.sequences.get(name)

    def get_sequence_by_index(self, index):
        for name in self.sequences.keys():
            if index == 0:
                return self.sequences.get(name)
            index -= 1
        return None

    def get_active_sequence_name(self):
        if not self.active_sequence:
            return ''
        return self.active_sequence.name

    def set_active_sequence(self, name):
        if name != self.get_active_sequence_name() and name in self.sequences:
            self.active_sequence = self.sequences.get(name)
            self.dt = 0.0
            self.cur_sprite = 0

    def add_sequence(self, seq):
        self.sequences[seq.name] = seq
        if not self.active_sequence:
            self.active_sequence = seq

    def calculate_axial_velocity(self, velocity):
        if self.anim_dir == 'X':
            return abs(velocity.x)
        if self.anim_dir == 'Y':
            return abs(velocity.y)
        return velocity.length()

    def advance(self, dt, velocity):
        axial_velocity = self.calculate_axial_velocity(velocity)
        # print "axial={}".format(axial_velocity)
        if self.active_sequence and len(self.active_sequence) > 0:
            mult = 1.0
            if hasattr(self.active_sequence, 'base_vel'):
                if self.active_sequence.base_vel > 0 and axial_velocity > 0.001:
                    mult = axial_velocity / self.active_sequence.base_vel;
            # print "mult={}".format(mult)
            self.dt = self.dt + dt * mult
            # print "self.dt={}".format(self.dt)
            if self.cur_sprite >= len(self.active_sequence):
                self.cur_sprite = 0
            spr = self.active_sequence[self.cur_sprite]
            while self.dt >= spr.duration:
                self.dt = self.dt - spr.duration
                self.cur_sprite += 1
                if self.cur_sprite >= len(self.active_sequence):
                    self.cur_sprite = 0
        return True

    def get_current_sprite(self):
        if self.active_sequence:
            return self.active_sequence[self.cur_sprite]
        return None

    def get_current_height(self):
        spr = self.get_current_sprite()
        if spr:
            return spr.get_height()
        return 0

    def draw(self, position):
        spr = self.get_current_sprite()
        if spr:
            oglblit.draw_sprite(spr.sprite_id, False, int(position.x), int(position.y))

    def get_rect(self):
        spr = self.get_current_sprite()
        if spr:
            return spr.get_rect()
        return Rect(0, 0, 1, 1)

    def serialize(self):
        sequences = [s.serialize() for s in self.sequences.values()]
        obj = {
            'Image': get_sheet_name(self.sheet),
            'Sequences': sequences,
            'Flags': self.flags
        }
        return json.dumps(obj, indent=4)

    def deserialize(self, obj):
        self.clear()
        self.sheet = get_sheet(obj['Image'])
        flags = obj['Flags']
        for key in flags:
            self.add_flag(key, flags[key])
        for seq in obj['Sequences']:
            s = AnimationSequence(seq['Name'], seq['BaseVelocity'])
            s.deserialize(self.sheet, seq)
            self.add_sequence(s)

    def load(self,filename):
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
    return AnimatedSprite.deserialize(obj)


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
#     while (y + h) < s.get_height():
#         while (x + w) < s.get_width():
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
    oglblit.init(800, 600, 1)
    ship = load_file('ship.json')
    open('fff.json', 'w').write(ship.serialize())
    oglblit.deinit()
