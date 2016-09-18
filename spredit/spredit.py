#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
import sys
sys.path.append('..')
sys.path.append('.')
from engine import *
import uis
import pygame
import itertools

qapp=None

class SequencesDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(SequencesDialog,self).__init__(parent)
        uis.loadDialog('spriteseq',self)
        self.addButton.clicked.connect(self.addSequence)
        self.sequenceList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sequenceList.customContextMenuRequested.connect(self.ctxMenu)
        self.sprite=AnimatedSprite()
        
    def addSequence(self):
        r=QtGui.QInputDialog.getText(None,"New Sequence","Enter Name")
        if r[1]:
            name=str(r[0])
            self.sequenceList.addItem(name)
            self.sprite.add_sequence(AnimationSequence(name))
            
    def ctxMenu(self,pos):
        menu=QtGui.QMenu()
        menu.addAction(QtGui.QAction('Clear',self,triggered=self.clearSequence))
        menu.exec_(self.sequenceList.mapToGlobal(pos))
        
    def getCurrentSequence(self):
        return str(self.sequenceList.currentItem().text())
        
    def clearSequence(self):
        name=self.getCurrentSequence()
        if name:
            seq=self.sprite.get_sequence_by_name(name)
            if seq:
                seq.clear()
            
    

class TransparencyDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        super(TransparencyDialog,self).__init__(parent)
        uis.loadDialog('transparency',self)
        self.type=''
        self.grid=False
        self.Color.setDisabled(True)
        self.Offset.setDisabled(True)
        self.Size.setDisabled(True)
        self.ColorKeyManual.toggled.connect(self.manual_selected)
        self.ColorKeyAuto.toggled.connect(self.auto_selected)
        self.Grid.toggled.connect(self.grid_selected)
        
    def accept(self):
        if len(self.type)>0:
            super(TransparencyDialog,self).accept()
        
    def manual_selected(self,state):
        self.Color.setEnabled(state)
        self.type='Manual'

    def auto_selected(self,state):
        self.type='Auto'
    
    def grid_selected(self,state):
        self.grid=state
        self.Offset.setEnabled(state)
        self.Size.setEnabled(state)


class SprEdit(Application):
    def __init__(self,filename):
        super(SprEdit,self).__init__((1280,720))
        self.sheet=None
        self.rects=[]
        self.bg=get_surface('checkers')
        if filename.endswith('.xml'):
            self.load_sprite(filename)
        else:
            self.load_sheet(filename)
        self.seqdlg=SequencesDialog()
        self.seqdlg.show()
            
    def load_sheet(self,filename):
        self.sheet=get_surface(filename)
        self.draw()
        self.flip()
        if not is_transparent(self.sheet):
            d=TransparencyDialog()
            d.exec_()
            if d.type=='Manual':
                self.manual_alpha(parse_color(d.Color.text()))
            elif d.type=='Auto':
                self.auto_alpha()
            else:
                self.sheet=None
            if d.grid and self.sheet:
                self.grid_rects(parse_point(d.Offset.text()),parse_point(d.Size.text()))

        else:
            m=pygame.mask.from_surface(self.sheet)
            self.rects=m.get_bounding_rects()

                
    def manual_alpha(self,color):
        a=pygame.Color(color.r,color.g,color.b,0)
        for p in all_pixels(self.sheet):
            if color==self.sheet.get_at(p):
                self.sheet.set_at(p,a)
        m=pygame.mask.from_surface(self.sheet)
        self.rects=m.get_bounding_rects()
                
    def auto_alpha(self):
        h={}
        mc=None
        mx=0
        for p in all_pixels(self.sheet):
            c=tuple(self.sheet.get_at(p))
            if not c in h:
                h[c]=1
            else:
                n=1+h.get(c)
                if n>mx:
                    mx=n
                    mc=c
                h[c]=n
        self.manual_alpha(pygame.Color(mc[0],mc[1],mc[2],mc[3]))
        
    def grid_rects(self,offset,size):
        self.rects=[]
        x=offset[0]
        y=offset[1]
        while y<(self.sheet.get_height()-size[1]):
            while x<(self.sheet.get_width()-size[0]):
                self.rects.append(pygame.Rect(x,y,size[0],size[1]))
                x=x+size[0]+offset[0]
            x=offset[0]
            y=y+size[1]+offset[1]
            
        
    def draw(self):        
        self.screen.blit(self.bg,(0,0))
        if self.sheet:
            self.screen.blit(self.sheet,(0,0))
        for r in self.rects:
            pygame.draw.rect(self.screen,pygame.Color(255,0,0,255),r,1)
        
    def loop(self,dt):
        qapp.processEvents()
        self.draw()

def main():
    if len(sys.argv)<2:
        print "Usage: spredit.py <image>|<sprite>"
    global qapp
    qapp=QtGui.QApplication(sys.argv)
    app=SprEdit(sys.argv[1])
    app.run()

if __name__=='__main__':
    main()
