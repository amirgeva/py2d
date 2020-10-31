import pygame
import time
from engine.keycodes import KeyCodes

app = None


# EXPORT
class Application(object):
    def __init__(self, res=(640, 480), scale=1.0):
        global app
        app = self
        self.res = res
        self.screen = pygame.display.set_mode(res)
        self.fps = 30
        self.keys = []
        self.last_ts = time.time()

    def calc_dt(self):
        cur = time.time()
        dt = cur - self.last_ts
        # print("dt={}".format(dt))
        self.last_ts = cur
        self.fps = 0.9 * self.fps + 0.1 / dt
        return dt

    @staticmethod
    def flip():
        pygame.display.flip()

    def clear(self, color=(192, 128, 255)):
        pass

    def onKey(self, key):
        pass

    def onClick(self, pos):
        pass

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        self.keys = pygame.key.get_pressed()
        return True

    def loop(self, dt):
        pass

    def run(self):
        while self.handleEvents():
            if not self.loop(self.calc_dt()):
                break
            self.flip()


# EXPORT
def get_screen_size():
    return app.res


# EXPORT
def get_screen():
    return app.screen


# EXPORT
def key_down(key_name):
    if key_name not in KeyCodes:
        return False
    code = KeyCodes.get(key_name)
    return app.keys[code]
