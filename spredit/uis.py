#!/usr/bin/env python
import os
from subprocess import call
from PyQt4 import QtGui
import re
import inspect
import importlib

pyuic4_ext=''
if os.name=='nt':
    pyuic4_ext='.bat'

def loadDialog(name,dlg=None):
    module=importlib.import_module('gen.'+name)
    for name,obj in inspect.getmembers(module):
        if name.startswith("Ui_"):
            if not dlg:
                dlg=QtGui.QDialog()
            ui=obj()
            ui.setupUi(dlg)
            return dlg


def generate():
    inputs = os.listdir('uis')
    syms=[]
    for uiName in inputs:
        base=(os.path.splitext(uiName))[0]
        inpath=os.path.join('uis',uiName)
        outpath=os.path.join('gen',base+".py")
        call(['pyuic4'+pyuic4_ext,'-o',outpath,inpath])
        dlg='dlg'
        f=open(outpath,"r")
        lines=f.readlines()
        f.close()
        for i in xrange(0,len(lines)):
            line=lines[i]
            line=line.replace('QtGui.QPixmap(_fromUtf8("../icons','QtGui.QPixmap(_fromUtf8("icons')
            lines[i]=line
            if line.startswith('# Created'):
                lines[i]='#\n'
            if line.startswith("class Ui_"):
                dlg=(re.split('\W+',line))[1]
                dlg=dlg[3:]
            p=line.find('self.')
            if p>0:
                sym=line[p+5:]
                if not sym.startswith('retranslateUi'):
                    lines[i]=line.replace('self.',dlg+'.')
        syms.append((base,dlg))
        f=open(outpath,"w")
        f.write(''.join(lines))
        f.close()
#    f=open('gen/__init__.py','w')
#    for s in syms:
#        f.write('from {} import Ui_{}\n'.format(s[0],s[1]))
#    f.write('\n__all__ = [ ')
#    first=True
#    for s in syms:
#        if not first:
#            f.write(", ")
#        first=False
#        f.write("'Ui_{}'".format(s[1]))
#    f.write(' ]\n\n')
#    f.close()
        
if __name__=='__main__':
    generate()
