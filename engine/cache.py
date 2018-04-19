import oglblit


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


surfaces = {}


# EXPORT
def get_sheet(filename):
    if filename in surfaces:
        return surfaces.get(filename)
    #    if filename=='checkers':
    #        s=generate_checkers()
    #    else:
    s = oglblit.load_sprites(filename)
    surfaces[filename] = s
    return s


# EXPORT
def get_sheet_name(sheet):
    for filename in surfaces.keys():
        if surfaces.get(filename) == sheet:
            return filename
    return ''

