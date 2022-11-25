import sys
import glob
from PIL import Image
from cv2 import cv2
import numpy as np
import cmdline as cmd

gap = 0
output = 'tiles.png'


def set_gap(param):
    global gap
    gap = int(param)


def set_output(param):
    global output
    output = param


def main():
    cmd.flag('gap', True, set_gap)
    cmd.flag('out', True, set_output)
    cmd.parse()
    print(f"Combining images with gap {gap}")
    x = gap
    y = gap
    rects = {}
    for arg in cmd.arguments:
        filenames = glob.glob(arg)
        for filename in filenames:
            pimg = Image.open(filename).convert('RGBA')
            img = np.array(pimg)
            r = img[:, :, 0]
            g = img[:, :, 1]
            b = img[:, :, 2]
            a = img[:, :, 3]
            img = cv2.merge((b, g, r, a))
            h, w = img.shape[0], img.shape[1]
            r = (x, y, x + w, y + h)
            rects[r] = img
            x = x + w + gap
            if x > 200:
                x = gap
                y = y + h + gap
    if len(rects) == 0:
        print("No input images specified")
    else:
        outimg = np.zeros((y + h + gap, 300, 4), dtype=np.uint8)
        for r in rects.keys():
            img = rects.get(r)
            outimg[r[1]:r[3], r[0]:r[2], :] = img
        cv2.imwrite(output, outimg)


if __name__ == '__main__':
    main()
