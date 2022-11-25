#!/usr/bin/env python3
from noise import snoise2
from xml.dom.minidom import *


def quantize(v):
    v = int(v * 127 + 128)
    v = (v / 64) * 64
    return v


def gen_noise_txt():
    freq = 40.0
    lines = []
    for y in range(100):
        line = []
        for x in range(100):
            v = snoise2(x / freq, y / freq, 4)
            v = quantize(v) / 64 + 1
            line.append(str(v))
        lines.append(','.join(line))
    return ',\n'.join(lines)


def gen_map():
    doc = parseString('<map version="1.0" orientation="orthogonal" renderorder="right-down"/>')
    root = doc.childNodes[0]
    root.setAttribute('width', '100')
    root.setAttribute('height', '100')
    root.setAttribute('tilewidth', "32")
    root.setAttribute('tileheight', "32")
    root.setAttribute('nextobjectid', "1")
    ts = doc.createElement('tileset')
    ts.setAttribute('firstgid', '1')
    ts.setAttribute('name', 'tiles')
    ts.setAttribute('tilewidth', '32')
    ts.setAttribute('tileheight', '32')
    ts.setAttribute('tilecount', "16")
    ts.setAttribute('columns', "4")
    img = doc.createElement('image')
    img.setAttribute('source', 'terrain.png')
    img.setAttribute('width', '128')
    img.setAttribute('height', '128')
    ts.appendChild(img)
    root.appendChild(ts)
    layer = doc.createElement('layer')
    layer.setAttribute('name', 'layer')
    layer.setAttribute('width', '100')
    layer.setAttribute('height', '100')
    data = doc.createElement('data')
    data.setAttribute('encoding', 'csv')
    txt = gen_noise_txt()
    data.appendChild(doc.createTextNode(txt))
    layer.appendChild(data)
    root.appendChild(layer)
    open('ter.tmx', 'w').write(doc.toprettyxml())


if __name__ == '__main__':
    gen_map()
