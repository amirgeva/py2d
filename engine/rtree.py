#!/usr/bin/env python3
from engine.utils import Rect
from random import randint, seed


class RTreeNode(object):
    def __init__(self, parent):
        self.children = []
        self.items = []
        self.rect = None
        self.parent = parent

    def move(self, id, rect):
        if self.rect.contains(rect):
            for i in range(len(self.items)):
                if self.items[i][0] == id:
                    self.items[i] = (id, rect)
                    return True
        return False

    def add_item(self, id, rect):
        if not self.rect:
            self.rect = Rect(rect)
        else:
            self.rect.union(rect)
        if len(self.children) > 0:
            return self.add_to_child(id, rect)
        else:
            self.items.append((id, rect))
            if len(self.items) >= 8:
                return self.split_node(id)
            return self

    def add_to_child(self, id, rect):
        min_delta = 99999999
        best_child = None
        for c in self.children:
            r = Rect(rect)
            r.union(c.rect)
            delta = r.area() - c.rect.area()
            if delta < min_delta:
                min_delta = delta
                best_child = c
        return best_child.add_item(id, rect)

    def split_node(self, id):
        if randint(0, 1) == 0:
            self.items.sort(key=lambda t: t[1].tl.x)
        else:
            self.items.sort(key=lambda t: t[1].tl.y)
        mid = int(len(self.items) / 2)
        self.children.append(RTreeNode(self))
        for i in self.items[0:mid]:
            self.children[-1].add_item(i[0], i[1])
        self.children.append(RTreeNode(self))
        for i in self.items[mid:]:
            self.children[-1].add_item(i[0], i[1])
        self.items = []
        return self.children

    def search(self, rect):
        res = []
        if not self.rect:
            return res
        if rect.overlaps(self.rect):
            for i in self.items:
                if i[1].overlaps(rect):
                    res.append(i)
            for c in self.children:
                res = res + c.search(rect)
        return res

    def remove_item(self, id):
        for i in range(len(self.items)):
            if self.items[i][0] == id:
                del self.items[i]
                break
        self.recalc_rect()

    def remove_child(self, child):
        for i in range(0, len(self.children)):
            if self.children[i] == child:
                del self.children[i]
                break
        return True

    def recalc_rect(self):
        if len(self.children) == 0 and len(self.items) == 0 and self.parent:
            return self.parent.remove_child(self)
        self.rect = Rect()
        for c in self.children:
            self.rect.union(c.rect)
        for item in self.items:
            self.rect.union(item[1])
        if self.parent:
            self.parent.recalc_rect()

    def get_depth(self):
        if len(self.children) > 0:
            return self.children[0].get_depth() + 1
        return 1


# EXPORT
class RTree(object):
    def __init__(self):
        self.root = RTreeNode(None)
        self.directory = {}

    def add(self, id, rect):
        self.remove(id)
        nodes = self.root.add_item(id, rect)
        if isinstance(nodes, list):
            for child in nodes:
                for item in child.items:
                    self.directory[item[0]] = child
        else:
            self.directory[id] = nodes

    def move(self, id, rect):
        if id in self.directory:
            node = self.directory.get(id)
            if not node.move(id, rect):
                self.remove(id)
                self.add(id, rect)

    def remove(self, id):
        if id in self.directory:
            node = self.directory.get(id)
            node.remove_item(id)
            del self.directory[id]
            return True
        return False

    def search(self, rect):
        return self.root.search(rect)

    def depth(self):
        return self.root.get_depth()


class BFTree(object):
    def __init__(self):
        self.rects = {}

    def add(self, id, rect):
        self.rects[id] = rect

    def move(self, id, rect):
        self.add(id, rect)

    def remove(self, id):
        if id in self.rects:
            del self.rects[id]

    def search(self, rect):
        res = []
        for id in self.rects:
            r = self.rects.get(id)
            if r.overlaps(rect):
                res.append((id, r))
        return res

    def get_random_id(self):
        if len(self.rects) == 0:
            return 0
        ids = list(self.rects.keys())
        return ids[randint(0, len(ids) - 1)]


def unit_test():
    def rand_rect():
        x = randint(0, 1000)
        y = randint(0, 1000)
        w = randint(16, 64)
        h = randint(16, 64)
        return Rect(x, y, x + w, y + h)

    seed(1)
    t1 = RTree()
    t2 = BFTree()
    fail = False
    rects = 0
    for i in range(10000):
        print("{} {} {}".format(i, rects, t1.depth()))
        if fail:
            break
        act = randint(0, 100)
        if act < 40:
            r = rand_rect()
            id = i  # randint(0, 10000)
            t1.add(id, r)
            t2.add(id, r)
            rects += 1
        elif act < 60:
            id = t2.get_random_id()
            if t1.remove(id):
                rects -= 1
            t2.remove(id)
        elif act < 90:
            r = rand_rect()
            res1 = t1.search(r)
            res2 = t2.search(r)
            if len(res1) != len(res2):
                print("{}: Mismatch result length".format(i))
                fail = True
                break
            res1.sort(key=lambda t: t[0])
            res2.sort(key=lambda t: t[0])
            for j in range(len(res1)):
                if res1[j][0] != res2[j][0]:
                    print("{}: Mismatch found id".format(i))
                    fail = True
                    break
        elif act < 100:
            id = t2.get_random_id()
            r = rand_rect()
            t1.move(id, r)
            t2.move(id, r)
    if not fail:
        print("All tests successful")


if __name__ == '__main__':
    try:
        unit_test()
    except RecursionError:
        print("RecursionError")
