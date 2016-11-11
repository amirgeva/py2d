import pygame
import utils
from rtree import RTree


#EXPORT
class Scene(object):
    def __init__(self):
        self.entities={}
        self.dynamics=set()
        self.rtree=RTree()
        
    def add(self,entity):
        id=entity.get_id()
        self.entities[id]=entity
        if entity.is_dynamic():
            self.dynamics.add(id)
        r=entity.get_rect()
        self.rtree.add(id,r)
        
    def advance(self,dt):
        dels=[]
        for id in self.dynamics:
            e=self.entities.get(id)
            before=e.get_rect()
            if not e.advance(dt):
                dels.append(id)
            else:
                after=e.get_rect()
                if not utils.same_rect(before,after):
                    self.check_collisions(e,after)
                    after=e.get_rect()                    
                    self.rtree.move(e.get_id(),after)
        if len(dels)>0:
            for id in dels:
                self.rtree.remove(id)
                self.dynamics.remove(id)
                del self.entities[id]

    def draw(self,view):
        visible=self.rtree.search(view.get_rect())
        for (id,rect) in visible:
            e=self.entities.get(id)
            if e:
                e.draw(view)

    def check_collisions(self,entity,rect):
        return
        id=entity.get_id()
        cands=self.rtree.search(rect)
        m1=entity.get_mask()
        for (cand_id,cand_rect) in cands:
            if cand_id!=id:
                cand=self.entities.get(cand_id)
                m2=cand.get_mask()
                offset=cand.get_position()-entity.get_position()
                ox=int(offset.x)
                oy=int(offset.y)
                c=m1.overlap_area(m2,(ox,oy))
                if c>0:
                    n1=m1.overlap_mask(m2,(ox,oy))
                    n2=m2.overlap_mask(m1,(-ox,-oy))
                    entity.collision(cand,n1.centroid())
                    cand.collision(entity,n2.centroid())
        
            