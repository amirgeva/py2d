#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os

from engine import *
from engine.utils import Rect, Point
from engine.subsheet import Subsheet
from engine.cache import cc_masks, get_sheet
from engine.app import Application
import json
import pygame


class AnimationFrame(object):
    def __init__(self):
        self.rect = None
        self.duration = 0.0
        self.sprite = None


class SpriteSheet(QtWidgets.QWidget):
    def __init__(self, sheet_name, parent=None):
        super(SpriteSheet, self).__init__(parent)
        self.mainwin = parent
        self.sheet = None
        self.rects = []
        self.texture = None
        self.highlight = None
        if sheet_name:
            self.load_image(sheet_name)

    def load_image(self, sheet_name):
        sheet_name = os.path.normpath(sheet_name)
        self.rects = []
        self.sheet = QtGui.QImage(sheet_name)
        self.setMinimumWidth(self.sheet.width())
        self.setMinimumHeight(self.sheet.height())
        self.texture = get_sheet(sheet_name)
        self.rects = []
        rects = cc_masks(self.texture)
        for r in rects:
            self.rects.append(Rect(r.left,r.top,r.right,r.bottom))


    def set_highlight_rect(self, r):
        self.highlight = r
        self.update()

    def clear_highlight(self):
        self.highlight = None
        self.update()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        for r in self.rects:
            if r.right() > x >= r.left() and r.bottom() > y >= r.top():
                self.mainwin.onRect(r)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.sheet:
            qp.drawImage(QtCore.QPoint(0, 0), self.sheet)
        qp.setBrush(QtCore.Qt.NoBrush)
        qp.setPen(QtGui.QColor(255, 0, 0))
        for r in self.rects:
            qp.drawRect(r.left(), r.top(), r.width(), r.height())
        qp.setPen(QtGui.QColor(0, 255, 0))
        if self.highlight:
            r = self.highlight
            qp.drawRect(r.left(), r.top(), r.width(), r.height())
        qp.end()


class SequencesList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(SequencesList, self).__init__(parent)
        self.mainwin = parent
        self.itemSelectionChanged.connect(self.onSel)

    def onSel(self):
        sel = self.selectedItems()
        if len(sel) == 1:
            self.mainwin.set_current_sequence(sel[0].text())

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        newAction = menu.addAction("New Sequence")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == newAction:
            (name, ok) = QtWidgets.QInputDialog.getText(self, "Sequence Name", "Name")
            if ok:
                self.mainwin.add_sequence(name)
                row = self.count()
                self.addItem(name)
                item = self.item(row)
                self.setCurrentItem(item)


