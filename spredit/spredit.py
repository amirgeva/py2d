#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from PyQt4 import QtCore, QtGui
from settings import loadWindowSettings, saveWindowSettings
from workspace import Workspace
import pygame
import utils
from engine import *

class PygameImageWidget(QtGui.QWidget):
    def __init__(self,surface=None,parent=None):
        super(PygameImageWidget,self).__init__(parent)
        self.data=''
        self.image=None
        if surface:
            self.setSurface(surface)
        
    def setSurface(self,surface):
        w=surface.get_width()
        h=surface.get_height()
        self.data=surface.get_buffer().raw
        self.image=QtGui.QImage(self.data,w,h,QtGui.QImage.Format_RGB32)

    def paintEvent(self,event):
        qp=QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(0,0,self.image)
        else:
            qp.fillRect(QtCore.QRectF(0,0,512,512),QtCore.Qt.DiagCrossPattern)
        qp.end()


class MainWindow(QtGui.QMainWindow):
    def __init__(self,screen,parent=None):
        super(MainWindow,self).__init__(parent)
        self.screen=screen
        self.setupMenu()
        self.setupWorkspace()
        self.workImage=None
        self.imageWidget=PygameImageWidget()
        self.setCentralWidget(self.imageWidget)
        loadWindowSettings(self)
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        self.screen.fill((0,0,0,255))
        pygame.draw.line(self.screen,pygame.Color(255,255,255,255),(0,0),(100,100))
        pygame.display.flip()

    def setupMenu(self):
        bar=self.menuBar()
        m=bar.addMenu('&File')
        m.addAction(QtGui.QAction('&Import Image',self,triggered=self.importImage))
        m.addAction(QtGui.QAction('&Save',self,shortcut='Ctrl+S',triggered=self.saveFile))
        m.addAction(QtGui.QAction('Save &As',self,triggered=self.saveAsFile))
        m.addAction(QtGui.QAction('E&xit',self,shortcut='Ctrl+Q',triggered=self.exitApp))
        
    def setupWorkspace(self):
        self.paneWorkspace=QtGui.QDockWidget("Workspace",self)
        self.paneWorkspace.setObjectName("Workspace")
        self.paneWorkspace.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.ws=Workspace(self.paneWorkspace,self)
        self.paneWorkspace.setWidget(self.ws)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,self.paneWorkspace)

    def importImage(self):
        filename=QtGui.QFileDialog.getOpenFileName()
        if filename:
            filename=str(filename)
            self.image=pygame.image.load(filename)
            self.image.convert_alpha()
            self.mask=pygame.mask.from_surface(self.image,1)
            self.rects=self.mask.get_bounding_rects()
            for r in self.rects:
                print r
            t=utils.generateBackground(self.image.get_size())
            t.blit(self.image,(0,0))
            self.imageWidget.setSurface(t)
    
    def saveFile(self):
        pass
    
    def saveAsFile(self):
        pass
    
    def exitApp(self):
        self.close()
    
    def moveEvent(self,event):
        super(MainWindow,self).moveEvent(event)
        saveWindowSettings(self)

    def resizeEvent(self,event):
        super(MainWindow,self).resizeEvent(event)
        saveWindowSettings(self)

    def moveEvent(self,event):
        super(MainWindow,self).moveEvent(event)
        saveWindowSettings(self)


def main():
    app=QtGui.QApplication(sys.argv)
    QtCore.QCoreApplication.setOrganizationName("MLGSoft")
    QtCore.QCoreApplication.setOrganizationDomain("mlgsoft.com")
    QtCore.QCoreApplication.setApplicationName("SprEdit")
    os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
    pygame.init()
    screen=pygame.display.set_mode((160,120),pygame.DOUBLEBUF)
    pygame.display.set_caption('SprEdit Animation','SprEdit Animation')
    
    w=MainWindow(screen)
    w.show()
    app.exec_()

if __name__=='__main__':
    main()
