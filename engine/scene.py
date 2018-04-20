import oglblit
from engine.rtree import RTree
from engine.utils import Point


# EXPORT
class Scene(object):
    def __init__(self):
        self.entities = {}
        self.dynamics = set()
        self.statics = set()
        self.rtree = RTree()

    def add(self, entity):
        id = entity.get_id()
        self.entities[id] = entity
        if entity.is_dynamic():
            self.dynamics.add(id)
        else:
            self.statics.add(id)
        r = entity.get_rect()
        self.rtree.add(id, r)

    def advance(self, dt):
        dels = []
        for id in self.dynamics:
            e = self.entities.get(id)
            before = e.get_rect()
            if not e.advance(dt):
                dels.append(id)
            else:
                after = e.get_rect()
                if before != after:
                    self.check_collisions(e, after)
                    after = e.get_rect()
                    self.rtree.move(e.get_id(), after)
        if len(dels) > 0:
            for id in dels:
                self.rtree.remove(id)
                self.dynamics.remove(id)
                del self.entities[id]

    def draw(self, view):
        visible = self.rtree.search(view.get_rect())
        vis_id = [v[0] for v in visible]
        ids = [id for id in vis_id if id in self.statics]
        ids.extend([id for id in vis_id if id not in self.statics])
        for id in ids:
            e = self.entities.get(id)
            if e:
                e.draw(view)

    def check_collisions(self, entity, rect):
        id = entity.get_id()
        spr1=entity.anim.get_current_sprite().sprite_id
        cands = self.rtree.search(rect)
        for (cand_id, cand_rect) in cands:
            if cand_id != id:
                cand = self.entities.get(cand_id)
                spr2 = cand.anim.get_current_sprite().sprite_id
                offset = cand.get_position() - entity.get_position()
                ox = int(offset.x)
                oy = int(offset.y)
                pts = oglblit.check_collision(spr1,spr2,ox,oy)
                if pts > 0:
                    dx = oglblit.get_collision_x()
                    dy = oglblit.get_collision_y()
                    entity.collision(cand, Point(dx, dy))
                    cand.collision(entity, Point(dx-ox, dy-oy))
