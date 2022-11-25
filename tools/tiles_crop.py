import sys
import numpy as np
from cv2 import cv2
from PyQt5 import QtWidgets, QtGui, QtCore


class TilesWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.image = QtGui.QImage()
        self.source = np.ndarray((32, 32, 3), dtype=np.uint8)
        self.set_image(self.source)
        self.tile_size = 32
        self.click_callback = None
        self.highlight = 0, 0
        self.setMinimumHeight(128)

    def increment_current(self):
        self.highlight = self.highlight[0] + 1, self.highlight[1]
        self.update()

    def get_current_tile(self):
        x, y = self.highlight
        x *= self.tile_size
        y *= self.tile_size
        return self.source[y:(y + self.tile_size), x:(x + self.tile_size)]

    def update_current_tile(self, image):
        x, y = self.highlight
        x *= self.tile_size
        y *= self.tile_size
        self.source[y:(y + self.tile_size), x:(x + self.tile_size)] = image
        self.set_image(self.source)
        self.update()

    def set_click_callback(self, cb):
        self.click_callback = cb

    def set_tile_size(self, size: int):
        self.tile_size = size

    def set_image(self, image: np.array):
        self.source = image
        self.image = QtGui.QImage(image, image.shape[1], image.shape[0], QtGui.QImage.Format_BGR888)
        self.resize(image.shape[1], image.shape[0])

    def load_image(self, filename: str):
        image = cv2.imread(filename, cv2.IMREAD_COLOR)
        self.set_image(image)

    def paintEvent(self, event: QtGui.QPaintEvent):
        qp = QtGui.QPainter(self)
        qp.drawImage(0, 0, self.image)
        x = self.highlight[0] * self.tile_size
        y = self.highlight[1] * self.tile_size
        qp.setPen(QtGui.QColor('red'))
        qp.drawRect(QtCore.QRectF(x, y, self.tile_size, self.tile_size))

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        x = event.x() // self.tile_size
        y = event.y() // self.tile_size
        self.highlight = x, y
        if self.click_callback:
            self.click_callback(x, y)
        self.update()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(None)
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        scroller = QtWidgets.QScrollArea(container)
        self.all_tiles = TilesWidget()
        self.all_tiles.set_tile_size(32)
        self.all_tiles.load_image('all.png')
        scroller.setWidget(self.all_tiles)
        layout.addWidget(scroller)

        self.cropped = TilesWidget()
        self.cropped.set_tile_size(32)
        self.cropped.set_image(np.ndarray((32, 512, 3), dtype=np.uint8))
        layout.addWidget(self.cropped)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == ord('S'):
            res = QtWidgets.QFileDialog.getSaveFileName(caption='Save Image')
            cv2.imwrite(res[0], self.cropped.source)
        if event.key() == 32:
            tile = self.all_tiles.get_current_tile()
            self.cropped.update_current_tile(tile)
            self.all_tiles.increment_current()
            self.cropped.increment_current()


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
