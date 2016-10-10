#!/usr/bin/env python
from PyQt4 import QtCore, QtGui
import sys
sys.path.append('..')
sys.path.append('.')
from engine import *
import uis
import pygame
from pygame.math import Vector2
import itertools

qapp=None
sheet_name=""
#osnat
class SequenceSettingsDialog(QtGui.QDialog):
    def __init__(self,seq,parent=None):
        super(SequenceSettingsDialog,self).__init__(parent)
        uis.loadDialog('seqset',self)
        self.seq=seq
        for spr in seq:
            self.durationsList.addItem(str(spr.duration))
            item=self.durationsList.item(self.durationsList.count()-1)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsEnabled)
        self.durationsList.itemChanged.connect(self.itemChanged)
        
    def itemChanged(self,item):
        print "Item changed"
        
    def accept(self):
        for i in xrange(0,self.durationsList.count()):
            item=self.durationsList.item(i)
            try:
                val=float(item.text())
                self.seq[i].duration=val
            except ValueError:
                pass
        return super(SequenceSettingsDialog,self).accept()
        

class SequencesDialog(QtGui.QDialog):
    def __init__(self,sheet,parent=None):
        super(SequencesDialog,self).__init__(parent)
        uis.loadDialog('spriteseq',self)
        self.sheet=sheet
        self.filename=""
        self.addButton.clicked.connect(self.addSequence)
        self.saveButton.clicked.connect(self.saveSprite)
        self.sequenceList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sequenceList.customContextMenuRequested.connect(self.ctxMenu)
        self.sequenceList.currentItemChanged.connect(self.changeCurrent)
        self.sprite=AnimatedSprite(sheet_name)
        
    def advance(self,dt):
        if self.sprite:
            self.sprite.advance(dt,Vector2(0.0,0.0))
    
    def draw(self,screen,pos):
        if self.sprite:
            self.sprite.draw(screen,pos)
        
    def changeCurrent(self,cur,prev):
        if self.sprite:
            self.sprite.set_active_sequence(self.getCurrentSequenceName())
            
    def saveSprite(self):
        if not self.filename:
            self.filename=QtGui.QFileDialog.getSaveFileName(filter="XML Files (*.xml)")
            if not self.filename:
                return
        s=self.sprite.serialize()
        open(self.filename,'w').write(s)
        
    def addSequence(self):
        r=QtGui.QInputDialog.getText(None,"New Sequence","Enter Name")
        if r[1]:
            name=str(r[0])
            self.sequenceList.addItem(name)
            self.sprite.add_sequence(AnimationSequence(name))
            self.sequenceList.setCurrentRow(self.sequenceList.count()-1)

    def addSprite(self,rect):
        seq=self.getCurrentSequence()
        if not seq is None:
            seq.add_sprite(Sprite(self.sheet,rect,0.1))
        else:
            print "addSprite: no active sequence"

    def ctxMenu(self,pos):
        menu=QtGui.QMenu()
        menu.addAction(QtGui.QAction('Clear',self,triggered=self.clearSequence))
        menu.addAction(QtGui.QAction('Edit',self,triggered=self.editSequence))
        menu.exec_(self.sequenceList.mapToGlobal(pos))
        
    def getCurrentSequenceName(self):
        item=self.sequenceList.currentItem()
        if item:
            return str(item.text())
        return ""
        
    def getCurrentSequence(self):
        name=self.getCurrentSequenceName()
        if name:
            return self.sprite.get_sequence_by_name(name)
        return None
        
    def clearSequence(self):
        seq=self.getCurrentSequence()
        if seq:
            seq.clear()
            
    def editSequence(self):
        seq=self.getCurrentSequence()
        if seq:
            d=SequenceSettingsDialog(seq)
            d.exec_()
            
    

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
        self.seqdlg=None
        self.rects=[]
        self.bg=get_surface('checkers')
        if filename.endswith('.xml'):
            self.load_sprite(filename)
        else:
            self.load_sheet(filename)
        self.seqdlg=SequencesDialog(self.sheet)
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
            
    def find_rect(self,pos):
        for r in self.rects:
            if r.collidepoint(pos):
                return r
        return None
            
    def onClick(self,pos):
        r=self.find_rect(pos)
        if r:
            self.seqdlg.addSprite(r)
        
    def draw(self):        
        self.screen.blit(self.bg,(0,0))
        if self.sheet:
            self.screen.blit(self.sheet,(0,0))
        for r in self.rects:
            pygame.draw.rect(self.screen,pygame.Color(255,0,0,255),r,1)
        if self.seqdlg:
            self.seqdlg.draw(self.screen,(self.sheet.get_width(),0))
        
    def loop(self,dt):
        qapp.processEvents()
        self.seqdlg.advance(dt)
        self.draw()

def main():
    if len(sys.argv)<2:
        print "Usage: spredit.py <image>|<sprite>"
    else:
        global qapp
        qapp=QtGui.QApplication(sys.argv)
        global sheet_name
        sheet_name=sys.argv[1]
        app=SprEdit(sheet_name)
        app.run()

if __name__=='__main__':
    main()
