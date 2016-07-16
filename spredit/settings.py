from PyQt4 import QtCore,QtGui


def loadWindowSettings(w):
    qsettings = QtCore.QSettings()

    qsettings.beginGroup( "MainWindow" )

    w.restoreGeometry(qsettings.value( "geometry", w.saveGeometry()).toByteArray()) 
    w.restoreState(qsettings.value( "saveState", w.saveState()).toByteArray())
    w.move(qsettings.value( "pos", w.pos()).toPoint())
    w.resize(qsettings.value( "size", w.size()).toSize())
    if qsettings.value( "maximized", w.isMaximized()).toBool() :
        w.showMaximized()
    qsettings.endGroup()
  
  

def saveWindowSettings(w):
    qsettings = QtCore.QSettings()
    qsettings.beginGroup( "MainWindow" )
    qsettings.setValue( "geometry", w.saveGeometry() )
    qsettings.setValue( "saveState", w.saveState() )
    qsettings.setValue( "maximized", w.isMaximized() )
    if not w.isMaximized() == True :
        qsettings.setValue( "pos", w.pos() )
        qsettings.setValue( "size", w.size() )
    qsettings.endGroup()
    