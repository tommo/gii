import logging
from gii.core.tmpfile import TempDir

from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

def unpackQColor( c ):
	return c.redF(), c.greenF(), c.blueF(), c.alphaF()

def QColorF( r, g, b, a =1 ):
	return QtGui.QColor( r*255, g*255, b*255, a*255)

def addWidgetWithLayout(child, parent = None, **option):
	#add a widget to parent along with a new layout
	direction = option.get('direction','vertical')
	layout    = None
	if   direction == 'vertical':
		layout = QtGui.QVBoxLayout()
	elif direction == 'horizontoal':
		layout = QtGui.QHBoxLayout()
	if not parent:
		parent = child.parent()
	parent.setLayout( layout )
	layout.addWidget( child )
	layout.setSpacing( 0 )
	layout.setMargin( 0 )
	return child

def setClipboardText( text ):
	QtGui.QApplication.clipboard().setText( text )

