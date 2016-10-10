import sys
import random
from PyQt4 import QtCore,QtGui

class LargeWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        super(LargeWidget,self).__init__(parent)
        self.setFixedSize(1000,1000)
        self.color=QtGui.QColor(50,100,150)
        
#    def sizeHint(self):
#        return QtCore.QSize(1024,1024)
        
    def paintEvent(self,event):
        rect=event.rect()
        TILE_SIZE=32
        l=TILE_SIZE*(rect.left()/TILE_SIZE)
        r=TILE_SIZE*((rect.right()+TILE_SIZE)/TILE_SIZE)
        t=TILE_SIZE*(rect.top()/TILE_SIZE)
        b=TILE_SIZE*((rect.bottom()+TILE_SIZE)/TILE_SIZE)
        print "{},{},{},{}".format(l,t,r,b)
        tiles_rect=QtCore.QRect(l,t,r-l,b-t)
        qp=QtGui.QPainter()
        qp.begin(self)
        for y in xrange(t,b,TILE_SIZE):
            for x in xrange(l,r,TILE_SIZE):
                red=((x+3)*(y+17))%255
                green=((x+5)*(y+13))%255
                blue=((x+31)*(y+37))%255
                color=QtGui.QColor(red,green,blue)
                qp.fillRect(QtCore.QRect(x,y,TILE_SIZE,TILE_SIZE),color)
                #self.color=QtGui.QColor(random.randint(0,255),random.randint(0,255),random.randint(0,255))
#        TILE_SIZE=10
#        rt=QtCore.QRect(r.left()/TILE_SIZE,r.top()/TILE_SIZE,r.width()/TILE_SIZE+1,r.height()/TILE_SIZE+1)
#        for x in xrange(rt.left()-2,rt.right()+2):
#            if x>=0 and x<100:
#                for y in xrange(rt.top()-2,rt.bottom()+2):
#                    if y>=0 and y<100:
#                        qp.fillRect(x*10,r.top(),10,r.bottom(),QtGui.QColor(x*2,x*2,x*2))
        qp.drawLine(0,0,1000,1000)
        qp.end()
        
        
class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.lw=LargeWidget()
        self.scrl=QtGui.QScrollArea()
        self.scrl.setWidget(self.lw)
        self.scrl.setWidgetResizable(True)
        #self.scrl.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.scrl.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setCentralWidget(self.scrl)
        
        
def main():
    app=QtGui.QApplication(sys.argv)
    w=MainWindow()
    w.show()
    app.exec_()
    
if __name__=='__main__':
    main()