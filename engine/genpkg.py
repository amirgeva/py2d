#!/usr/bin/env python3
import os
import re

sym_pat = re.compile(r'(?:class|def) (\w+)')

names = []
files = os.listdir('.')
files = [f for f in files if f.endswith('.py')]
for fname in files:
    base = os.path.splitext(fname)[0]
    export = False
    for line in open(fname, 'r').readlines():
        if export:
            if not line.startswith('@'):
                export = False
                m = re.match(sym_pat, line)
                if m:
                    name = m.groups()[0]
                    names.append((base, name))
        if line.startswith('# EXPORT'):
            export = True
f = open('__init__.py', 'w')
allnames = []
for p in names:
    f.write('from engine.{} import {}\n'.format(p[0], p[1]))
    allnames.append(p[1])

f.write('from engine.keycodes import *\n\n')

f.write('\n__all__ = [ ')
f.write("'{}'".format("','".join(allnames)))
f.write(' ]\n\n')
