import sys
import random
from PyQt5 import QtCore,QtGui,QtWidgets

class LargeWidget(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(LargeWidget,self).__init__(parent)
        self.setFixedSize(1000,1000)
        self.color=QtGui.QColor(50,100,150)
        
#    def sizeHint(self):
#        return QtCore.QSize(1024,1024)
        
    def paintEvent(self,event):
        rect=event.rect()
        TILE_SIZE=32
        l=TILE_SIZE*(rect.left()//TILE_SIZE)
        r=TILE_SIZE*((rect.right()+TILE_SIZE)//TILE_SIZE)
        t=TILE_SIZE*(rect.top()//TILE_SIZE)
        b=TILE_SIZE*((rect.bottom()+TILE_SIZE)//TILE_SIZE)
        print("{},{},{},{}".format(l,t,r,b))
        tiles_rect=QtCore.QRect(l,t,r-l,b-t)
        qp=QtGui.QPainter()
        qp.begin(self)
        for y in range(t,b,TILE_SIZE):
            for x in range(l,r,TILE_SIZE):
                red=((x+3)*(y+17))%255
                green=((x+5)*(y+13))%255
                blue=((x+31)*(y+37))%255
                color=QtGui.QColor(red,green,blue)
                qp.fillRect(QtCore.QRect(x,y,TILE_SIZE,TILE_SIZE),color)
        qp.drawLine(0,0,1000,1000)
        qp.end()
        
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.lw=LargeWidget()
        self.scrl=QtWidgets.QScrollArea()
        self.scrl.setWidget(self.lw)
        self.scrl.setWidgetResizable(True)
        #self.scrl.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.scrl.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setCentralWidget(self.scrl)
        
        
def main():
    app=QtWidgets.QApplication(sys.argv)
    w=MainWindow()
    w.show()
    app.exec_()
    
if __name__=='__main__':
    main()