class SequenceRectList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(SequenceRectList, self).__init__(parent)
        self.mainwin = parent
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.itemSelectionChanged.connect(self.onSel)

    def onSel(self):
        sel = self.currentRow()
        self.mainwin.set_current_frame(sel)

    def addRect(self, rect, duration):
        row = self.count()
        self.addItem('{}, {}'.format(rect, duration))
        item = self.item(row)
        self.setCurrentItem(item)

    def update_items(self, seq):
        self.clear()
        for frame in seq:
            self.addRect(frame.rect, frame.duration)

    def onItemDoubleClicked(self, item):
        self.mainwin.edit_duration(self.row(item))

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            for item in self.selectedItems():
                self.mainwin.remove_sprite(self.row(item))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, sheet_name, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setup_menu()
        self.sheet_name = sheet_name
        self.sheet = SpriteSheet(sheet_name, self)
        self.setCentralWidget(self.sheet)
        self.paneSequences = QtWidgets.QDockWidget("Sequences", self)
        self.paneSequences.setObjectName("Sequences")
        self.paneSequences.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.sequences = SequencesList(self)
        self.sequences.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.paneSequences.setWidget(self.sequences)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.paneSequences)

        self.paneRects = QtWidgets.QDockWidget("Sprites", self)
        self.paneRects.setObjectName("Sprites")
        self.paneRects.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.sprites = SequenceRectList(self)
        self.sprites.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.paneRects.setWidget(self.sprites)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.paneRects)

        self.current_sequence = ''
        self.current_frame = -1
        self.seq_dict = {}

        self.animation_frame = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.onTimer)
        self.timer.start(100)
        self.frame_time_left=0.0

    def closeEvent(self, *args, **kwargs):
        self.timer.stop()
        super(MainWindow,self).closeEvent(*args,**kwargs)

    def onTimer(self):
        get_screen().fill((0,0,0))
        if not self.current_sequence:
            return
        seq = self.seq_dict.get(self.current_sequence)
        if not seq:
            return
        self.frame_time_left = self.frame_time_left - 0.1
        if self.frame_time_left <= 0.0:
            if self.animation_frame < len(seq):
                frame = seq[self.animation_frame]
                self.animation_frame += 1
                if self.animation_frame >= len(seq):
                    self.animation_frame = 0
                self.frame_time_left = seq[self.animation_frame].duration
                frame.sprite.blit(get_screen(),Point(0,0))
                pygame.display.flip()
            else:
                self.animation_frame = 0
                pygame.display.flip()

    def set_current_sequence(self, name):
        self.current_sequence = name
        self.sprites.update_items(self.seq_dict[name])

    def set_current_frame(self, frame_index):
        if self.current_sequence:
            seq = self.seq_dict[self.current_sequence]
            if frame_index < len(seq):
                self.sheet.set_highlight_rect(seq[frame_index].rect)
            else:
                self.sheet.clear_highlight()

    def add_sequence(self, name):
        self.seq_dict[name] = []

    def remove_sprite(self, index):
        seq = self.seq_dict[self.current_sequence]
        del seq[index]
        self.sprites.update_items(seq)

    def edit_duration(self, index):
        seq = self.seq_dict[self.current_sequence]
        duration = float(seq[index].duration)
        (duration, ok) = QtWidgets.QInputDialog.getDouble(self, 'Duration', 'Duration', duration)
        if ok:
            seq[index].duration = duration
            self.sprites.update_items(seq)

    def onRect(self, r):
        si = self.sequences.selectedItems()
        if len(si) == 1:
            name = si[0].text()
            frame = AnimationFrame()
            frame.rect = Rect(r)
            frame.duration = 0.1
            frame.sprite = Subsheet(self.sheet.texture, r)
            self.seq_dict[name].append(frame)
            self.sprites.update_items(self.seq_dict[name])

    def setup_menu(self):
        mb = self.menuBar()
        m = mb.addMenu('&File')

        new_action = QtWidgets.QAction(QtGui.QIcon('new.png'), '&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.setStatusTip('New Sprite')
        new_action.triggered.connect(self.on_new)
        m.addAction(new_action)

        open_action = QtWidgets.QAction(QtGui.QIcon('open.png'), '&Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open Sprite')
        open_action.triggered.connect(self.on_open)
        m.addAction(open_action)

        save_action = QtWidgets.QAction(QtGui.QIcon('save.png'), '&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save Sprite')
        save_action.triggered.connect(self.on_save)
        m.addAction(save_action)

        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        m.addAction(exitAction)

    def on_new(self):
        (filename, ok) = QtWidgets.QFileDialog.getOpenFileName(self, "Sprite Image Sheet", os.getcwd(), "*.png",
                                                                    "*.png")
        if ok:
            self.seq_dict = {}
            self.sequences.clear()
            self.sprites.clear()
            self.sheet_name = filename
            self.sheet.load_image(filename)

    def on_open(self):
        (filename, ok) = QtWidgets.QFileDialog.getOpenFileName(self, "Load Sprite", os.getcwd(), "*.json",
                                                                    "*.json")
        if ok and filename:
            self.current_sequence = ''
            root = json.load(open(filename, 'r'))
            self.sheet_name = root.get('Image')
            self.seq_dict = {}
            self.sequences.clear()
            self.sprites.clear()
            self.sheet.load_image(self.sheet_name)
            for seq in root.get('Sequences'):
                name = seq.get('Name')
                self.sequences.addItem(name)
                frames = []
                for frame_dict in seq.get('Frames'):
                    frame = AnimationFrame()
                    r = tuple(frame_dict.get('Rect'))
                    frame.duration = frame_dict.get('Duration')
                    r = Rect(r[0],r[1],r[2],r[3])
                    frame.rect = r
                    frame.sprite = Subsheet(self.sheet.texture, r)
                    frames.append(frame)
                self.seq_dict[name] = frames
                self.animation_frame = 0
            self.current_sequence = self.sequences.item(0).text()
            self.current_frame = 0
            self.sequences.setCurrentItem(self.sequences.item(0))

    def on_save(self):
        (filename, filter) = QtWidgets.QFileDialog.getSaveFileName(self, "Save", os.getcwd(), "*.json", "*.json")
        if filename:
            imagename = os.path.basename(self.sheet_name)
            root = {"Image": imagename, "Flags": ''}
            sequences = []
            for name in self.seq_dict:
                frames = []
                seq = self.seq_dict.get(name)
                for frame in seq:
                    frames.append({"Rect": frame.rect.coords(), "Duration": frame.duration})
                sequences.append({"Name": name, "BaseVelocity": 1.0, "Frames": frames})
            root['Sequences'] = sequences
            open(filename, 'w').write(json.dumps(root, indent=4))


def main():
    arg = ''
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    pygame.init()
    a=Application((640,480))
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(arg)
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
