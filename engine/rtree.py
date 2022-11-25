#!/usr/bin/env python3
import sys
from engine.utils import Rect
from random import randint, seed


class RTreeNode(object):
    def __init__(self, parent):
        self._children = []
        self._items = []
        self._rect = None
        self._parent = parent

    def get_items(self):
        return self._items

    def get_rect(self):
        return self._rect

    def move(self, item_id, rect):
        if self._rect.contains(rect):
            for i in range(len(self._items)):
                if self._items[i][0] == item_id:
                    self._items[i] = (item_id, rect)
                    return True
        return False

    def add_item(self, item_id, rect):
        if not self._rect:
            self._rect = Rect(rect)
        else:
            self._rect.union(rect)
        if len(self._children) > 0:
            return self.add_to_child(item_id, rect)
        else:
            self._items.append((item_id, rect))
            if len(self._items) >= 8:
                return self.split_node()
            return self

    def add_to_child(self, item_id, rect):
        min_delta = 99999999
        best_child = None
        for c in self._children:
            r = Rect(rect)
            r.union(c.get_rect())
            delta = r.area() - c.get_rect().area()
            if delta < min_delta:
                min_delta = delta
                best_child = c
        if not best_child:
            return self.add_item(item_id, rect)
        return best_child.add_item(item_id, rect)

    def split_node(self):
        if randint(0, 1) == 0:
            self._items.sort(key=lambda t: t[1].tl.x)
        else:
            self._items.sort(key=lambda t: t[1].tl.y)
        mid = int(len(self._items) / 2)
        self._children.append(RTreeNode(self))
        for i in self._items[0:mid]:
            self._children[-1].add_item(i[0], i[1])
        self._children.append(RTreeNode(self))
        for i in self._items[mid:]:
            self._children[-1].add_item(i[0], i[1])
        self._items = []
        return self._children

    def search(self, rect):
        res = []
        if not self._rect:
            return res
        if rect.overlaps(self._rect):
            for i in self._items:
                if i[1].overlaps(rect):
                    res.append(i)
            for c in self._children:
                res = res + c.search(rect)
        return res

    def remove_item(self, item_id):
        for i in range(len(self._items)):
            if self._items[i][0] == item_id:
                del self._items[i]
                break
        self.recalc_rect()

    def remove_child(self, child):
        for i in range(0, len(self._children)):
            if self._children[i] == child:
                del self._children[i]
                break
        return True

    def recalc_rect(self):
        if len(self._children) == 0 and len(self._items) == 0 and self._parent:
            return self._parent.remove_child(self)
        self._rect = Rect()
        for c in self._children:
            self._rect.union(c.get_rect())
        for item in self._items:
            self._rect.union(item[1])
        if self._parent:
            self._parent.recalc_rect()

    def get_depth(self):
        if len(self._children) > 0:
            return self._children[0].get_depth() + 1
        return 1


# EXPORT
class RTree(object):
    def __init__(self):
        self._root = RTreeNode(None)
        self._directory = {}

    def add(self, item_id, rect):
        self.remove(item_id)
        nodes = self._root.add_item(item_id, rect)
        if isinstance(nodes, list):
            for child in nodes:
                for item in child.get_items():
                    self._directory[item[0]] = child
        else:
            self._directory[item_id] = nodes

    def move(self, item_id, rect):
        if item_id in self._directory:
            node = self._directory.get(item_id)
            if not node.move(item_id, rect):
                self.add(item_id, rect)

    def remove(self, item_id):
        if item_id in self._directory:
            node = self._directory.get(item_id)
            node.remove_item(item_id)
            del self._directory[item_id]
            return True
        return False

    def search(self, rect):
        return self._root.search(rect)

    def depth(self):
        return self._root.get_depth()


class BFTree(object):
    def __init__(self):
        self.rects = {}

    def add(self, item_id, rect):
        self.rects[item_id] = rect

    def move(self, item_id, rect):
        self.add(item_id, rect)

    def remove(self, item_id):
        if item_id in self.rects:
            del self.rects[item_id]

    def search(self, rect):
        res = []
        for item_id in self.rects:
            r = self.rects.get(item_id)
            if r.overlaps(rect):
                res.append((item_id, r))
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
        if (i & 255) == 0:
            sys.stdout.write(f'{i}\r')
        # print(f"{i} {rects} {t1.depth()}")
        if fail:
            break
        act = randint(0, 100)
        if act < 40:
            r = rand_rect()
            item_id = i  # randint(0, 10000)
            t1.add(item_id, r)
            t2.add(item_id, r)
            rects += 1
        elif act < 60:
            item_id = t2.get_random_id()
            if t1.remove(item_id):
                rects -= 1
            t2.remove(item_id)
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
            item_id = t2.get_random_id()
            r = rand_rect()
            t1.move(item_id, r)
            t2.move(item_id, r)
    if not fail:
        print("All tests successful")


if __name__ == '__main__':
    try:
        unit_test()
    except RecursionError:
        print("RecursionError")
