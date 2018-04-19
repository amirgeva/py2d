#!/usr/bin/env python3
from PyQt4 import QtCore, QtGui
import sys

sys.path.append('..')
sys.path.append('.')
from engine import *
from engine.utils import Rect
import uis
import itertools
import oglblit


class SequenceSettingsDialog(QtGui.QDialog):
    def __init__(self, seq, parent=None):
        super(SequenceSettingsDialog, self).__init__(parent)
        uis.loadDialog('seqset', self)
        self.seq = seq
        for spr in seq:
            self.durationsList.addItem(str(spr.duration))
            item = self.durationsList.item(self.durationsList.count() - 1)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        self.durationsList.itemChanged.connect(self.itemChanged)

    def itemChanged(self, item):
        print("Item changed")

    def accept(self):
        for i in range(self.durationsList.count()):
            item = self.durationsList.item(i)
            try:
                val = float(item.text())
                self.seq[i].duration = val
            except ValueError:
                pass
        return super(SequenceSettingsDialog, self).accept()


class SequencesDialog(QtGui.QDialog):
    def __init__(self, sheet, sprite, parent=None):
        super(SequencesDialog, self).__init__(parent)
        uis.loadDialog('spriteseq', self)
        self.sheet = sheet
        self.filename = ""
        self.addButton.clicked.connect(self.addSequence)
        self.saveButton.clicked.connect(self.saveSprite)
        self.sequenceList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.sequenceList.customContextMenuRequested.connect(self.ctxMenu)
        self.sequenceList.currentItemChanged.connect(self.changeCurrent)
        if sprite:
            self.sprite = sprite
            for seq in self.sprite.sequences:
                self.sequenceList.addItem(seq)
            self.sequenceList.setCurrentRow(0)
        else:
            self.sprite = AnimatedSprite()

    def advance(self, dt):
        if self.sprite:
            self.sprite.advance(dt, vector2(0.0, 0.0))

    def draw(self, pos):
        if self.sprite:
            self.sprite.draw(pos)

    def changeCurrent(self, cur, prev):
        if self.sprite:
            self.sprite.set_active_sequence(self.getCurrentSequenceName())

    def condenseSheet(self):
        pass

    def saveSprite(self):
        if not self.filename:
            self.filename = QtGui.QFileDialog.getSaveFileName(filter="JSON Files (*.json)")
            if not self.filename:
                return
        s = self.sprite.serialize()
        open(self.filename, 'w').write(s)

    def addSequence(self):
        r = QtGui.QInputDialog.getText(None, "New Sequence", "Enter Name")
        if r[1]:
            name = str(r[0])
            self.sequenceList.addItem(name)
            self.sprite.add_sequence(AnimationSequence(name))
            self.sequenceList.setCurrentRow(self.sequenceList.count() - 1)

    def addSprite(self, rect):
        seq = self.getCurrentSequence()
        if not seq is None:
            seq.add_sprite(oglblit.get_sprite(self.sheet, rect.tl.x, rect.tl.y, rect.br.x, rect.br.y), 0.1)
        else:
            print("addSprite: no active sequence")

    def ctxMenu(self, pos):
        menu = QtGui.QMenu()
        menu.addAction(QtGui.QAction('Clear', self, triggered=self.clearSequence))
        menu.addAction(QtGui.QAction('Edit', self, triggered=self.editSequence))
        menu.exec_(self.sequenceList.mapToGlobal(pos))

    def getCurrentSequenceName(self):
        item = self.sequenceList.currentItem()
        if item:
            return str(item.text())
        return ""

    def getCurrentSequence(self):
        name = self.getCurrentSequenceName()
        if name:
            return self.sprite.get_sequence_by_name(name)
        return None

    def clearSequence(self):
        seq = self.getCurrentSequence()
        if seq:
            seq.clear()

    def editSequence(self):
        seq = self.getCurrentSequence()
        if seq:
            d = SequenceSettingsDialog(seq)
            d.exec_()


class TransparencyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(TransparencyDialog, self).__init__(parent)
        uis.loadDialog('transparency', self)
        self.type = ''
        self.grid = False
        self.Color.setDisabled(True)
        self.Offset.setDisabled(True)
        self.Size.setDisabled(True)
        self.ColorKeyManual.toggled.connect(self.manual_selected)
        self.ColorKeyAuto.toggled.connect(self.auto_selected)
        self.Grid.toggled.connect(self.grid_selected)

    def accept(self):
        if len(self.type) > 0:
            super(TransparencyDialog, self).accept()

    def manual_selected(self, state):
        self.Color.setEnabled(state)
        self.type = 'Manual'

    def auto_selected(self, state):
        self.type = 'Auto'

    def grid_selected(self, state):
        self.grid = state
        self.Offset.setEnabled(state)
        self.Size.setEnabled(state)


