#!/usr/bin/env python3
import re
import sys

def remove_quotes(m,line, is_list):
    s = m.start()
    e = m.end()
    val = line[s:e]
    if is_list:
        val = '[ ' + val[1:-1] + ' ]'
    else:
        val = val[1:-1]
    return line[0:s] + val + line[e:]


pat=re.compile(r'("\d+,\d+,\d+,\d+")')
num=re.compile(r'("\d+(?:\.\d+)?")')
for line in open(sys.argv[1],'r').readlines():
    line=line.rstrip()
    m=re.search(pat,line)
    if m:
        line=remove_quotes(m,line,True)
    m=re.search(num,line)
    if m:
        line=remove_quotes(m,line,False)
    print(line)
