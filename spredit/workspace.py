import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from PyQt4 import QtCore, QtGui
from engine import *

class AnimationModel(QtCore.QAbstractTableModel):
    def __init__(self,anim,parent=None):
        super(AnimationModel,self).__init__(parent)
        self.anim=anim
        
    def rowCount(self,parent):
        return len(self.anim.sequences)
        
    def columnCount(self,parent):
        seq=self.anim.get_longest_sequence()
        if seq:
            return 1+len(seq)
        return 1
        
    def data(self,index,role):
        if role==QtCore.Qt.DisplayRole:
            i=index.row()
            j=index.column()
            seq=self.anim.get_sequence(i)
            if not seq is None:
                s=seq.name
                if j>=0 and j<len(seq):
                    s="{}:{}".format(i,j)
                return QtCore.QVariant(s)
        return QtCore.QVariant()
        
    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
            if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
                if section==0:
                    return 'Name'
                else:
                    return str(section)
            return super(AnimationModel,self).headerData(section, orientation, role)        

class Workspace(QtGui.QTableView):
    def __init__(self,pane,mainwin):
        super(Workspace,self).__init__(pane)
        self.mainwin=mainwin
        self.anim=AnimatedSprite()
        self.update()

    def update(self):
        self.setModel(AnimationModel(self.anim))

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        addSeq = menu.addAction("Add Sequence")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action==addSeq:
            (name,valid)=QtGui.QInputDialog.getText(self,'New Sequence','Sequence Name')
            if valid:
                self.anim.add_sequence(AnimationSequence(name))
                self.update()
        
