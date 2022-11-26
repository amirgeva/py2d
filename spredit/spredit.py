#!/usr/bin/env python3
from typing import Optional
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
from cv2 import cv2
import numpy as np
import sys
import os
import json
from engine.sprite import Sprite


clipboard = []


def comma(r: QtCore.QRect) -> str:
    return f'{r.x()},{r.y()},{r.x() + r.width()},{r.y() + r.height()}'


def clear_clipboard():
    if len(clipboard) > 0:
        del clipboard[0]


def swap_rb(img):
    """
    Swaps the red and blue channels
    :param img: Numpy image
    :return: Result image
    """
    r = img[:, :, 0]
    g = img[:, :, 1]
    b = img[:, :, 2]
    a = img[:, :, 3]
    return cv2.merge((b, g, r, a))


def calculate_alpha(img):
    rgb = img[:, :, 0:3]
    corner = img[0, 0, 0], img[0, 0, 1], img[0, 0, 2]
    indices = np.where(np.all(rgb == corner, axis=-1))
    for y, x in zip(indices[0], indices[1]):
        img[y, x, 3] = 0


def scan_ccs(img):
    """
    Finds all connected components in the alpha channel
    :param img:
    :return: list of rectangles
    """
    rectangles = []
    alpha = img[:, :, 3]
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for c in contours:
        r = cv2.boundingRect(c)
        rectangles.append(QtCore.QRect(*r))
    return rectangles


class AnimationFrame(object):
    def __init__(self, rect: QtCore.QRect, duration: float):
        self._rect = rect
        self._duration = duration
        self._sprite: Optional[Sprite] = None

    def get_rect(self):
        return self._rect

    def set_rect(self, rect: QtCore.QRect):
        self._rect = rect

    def get_duration(self):
        return self._duration

    def set_duration(self, duration: float):
        self._duration = duration

    def get_sprite(self):
        return self._sprite

    def set_sprite(self, sprite: Sprite):
        self._sprite = sprite


