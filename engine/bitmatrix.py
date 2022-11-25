#!/usr/bin/env python3
from bitarray import bitarray


class BitMatrix(object):
    def __init__(self, width, height, init=True):
        self.sizes = (width, height)
        self.rows = [bitarray(width) for _ in range(0, height)]
        if init:
            self.clear()

    def width(self):
        return self.sizes[0]

    def height(self):
        return self.sizes[1]

    def get(self, x, y):
        if x < 0 or x >= self.width() or y < 0 or y >= self.height():
            return False
        row = self.rows[y]
        return row[x]

    def set(self, x, y, v):
        if 0 <= x < self.width() and 0 <= y < self.height():
            row = self.rows[y]
            row[x] = v

    def clear(self):
        for row in self.rows:
            row.setall(False)

    def setall(self):
        for row in self.rows:
            row.setall(True)


class BFBitMatrix(object):
    def __init__(self, width, height):
        self.sizes = (width, height)
        self.data = [False] * (width * height)

    def width(self):
        return self.sizes[0]

    def height(self):
        return self.sizes[1]

    def get(self, x, y):
        if x < 0 or x >= self.width() or y < 0 or y >= self.height():
            return False
        return self.data[y * self.width() + x]

    def set(self, x, y, v):
        if 0 <= x < self.width() and 0 <= y < self.height():
            self.data[y * self.width() + x] = v

    def clear(self):
        self.data = [False] * (self.width() * self.height())

    def setall(self):
        self.data = [True] * (self.width() * self.height())


def compare(m1, m2):
    if m1.width() != m2.width():
        return False
    if m1.height() != m2.height():
        return False
    for y in range(0, m1.height()):
        for x in range(0, m1.width()):
            if m1.get(x, y) != m2.get(x, y):
                return False
    return True


def unit_test():
    from random import randint, seed
    seed(1)
    try:
        matrix_size = 18
        repetitions = 1000
        mat1 = BitMatrix(matrix_size, matrix_size)
        mat2 = BFBitMatrix(matrix_size, matrix_size)
        for i in range(0, repetitions):
            if not compare(mat1, mat2):
                raise Exception("Failed {}".format(i))
            x = randint(0, matrix_size - 1)
            y = randint(0, matrix_size - 1)
            v = (randint(0, 1) > 0)
            mat1.set(x, y, v)
            mat2.set(x, y, v)
        print("Test successful")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    unit_test()