class SprEdit:
    def __init__(self, filename):
        super(SprEdit, self).__init__((1280, 720))
        self.sheet = None
        self.sprite = None
        self.seqdlg = None
        self.rects = []
        self.bg = get_sheet('checkers')
        if filename.endswith('.json'):
            self.load_sprite(filename)
        else:
            self.load_sheet(filename)
        # self.seqdlg=SequencesDialog(self.sheet,self.sprite)
        # self.seqdlg.show()

    def load_sprite(self, filename):
        self.sprite = load_file(filename)
        self.load_sheet(self.sprite.sheet)

    def load_sheet(self, filename):
        self.sheet = get_sheet(filename)
        n = oglblit.get_bounding_box_count(self.sheet)
        for bi in range(n):
            x0 = oglblit.get_bounding_box_coord(self.sheet, bi, 0)
            y0 = oglblit.get_bounding_box_coord(self.sheet, bi, 1)
            x1 = oglblit.get_bounding_box_coord(self.sheet, bi, 2)
            y1 = oglblit.get_bounding_box_coord(self.sheet, bi, 3)
            self.rects.append(Rect(x0, y0, x1, y1))

        self.draw()
        self.flip()
        # if not is_transparent(self.sheet):
        #     d=TransparencyDialog()
        #     d.exec_()
        #     if d.type=='Manual':
        #         self.manual_alpha(parse_color(d.Color.text()))
        #     elif d.type=='Auto':
        #         self.auto_alpha()
        #     if d.grid and self.sheet:
        #         self.grid_rects(parse_point(d.Offset.text()),parse_point(d.Size.text()))
        #
        # else:
        #     m=pygame.mask.from_surface(self.sheet)
        #     self.rects=m.get_bounding_rects()

    # def manual_alpha(self,color):
    #     a=pygame.Color(color.r,color.g,color.b,0)
    #     for p in all_pixels(self.sheet):
    #         if color==self.sheet.get_at(p):
    #             self.sheet.set_at(p,a)
    #     m=pygame.mask.from_surface(self.sheet)
    #     self.rects=m.get_bounding_rects()
    #
    # def auto_alpha(self):
    #     h={}
    #     mc=None
    #     mx=0
    #     for p in all_pixels(self.sheet):
    #         c=tuple(self.sheet.get_at(p))
    #         if not c in h:
    #             h[c]=1
    #         else:
    #             n=1+h.get(c)
    #             if n>mx:
    #                 mx=n
    #                 mc=c
    #             h[c]=n
    #     self.manual_alpha(pygame.Color(mc[0],mc[1],mc[2],mc[3]))
    #
    # def grid_rects(self,offset,size):
    #     self.rects=[]
    #     x=offset[0]
    #     y=offset[1]
    #     while y<(self.sheet.get_height()-size[1]):
    #         while x<(self.sheet.get_width()-size[0]):
    #             self.rects.append(pygame.Rect(x,y,size[0],size[1]))
    #             x=x+size[0]+offset[0]
    #         x=offset[0]
    #         y=y+size[1]+offset[1]

    def find_rect(self, pos):
        for r in self.rects:
            if r.collidepoint(pos):
                return r
        return None

    def onClick(self, pos):
        r = self.find_rect(pos)
        if r:
            self.seqdlg.addSprite(r)

    def draw(self):
        pass
        # self.screen.blit(self.bg,(0,0))
        # if self.sheet:
        #     self.screen.blit(self.sheet,(0,0))
        # for r in self.rects:
        #     pygame.draw.rect(self.screen,pygame.Color(255,0,0,255),r,1)
        # if self.seqdlg:
        #     self.seqdlg.draw(self.screen,(self.sheet.get_width(),0))