class SpriteSheet(QtWidgets.QWidget):
    def __init__(self, sheet_name, parent: Optional["MainWindow"] = None):
        super().__init__(parent)
        self.main_window = parent
        self.image: Optional[np.ndarray] = None
        self.sheet = None
        self.scale = 1.0
        self.rectangles = []
        self.empty_rectangles = []
        self.texture = None
        self.highlight = None
        self.sel_rect = None
        if sheet_name:
            self.load_image(sheet_name)

    def context_menu(self, event):
        menu = QtWidgets.QMenu()
        copy_action = QtWidgets.QAction('Copy')
        copy_action.triggered.connect(self.copy_rect)
        menu.addAction(copy_action)

        copy_hflip_action = QtWidgets.QAction('Copy H-Flip')
        copy_hflip_action.triggered.connect(self.copy_horizontal_flip)
        menu.addAction(copy_hflip_action)

        copy_vflip_action = QtWidgets.QAction('Copy V-Flip')
        copy_vflip_action.triggered.connect(self.copy_vertical_flip)
        menu.addAction(copy_vflip_action)

        paste_action = QtWidgets.QAction('Paste')
        paste_action.triggered.connect(self.paste)
        menu.addAction(paste_action)

        clear_action = QtWidgets.QAction('Clear')
        clear_action.triggered.connect(self.clear)
        menu.addAction(clear_action)

        menu.exec_(self.mapToGlobal(event.pos()))

    def copy_rect(self):
        clear_clipboard()
        if self.sel_rect:
            r = self.sel_rect
            sub = self.image[r.top():(r.bottom() + 1), r.left():(r.right() + 1), :]
            if len(clipboard) > 0:
                clipboard[0] = sub
            else:
                clipboard.append(sub)

    def copy_horizontal_flip(self):
        self.copy_rect()
        if len(clipboard) > 0:
            clipboard[0] = cv2.flip(clipboard[0], 1)

    def copy_vertical_flip(self):
        self.copy_rect()
        if len(clipboard) > 0:
            clipboard[0] = cv2.flip(clipboard[0], 0)

    def paste(self):
        if len(clipboard) > 0:
            r = self.sel_rect
            self.image[r.top():(r.bottom() + 1), r.left():(r.right() + 1), :] = clipboard[0]
            self.scan_empty_rectangles()
            self.update()

    def clear(self):
        if self.sel_rect:
            r = self.sel_rect
            sub = self.image[r.top():(r.bottom() + 1), r.left():(r.right() + 1), :]
            sub[:] = (0, 0, 0, 0)
            self.scan_empty_rectangles()
            self.update()

    def zoom_in(self):
        if self.scale < 16:
            self.scale = 2 * self.scale
            self.update()

    def zoom_out(self):
        if self.scale > 1:
            self.scale = self.scale // 2
            self.update()

    def save_image(self, filename):
        if os.path.exists(filename):
            r = QtWidgets.QMessageBox.question(None, f"{filename} exists", "Overwrite?",
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if r != QtWidgets.QMessageBox.Yes:
                return False
        color_image = cv2.cvtColor(self.image, cv2.COLOR_RGBA2BGRA)
        cv2.imwrite(filename, color_image)
        return True

    def load_image(self, sheet_name: str):
        sheet_name = os.path.normpath(sheet_name)
        image = Image.open(sheet_name).convert('RGBA')
        self.image = np.array(image)
        h, w, c = self.image.shape
        if np.count_nonzero(self.image[:, :, 3]) == (h * w):
            calculate_alpha(self.image)
        pitch = w * c
        self.rectangles = []
        self.sheet = QtGui.QImage(self.image.data, w, h, pitch, QtGui.QImage.Format_RGBA8888)
        self.setMinimumWidth(self.sheet.width())
        self.setMinimumHeight(self.sheet.height())
        self.rectangles = scan_ccs(self.image)
        self.empty_rectangles = []

    def scan_empty_rectangles(self):
        self.empty_rectangles = []
        for r in self.rectangles:
            alpha = self.image[:, :, 3]
            sub = alpha[r.top():r.bottom(), r.left():r.right()]
            if np.max(sub) == 0:
                self.empty_rectangles.append(r)

    def set_tile_size(self, tile_size, gap_size):
        w = self.sheet.width()
        h = self.sheet.height()
        nw = w // (tile_size + gap_size)
        nh = h // (tile_size + gap_size)
        self.rectangles = []
        x = gap_size
        y = gap_size
        for i in range(nh):
            for j in range(nw):
                r = QtCore.QRect(x, y, tile_size, tile_size)
                self.rectangles.append(r)
                x = x + tile_size + gap_size
            x = gap_size
            y = y + tile_size + gap_size
        self.scan_empty_rectangles()

    def set_highlight_rect(self, r):
        self.highlight = r
        self.update()

    def clear_highlight(self):
        self.highlight = None
        self.update()

    def mousePressEvent(self, event):
        x = event.x() / self.scale
        y = event.y() / self.scale
        ctrl = (event.modifiers() & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier
        # alt = (event.modifiers() & QtCore.Qt.AltModifier) == QtCore.Qt.AltModifier
        print(event.modifiers())
        sel_rect = None
        for r in self.rectangles:
            if r.right() > x >= r.left() and r.bottom() > y >= r.top():
                sel_rect = r
                break
        if sel_rect:
            if event.button() == QtCore.Qt.LeftButton:
                if ctrl:
                    self.sel_rect = sel_rect
                    self.clear()
                else:
                    self.main_window.on_rect(sel_rect)
            if event.button() == QtCore.Qt.RightButton:
                self.sel_rect = sel_rect
                self.context_menu(event)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.sheet:
            sz = self.sheet.size()
            r = QtCore.QRect(0, 0, sz.width() * self.scale, sz.height() * self.scale)
            qp.drawImage(r, self.sheet)
        qp.setBrush(QtCore.Qt.NoBrush)
        qp.setPen(QtGui.QColor(255, 0, 0))
        for r in self.rectangles:
            qp.drawRect(self.scale * r.left(), self.scale * r.top(),
                        self.scale * r.width(), self.scale * r.height())
        qp.setPen(QtGui.QColor(128, 255, 0))
        for r in self.empty_rectangles:
            qp.drawRect(self.scale * r.left(), self.scale * r.top(),
                        self.scale * r.width(), self.scale * r.height())
        qp.setPen(QtGui.QColor(0, 255, 0))
        if self.highlight:
            r = self.highlight
            qp.drawRect(self.scale * r.left(), self.scale * r.top(),
                        self.scale * r.width(), self.scale * r.height())
        qp.end()


class SequencesList(QtWidgets.QListWidget):
    def __init__(self, parent: Optional["MainWindow"] = None):
        super().__init__(parent)
        self.main_window: MainWindow = parent
        self.itemSelectionChanged.connect(self.on_selection)

    def on_selection(self):
        sel = self.selectedItems()
        if len(sel) == 1:
            self.main_window.set_current_sequence(sel[0].text())

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        new_action = menu.addAction("New Sequence")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == new_action:
            (name, ok) = QtWidgets.QInputDialog.getText(self, "Sequence Name", "Name")
            if ok:
                self.main_window.add_sequence(name)
                row = self.count()
                self.addItem(name)
                item = self.item(row)
                self.setCurrentItem(item)

    def update_items(self, names):
        self.clear()
        for name in names:
            self.addItem(name)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            for item in self.selectedItems():
                self.main_window.remove_sequence(item.text())
                # self.removeItemWidget(item)


class SequenceRectList(QtWidgets.QListWidget):
    def __init__(self, parent: Optional["MainWindow"] = None):
        super().__init__(parent)
        self.main_window = parent
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.itemSelectionChanged.connect(self.on_selection)

    def on_selection(self):
        sel = self.currentRow()
        self.main_window.set_current_frame(sel)

    def add_rect(self, rect, duration):
        row = self.count()
        self.addItem(f'{rect.left()},{rect.top()},{rect.right()},{rect.bottom()}, {duration}')
        item = self.item(row)
        self.setCurrentItem(item)

    def update_items(self, seq):
        self.clear()
        for frame in seq:
            self.add_rect(frame.get_rect(), frame.get_duration())

    # noinspection PyPep8Naming
    def onItemDoubleClicked(self, item):
        self.main_window.edit_duration(self.row(item))

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            for item in self.selectedItems():
                self.main_window.remove_sprite(self.row(item))


class AnimationWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.src = None
        self.scale = 1
        self.setMinimumSize(QtCore.QSize(300, 300))

    def set_image(self, image):
        self.image = image
        self.src = None

    def set_source_rect(self, r):
        self.src = r
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        if self.image and self.src:
            qp = QtGui.QPainter(self)
            r = QtCore.QRect(0, 0, self.scale * self.src.width(), self.scale * self.src.height())
            qp.drawImage(r, self.image, self.src)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.setup_menu()
        self.sheet_name = filename
        self.sheet = SpriteSheet(filename, self)
        self.setCentralWidget(self.sheet)

        self.paneSequences = QtWidgets.QDockWidget("Sequences", self)
        self.paneSequences.setObjectName("Sequences")
        self.paneSequences.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.sequences = SequencesList(self)
        self.sequences.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.paneSequences.setWidget(self.sequences)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.paneSequences)

        self.paneAnimation = QtWidgets.QDockWidget("Animation", self)
        self.paneAnimation.setObjectName("Animation")
        self.paneAnimation.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.animation = AnimationWidget(self)
        self.animation.image = self.sheet.sheet
        self.paneAnimation.setWidget(self.animation)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.paneAnimation)

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
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(100)
        self.frame_time_left = 0.0

        self.tile_size = 0
        self.tile_gap = 0

    def closeEvent(self, *args, **kwargs):
        self.timer.stop()
        super().closeEvent(*args, **kwargs)

    def on_timer(self):
        # get_screen().fill((0, 0, 0))
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
                self.frame_time_left = seq[self.animation_frame].get_duration()
                self.animation.set_source_rect(frame.get_rect())
            else:
                self.animation_frame = 0

    def set_current_sequence(self, name):
        self.current_sequence = name
        self.sprites.update_items(self.seq_dict[name])

    def set_current_frame(self, frame_index):
        if self.current_sequence:
            seq = self.seq_dict[self.current_sequence]
            if frame_index < len(seq):
                self.sheet.set_highlight_rect(seq[frame_index].get_rect())
            else:
                self.sheet.clear_highlight()

    def add_sequence(self, name):
        self.seq_dict[name] = []

    def remove_sequence(self, name):
        del self.seq_dict[name]
        self.animation.set_source_rect(None)
        self.sequences.update_items(self.seq_dict.keys())
        if self.current_sequence == name:
            self.current_sequence = ''
            self.sprites.clear()

    def remove_sprite(self, index):
        seq = self.seq_dict[self.current_sequence]
        del seq[index]
        self.sprites.update_items(seq)

    def edit_duration(self, index):
        seq = self.seq_dict[self.current_sequence]
        duration = float(seq[index].get_duration())
        (duration, ok) = QtWidgets.QInputDialog.getDouble(self, 'Duration', 'Duration', duration)
        if ok:
            seq[index].set_duration(duration)
            self.sprites.update_items(seq)

    def on_rect(self, r):
        si = self.sequences.selectedItems()
        if len(si) == 1:
            name = si[0].text()
            frame = AnimationFrame(QtCore.QRect(r), 0.1)
            self.seq_dict[name].append(frame)
            self.sprites.update_items(self.seq_dict[name])

    # noinspection PyTypeChecker
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

        exit_action = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        m.addAction(exit_action)

        m = mb.addMenu('&Edit')

        tile_size_action = QtWidgets.QAction('&Tile Size', self)
        tile_size_action.triggered.connect(self.change_tile_size)
        m.addAction(tile_size_action)

        tile_gap_action = QtWidgets.QAction('&Tile Gap', self)
        tile_gap_action.triggered.connect(self.change_tile_gap)
        m.addAction(tile_gap_action)

        m = mb.addMenu('&View')

        zoom_in_action = QtWidgets.QAction('&Zoom In', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.setStatusTip('Zoom In')
        zoom_in_action.triggered.connect(self.zoom_in)
        m.addAction(zoom_in_action)

        zoom_out_action = QtWidgets.QAction('Zoom &Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.setStatusTip('Zoom Out')
        zoom_out_action.triggered.connect(self.zoom_out)
        m.addAction(zoom_out_action)

    def change_tile_size(self):
        ts, ok = QtWidgets.QInputDialog.getInt(self, "Tile Size", "Tile Size")
        if ok:
            self.tile_size = ts
            self.sheet.set_tile_size(self.tile_size, self.tile_gap)

    def change_tile_gap(self):
        gap, ok = QtWidgets.QInputDialog.getInt(self, "Tile Gap", "Tile Gap")
        if ok:
            self.tile_gap = gap
            if self.tile_size > 0:
                self.sheet.set_tile_size(self.tile_size, self.tile_gap)

    def zoom_in(self):
        self.sheet.zoom_in()
        self.animation.scale = self.sheet.scale

    def zoom_out(self):
        self.sheet.zoom_out()
        self.animation.scale = self.sheet.scale

    def on_new(self):
        (filename, ok) = QtWidgets.QFileDialog.getOpenFileName(self, "Sprite Image Sheet", os.getcwd(), "*.png",
                                                               "*.png")
        if ok:
            self.seq_dict = {}
            self.sequences.clear()
            self.sprites.clear()
            self.sheet_name = filename
            self.sheet.load_image(filename)
            self.animation.set_image(self.sheet.sheet)

    def on_open_file(self, filename):
        try:
            self.current_sequence = ''
            root = json.load(open(filename, 'r'))
            self.sheet_name = root.get('Image')
            self.seq_dict = {}
            self.sequences.clear()
            self.sprites.clear()
            self.sheet.load_image(self.sheet_name)
            self.animation.set_image(self.sheet.sheet)
            for seq in root.get('Sequences'):
                name = seq.get('Name')
                self.sequences.addItem(name)
                frames = []
                for frame_dict in seq.get('Frames'):
                    r = [int(c) for c in frame_dict.get('Rect').strip().split(',')]
                    duration = frame_dict.get('Duration')
                    r = QtCore.QRect(r[0], r[1], r[2] - r[0], r[3] - r[1])
                    frame = AnimationFrame(r, duration)
                    # frame.sprite = Subsheet(self.sheet.texture, r)
                    frames.append(frame)
                self.seq_dict[name] = frames
                self.animation_frame = 0
            self.current_frame = 0
            if self.sequences.count() > 0:
                self.current_sequence = self.sequences.item(0).text()
                self.sequences.setCurrentItem(self.sequences.item(0))
        except FileNotFoundError:
            pass

    def on_open(self):
        (filename, ok) = QtWidgets.QFileDialog.getOpenFileName(self, "Load Sprite", os.getcwd(), "*.json",
                                                               "*.json")
        if ok and filename:
            self.on_open_file(filename)

    def on_save(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save", os.getcwd(), "*.json", "*.json")
        if filename:
            image_name = filename.replace('.json', '.png')
            if not self.sheet.save_image(image_name):
                return
            root = {"Image": os.path.basename(image_name), "Flags": ''}
            sequences = []
            for name in self.seq_dict:
                frames = []
                seq = self.seq_dict.get(name)
                for frame in seq:
                    frames.append({"Rect": comma(frame.get_rect()), "Duration": frame.get_duration()})
                sequences.append({"Name": name, "BaseVelocity": 1.0, "Frames": frames})
            root['Sequences'] = sequences
            open(filename, 'w').write(json.dumps(root, indent=4))


def main():
    arg = ''
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(arg)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        w.on_open_file(arg)
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
