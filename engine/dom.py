#!/usr/bin/env python
from xml.dom import minidom

class Element(object):
    def __init__(self,node):
        self.node=node
        
    def __getitem__(self,name):
        if self.node:
            if self.node.hasAttribute(name):
                return self.node.attributes[name].value
        return ''
        
    def children(self,tag):
        if not self.node:
            return []
        return [Element(e) for e in self.node.getElementsByTagName(tag)]
        
def parseFile(filename):
    return Element(minidom.parse(filename))
    
def parseString(s):
    return Element(minidom.parseString(s))
    