import pygame
import dom
from cache import get_surface
from utils import parse_rect, parse_float, format_rect
from xml.dom.minidom import Element, parseString
import json

#EXPORT
class Sprite(object):
    def __init__(self,surface=None,rect=None,duration=0.0):
        self.surface=surface
        if not rect:
            rect=pygame.Rect(0,0,surface.get_width(),surface.get_height())
        self.rect=rect
        self.duration=duration
        self.mask=pygame.mask.from_surface(self.surface.subsurface(self.rect),1)
        #print self.mask.centroid()
        
    def draw(self,target,position):
        if self.surface:
            target.blit(self.surface,position,self.rect)
            
    def get_mask(self):
        return self.mask
        
    def get_rect(self):
        return pygame.Rect(0,0,self.rect.width,self.rect.height)

    def serialize(self):
        obj = { 
            'Rect'     : format_rect(self.rect),
            'Duration' : str(1000*self.duration)
        }
        return obj
        
    @staticmethod
    def deserialize(surface, obj):
        rect=parse_rect(obj['Rect'])
        dur=0.001*parse_float(obj['Duration'])
        return Sprite(surf,rect,dur)
        


#EXPORT
class AnimationSequence(object):
    def __init__(self,name):
        self.name=name
        self.duration=0
        self.base_vel=1
        self.sprites=[]
        
    def add_sprite(self,sprite):
        self.sprites.append(sprite)
        self.duration=self.duration+sprite.duration

    def clear(self):
        self.sprites=[]
        self.duration=0
        
    def serialize(self):
        frames = [fr.serialize() for fr in self.sprites]
        obj = { 
            'Name' : self.name,
            'BaseVelocity' : str(self.base_vel),
            'Frames' : frames
        }
        return obj
        
    @staticmethod
    def deserialize(surface, seq):
        s=AnimationSequence(seq['Name'],parse_float(seq['BaseVelocity']))
        for fr in seq['Frames']:
            s.add_sprite(Sprite.deserialize(surface, fr))
        return s

        
    def __getitem__(self,index):
        return self.sprites[index]
        
    def __len__(self):
        return len(self.sprites)

#EXPORT
class AnimatedSprite(object):
    def __init__(self,sheet):
        self.sheet=sheet
        self.sequences={}
        self.flags={}
        self.active_sequence=None
        self.cur_sprite=0
        self.dt=0.0
        self.anim_dir=''
        
    def add_flag(self,name,value):
        if name=='AnimDir':
            self.anim_dir=value
        self.flags[name]=value
        
    def get_longest_sequence(self):
        mx=0
        res=None
        for name in self.sequences:
            seq=self.sequences.get(name)
            if len(seq)>mx:
                mx=len(seq)
                res=seq
        return res
        
    def get_sequence_by_name(self,name):        
        return self.sequences.get(name)
        
    def get_sequence_by_index(self,index):
        for name in self.sequences.keys():
            if index==0:
                return self.sequences.get(name)
            index-=1
        return None
        
    def set_active_sequence(self,name):
        if name in self.sequences:
            self.active_sequence=self.sequences.get(name)
            self.dt=0.0
            self.cur_sprite=0
        
    def add_sequence(self,seq):
        self.sequences[seq.name]=seq
        if not self.active_sequence:
            self.active_sequence=seq
            
    def calculate_axial_velocity(self,velocity):
        if self.anim_dir=='X': 
            return abs(velocity.x)
        if self.anim_dir=='Y': 
            return abs(velocity.y)
        return velocity.length()
        
    def advance(self,dt,velocity):
        axial_velocity=self.calculate_axial_velocity(velocity)
        if self.active_sequence:
            mult=1
            if hasattr(self.active_sequence,'base_vel'):
                if self.active_sequence.base_vel>0 and axial_velocity>0.001: 
                    mult=axial_velocity / self.active_sequence.base_vel;
            self.dt = self.dt + dt*mult
            spr = self.active_sequence[self.cur_sprite]
            while self.dt >= spr.duration:
                self.dt = self.dt - spr.duration
                self.cur_sprite+=1
                if self.cur_sprite>=len(self.active_sequence):
                    self.cur_sprite=0
        return True
        
    def draw(self,target,position):
        if self.active_sequence:
            spr = self.active_sequence[self.cur_sprite]
            spr.draw(target,position)
            
    def get_mask(self):
        if self.active_sequence:
            return self.active_sequence[self.cur_sprite].get_mask()
        return pygame.mask.Mask(1,1)

    def get_rect(self):
        if self.active_sequence:
            return self.active_sequence[self.cur_sprite].get_rect()
        return pygame.Rect(0,0,1,1)
        
    def serialize(self):
        sequences = [s.serialize() for s in self.sequences.values()]
        obj = { 
            'Image' : self.sheet,
            'Sequences' : sequences,
            'Flags': self.flags
        }
        return json.dumps(obj, indent=4)
        
    @staticmethod
    def deserialize(obj):
        res=AnimatedSprite(obj['Image'])
        surface = get_surface(obj['Image'])
        flags = obj['Flags']
        for key in flags:
            res.add_flag(key,flags[key])
        for seq in obj['Sequences']:
            s=AnimationSequence.deserialize(surface, seq)
            res.add_sequence(s)
        return res

def load_xml(root):
    res=AnimatedSprite()
    for flag in root.children('Flag'):
        res.add_flag(flag['Name'],flag['Value'])
    for seq in root.children('Sequence'):
        s=AnimationSequence(seq['Name'],parse_float(seq['BaseVelocity']))
        res.add_sequence(s)
        for fr in seq.children('Frame'):
            surf=get_surface(fr['Image'])
            rect=parse_rect(fr['Rect'])
            dur=0.001*parse_float(fr['Duration'])
            s.add_sprite(Sprite(surf,rect,dur))
    return res
    
#EXPORT
def load_xml_file(filename):
    return load(dom.parseFile(filename))
    
#EXPORT
def load_xml_str(s):
    return load(dom.parseString(filename))

#EXPORT
def load_file(filename):
    obj = json.load(filename)
    return AnimatedSprite.deserialize(obj)
    
#EXPORT
def load_str(s):
    obj = json.loads(filename)
    return AnimatedSprite.deserialize(obj)
            
        
    
