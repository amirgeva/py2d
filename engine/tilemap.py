import pygame
from cache import get_sheet
# from utils import parse_rect, parse_float, format_rect
from xml.dom.minidom import parseString
from rtree import RTree


class TileSet:
    def __init__(self, sheet, first, tile_size):
        self.sheet = sheet
        self.first = first
        self.tile_size = tile_size
        self.grid_size = (sheet.width() / tile_size[0], sheet.height() / tile_size[1])
        # self.cache={}

    def __getitem__(self, index):
        # if index in self.cache:
        #    return self.cache.get(index)
        if index < self.first or index >= (self.first + len(self)):
            return None
        i = index - self.first
        ix = i % self.grid_size[0]
        iy = i / self.grid_size[0]
        r = pygame.Rect(ix * self.tile_size[0], iy * self.tile_size[1], self.tile_size[0], self.tile_size[1])
        s = self.sheet.subsurface(r)
        # self.cache[index]=s
        return s

    def __len__(self):
        return self.grid_size[0] * self.grid_size[1]


class TileLayer(object):
    def __init__(self):
        self.tree = RTree()

    def add(self, tile, rect):
        self.tree.add(tile, rect)


class TileMap:
    def __init__(self):
        self.layers = []
        self.tile_sets = []

    def load_file(self, filename):
        s = open(filename).read()
        return self.load_str(s)

    def load_str(self, s: str):
        return self.load(parseString(s))

    def load(self, root):
        width = int(root['width'])
        height = int(root['height'])
        tile_width = int(root['tilewidth'])
        tile_height = int(root['tileheight'])
        for ts in root._children('tileset'):
            first = int(ts['firstgid'])
            images = ts._children('image')
            image = images[0]
            sheet = get_sheet(image['source'])
            self.tile_sets.append(TileSet(sheet, first, (tile_width, tile_height)))
        for ld in root._children('layer'):
            data = ld._children('data')[0]
            layer = TileLayer()
            self.layers.append(layer)
            lines = data.text.strip().split('\n')
            for y in range(height):
                ids = lines[y].split(',')
                for x in range(width):
                    rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
                    id = int(ids[x])
                    if id > 0:
                        layer.add(self.get_tile(id), rect)

    def get_tile(self, id):
        for ts in self.tile_sets:
            tile = ts[id]
            if tile:
                return tile
        return None

    def draw(self, target):
        for layer in self.layers:
            items = layer.tree.search(pygame.Rect(0, 0, target.width(), target.height()))
            for item in items:
                tile = item[0]
                rect = item[1]
                target.blit(tile, (rect.left, rect.top))


def unit_test():
    import sys
    pygame.init()
    screen = pygame.display.set_mode((1280, 960))
    map = TileMap()
    map.load_file('tiles.tmx')
    while True:
        map.draw(screen)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    unit_test()
