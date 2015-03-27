import logging
from gii.core.tmpfile import TempDir

from PyQt4 import QtGui,QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

def unpackQColor( c ):
	return c.redF(), c.greenF(), c.blueF(), c.alphaF()

def QColorF( r, g, b, a =1 ):
	return QtGui.QColor( r*255, g*255, b*255, a*255)

def addWidgetWithLayout( child, parent = None, **option ):
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


def getClipboardText( default = None ):
	t = QtGui.QApplication.clipboard().text()
	if not t: return default
	return t


def restrainWidgetToScreen( widget ):
		screenRect = QtGui.QApplication.desktop().availableGeometry(widget);
		widgetRect = widget.frameGeometry()
		pos = widget.pos()
		
		if widgetRect.left() < screenRect.left() :
			pos.setX( pos.x() + screenRect.left() - widgetRect.left() )
		elif widgetRect.right() > screenRect.right():
			pos.setX( pos.x() + screenRect.right() - widgetRect.right() )

		if widgetRect.top() < screenRect.top():
			pos.setY( pos.y() + screenRect.top() - widgetRect.top() )			
		elif widgetRect.bottom() > screenRect.bottom():
			pos.setY( pos.y() + screenRect.bottom() - widgetRect.bottom() )

		widget.move( pos )
