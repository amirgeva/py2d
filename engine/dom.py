#!/usr/bin/env python
from xml.dom import minidom,Node

class Element(object):
    def __init__(self,node):
        self.node=node
        self.text=''
        for c in self.node.childNodes:
            if c.nodeType == Node.TEXT_NODE:
                self.text=c.nodeValue

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
    node=minidom.parse(filename)
    return Element(node.childNodes[0])

def parseString(s):
    node=minidom.parseString(s)
    return Element(node.childNodes[0])
