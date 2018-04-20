import oglblit
import time


# EXPORT
class Application(object):
    def __init__(self, res=(640, 480)):
        oglblit.init(res[0], res[1], 1)
        self.fps = 30
        self.last_ts = time.time()

    def calc_dt(self):
        cur = time.time()
        dt = cur - self.last_ts
        self.last_ts = cur
        self.fps = 0.9 * self.fps + 0.1 / dt
        return dt

    def flip(self):
        oglblit.render()

    def clear(self, color=(192, 128, 255)):
        pass

    def onKey(self, key):
        pass

    def onClick(self, pos):
        pass

    def handleEvents(self):
        self.keys = [int(k) for k in oglblit.get_keys().split()]
        if 256 in self.keys:
            return False
        # for event in pygame.event.get():
        #     if hasattr(event, 'key'):
        #         if event.key == K_ESCAPE:
        #             return False
        #         else:
        #             if event.type==2:
        #                 self.onKey(event.key)
        #     elif event.type==pygame.MOUSEBUTTONDOWN:
        #         self.onClick(event.pos)
        #     #elif hasattr(event,)
        return True

    def loop(self, dt):
        pass

    def run(self):
        while self.handleEvents():
            if not self.loop(self.calc_dt()):
                break
            self.flip()
