import pygame


# def generate_checkers():
#     s = pygame.Surface((1920, 1080), pygame.HWSURFACE | pygame.SRCALPHA, 32)
#     d = 32
#     b = 96
#     colors = [pygame.Color(b, b, b, 255), pygame.Color(d, d, d, 255)]
#     dark = 1
#     for y in xrange(0, 135):
#         dark = 1 - dark
#         for x in xrange(0, 240):
#             dark = 1 - dark
#             pygame.draw.rect(s, colors[dark], pygame.Rect(x * 8, y * 8, 8, 8))
#     return s

class SurfaceDetails:
    def __init__(self,surface):
        self.surface=surface
        self.masks={}

    def get_mask(self,const_rect):
        if const_rect not in self.masks:
            sub = self.surface.subsurface(const_rect)
            mask = pygame.mask.from_surface(sub)
            self.masks[const_rect]=mask
        return self.masks.get(const_rect)

    def cc_masks(self):
        return pygame.mask.from_surface(self.surface).get_bounding_rects()


surfaces = {}


# EXPORT
def get_sheet(filename):
    if filename in surfaces:
        return surfaces.get(filename).surface
    #    if filename=='checkers':
    #        s=generate_checkers()
    #    else:
    s = pygame.image.load(filename)
    surfaces[filename] = SurfaceDetails(s)
    return s


# EXPORT
def get_sheet_name(sheet):
    for filename in surfaces.keys():
        if surfaces.get(filename).surface is sheet:
            return filename
    return ''


#EXPORT
def get_mask(sheet,const_rect):
    name = get_sheet_name(sheet)
    if not name:
        return None
    return surfaces.get(name).get_mask(const_rect)

#EXPORT
def cc_masks(sheet):
    name = get_sheet_name(sheet)
    if not name:
        return None
    return surfaces.get(name).cc_masks()

