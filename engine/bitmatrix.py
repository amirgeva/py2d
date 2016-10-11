#!/usr/bin/env python
from bitarray import bitarray


class BitMatrix(object):
    def __init__(self,width,height,init=True):
        self.sizes=(width,height)
        self.rows=[bitarray(width) for i in xrange(0,height)]
        if init:
            self.clear()
        
    def width(self):
        return self.sizes[0]
        
    def height(self):
        return self.sizes[1]
        
    def get(self,x,y):
        if x<0 or x>=self.width() or y<0 or y>=self.height():
            return False
        row=self.rows[y]
        return row[x]
        
    def set(self,x,y,v):
        if x>=0 and x<self.width() and y>=0 and y<self.height():
            row=self.rows[y]
            row[x]=v
        
    def clear(self):
        for row in self.rows:
            row.setall(False)
            
    def setall(self):
        for row in self.rows:
            row.setall(True)

class BFBitMatrix(object):
    def __init__(self,width,height):
        self.sizes=(width,height)
        self.data=[False]*(width*height)
        
    def width(self):
        return self.sizes[0]
        
    def height(self):
        return self.sizes[1]
        
    def get(self,x,y):
        if x<0 or x>=self.width() or y<0 or y>=self.height():
            return False
        return self.data[y*self.width()+x]
        
    def set(self,x,y,v):
        if x>=0 and x<self.width() and y>=0 and y<self.height():
            self.data[y*self.width()+x]=v
        
    def clear(self):
        self.data=[False]*(self.width()*self.height())
            
    def setall(self):
        self.data=[True]*(self.width()*self.height())
            



def unit_test():
    def compare(m1,m2):
        if m1.width()!=m2.width():
            return False
        if m1.height()!=m2.height():
            return False
        for y in xrange(0,m1.height()):
            for x in xrange(0,m1.width()):
                if m1.get(x,y)!=m2.get(x,y):
                    return False
        return True
    from random import randint,seed
    seed(1)
    try:
        S=18
        N=1000
        m1=BitMatrix(S,S)
        m2=BFBitMatrix(S,S)
        for i in xrange(0,N):
            if not compare(m1,m2):
                raise Exception("Failed {}".format(i))
            x=randint(0,S-1)
            y=randint(0,S-1)
            v=(randint(0,1)>0)
            m1.set(x,y,v)
            m2.set(x,y,v)
        raise Exception("Test successful")
    except Exception,e:
        print e


if __name__=='__main__':
    unit_test()