class SpriteSheet(QtGui.QWidget):
    def __init__(self, sheet_name, parent=None):
        super(SpriteSheet, self).__init__(parent)
        self.mainwin = parent
        self.sheet = QtGui.QImage(sheet_name)
        self.setMinimumWidth(self.sheet.width())
        self.setMinimumHeight(self.sheet.height())
        self.texture = oglblit.load_sprites(sheet_name)
        self.rects = []
        n = oglblit.get_bounding_box_count(self.texture)
        for i in range(n):
            x0 = oglblit.get_bounding_box_coord(self.texture, i, 0)
            y0 = oglblit.get_bounding_box_coord(self.texture, i, 1)
            x1 = oglblit.get_bounding_box_coord(self.texture, i, 2)
            y1 = oglblit.get_bounding_box_coord(self.texture, i, 3)
            self.rects.append((x0, y0, x1, y1))

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        for r in self.rects:
            if r[2] > x >= r[0] and r[3] > y >= r[1]:
                self.mainwin.onRect(r)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(QtCore.QPoint(0, 0), self.sheet)
        qp.setBrush(QtCore.Qt.NoBrush)
        qp.setPen(QtGui.QColor(255, 0, 0))
        for r in self.rects:
            qp.drawRect(r[0], r[1], r[2] - r[0], r[3] - r[1])
        qp.end()


class SequencesList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(SequencesList, self).__init__(parent)
        self.mainwin = parent
        self.itemSelectionChanged.connect(self.onSel)

    def onSel(self):
        sel = self.selectedItems()
        if len(sel)==1:
            self.mainwin.set_current_sequence(sel[0].text())

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        newAction = menu.addAction("New Sequence")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == newAction:
            (name, ok) = QtGui.QInputDialog.getText(self, "Sequence Name", "Name")
            if ok:
                self.mainwin.add_sequence(name)
                self.addItem(name)


class SequenceRectList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(SequenceRectList, self).__init__(parent)
        self.mainwin = parent
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def addRect(self, rect, duration):
        self.addItem('{}, {}'.format(rect, duration))

    def update_items(self, s):
        self.clear()
        for r,d in s:
            self.addRect(r,d)

    def onItemDoubleClicked(self, item):
        self.mainwin.edit_duration(self.row(item))

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            for item in self.selectedItems():
                self.mainwin.remove_sprite(self.row(item))


class MainWindow(QtGui.QMainWindow):
    def __init__(self, sheet_name, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_menu()
        self.sheet = SpriteSheet(sheet_name, self)
        self.setCentralWidget(self.sheet)
        self.paneSequences = QtGui.QDockWidget("Sequences", self)
        self.paneSequences.setObjectName("Sequences")
        self.paneSequences.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.sequences = SequencesList(self)
        self.sequences.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.paneSequences.setWidget(self.sequences)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.paneSequences)

        self.paneRects = QtGui.QDockWidget("Sprites", self)
        self.paneRects.setObjectName("Sprites")
        self.paneRects.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.sprites = SequenceRectList(self)
        self.sprites.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.paneRects.setWidget(self.sprites)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.paneRects)

        self.current_sequence = ''
        self.seq_dict = {}


    def set_current_sequence(self, name):
        self.current_sequence = name
        self.sprites.update_items(self.seq_dict[name])

    def add_sequence(self,name):
        self.seq_dict[name]=[]

    def remove_sprite(self, index):
        seq = self.seq_dict[self.current_sequence]
        del seq[index]
        self.sprites.update_items(seq)

    def edit_duration(self, index):
        seq = self.seq_dict[self.current_sequence]
        duration = float(seq[index][1])
        (duration, ok) = QtGui.QInputDialog.getDouble(self, 'Duration', 'Duration', duration)
        if ok:
            seq[index]=(seq[index][0], duration)
            self.sprites.update_items(seq)

    def onRect(self,r):
        si=self.sequences.selectedItems()
        if len(si)==1:
            name = si[0].text()
            self.seq_dict[name].append((r,0.1))
            self.sprites.update_items(self.seq_dict[name])

    def setup_menu(self):
        mb = self.menuBar()
        m = mb.addMenu('&File')

        open_action = QtGui.QAction(QtGui.QIcon('open.png'), '&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open Sprite')
        open_action.triggered.connect(self.on_open)
        m.addAction(open_action)

        save_action = QtGui.QAction(QtGui.QIcon('save.png'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save Sprite')
        save_action.triggered.connect(self.on_save)
        m.addAction(save_action)

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        m.addAction(exitAction)

    def on_open(self):
        pass

    def on_save(self):
        pass

def main():
    if len(sys.argv) < 2:
        print("Usage: spredit.py <image>|<sprite>")
    else:
        oglblit.init(320, 320, 1)
        app = QtGui.QApplication(sys.argv)
        sheet_name = sys.argv[1]
        w = MainWindow(sheet_name)
        w.show()
        app.exec_()
        oglblit.deinit()


if __name__ == '__main__':
    main()
