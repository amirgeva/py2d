import numpy as np
from cv2 import cv2


class Level:
    def __init__(self):
        self.map = np.ndarray((24, 78), dtype=np.uint8)
        self.map.fill(255)
        self.tiles = cv2.imread('tiles.png', cv2.IMREAD_COLOR)
        self.tiles_count = self.tiles.shape[1] // 32

    def draw(self):
        h, w = self.map.shape
        image = np.zeros((h * 32, w * 32, 3), dtype=np.uint8)
        for i in range(h):
            y = i * 32
            for j in range(w):
                x = j * 32
                v = self.map[i, j]
                if 0 <= v < self.tiles_count:
                    tx = int(v) * 32
                    image[y:(y + 32), x:(x + 32), :] = self.tiles[0:32, tx:(tx + 32), :]

    def generate(self):
        pass


def main():
    pass


if __name__ == '__main__':
    main()
   