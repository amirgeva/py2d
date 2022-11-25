from engine.rtree import RTree
from engine.utils import Point


# EXPORT
class Scene(object):
    def __init__(self):
        self._entities = {}
        self._dynamics = set()
        self._statics = set()
        self._rtree = RTree()

    def add(self, entity):
        entity_id = entity.get_id()
        self._entities[entity_id] = entity
        if entity.is_dynamic():
            self._dynamics.add(entity_id)
        else:
            self._statics.add(entity_id)
        r = entity.get_rect()
        self._rtree.add(entity_id, r)

    def advance(self, dt):
        to_delete = []
        ids = set(self._dynamics)
        for entity_id in ids:
            e = self._entities.get(entity_id)
            before = e.get_rect()
            if not e.advance(dt):
                to_delete.append(entity_id)
            else:
                after = e.get_rect()
                if before != after:
                    self.check_collisions(e, after)
                    after = e.get_rect()
                    self._rtree.move(e.get_id(), after)
        if len(to_delete) > 0:
            for entity_id in to_delete:
                self._rtree.remove(entity_id)
                self._dynamics.remove(entity_id)
                del self._entities[entity_id]

    def draw(self, view):
        visible = self._rtree.search(view.get_rect())
        vis_id = [v[0] for v in visible]
        ids = [entity_id for entity_id in vis_id if entity_id in self._statics]
        ids.extend([entity_id for entity_id in vis_id if entity_id not in self._statics])
        for entity_id in ids:
            e = self._entities.get(entity_id)
            if e:
                e.draw(view)

    def check_collisions(self, entity, rect):
        entity_id = entity.get_id()
        spr1 = entity.anim.get_current_sprite()
        candidates = self._rtree.search(rect)
        for (cand_id, cand_rect) in candidates:
            if cand_id != entity_id:
                cand = self._entities.get(cand_id)
                spr2 = cand.anim.get_current_sprite()  # .sprite_id
                offset = cand.get_position() - entity.get_position()
                ox = int(offset.x)
                oy = int(offset.y)
                pt = spr1._mask.overlap(spr2._mask, (ox, oy))
                if pt is not None:
                    dx, dy = pt
                    entity.collision(cand, Point(dx, dy))
                    cand.collision(entity, Point(dx - ox, dy - oy))
