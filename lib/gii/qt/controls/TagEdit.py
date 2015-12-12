import sys
import math

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle, qRgb


class TagLabel( QtGui.QToolButton ):
	def __init__(self, *args, **kwargs ):
		super( TagLabel, self ).__init__( *args, **kwargs )
		self.setStyleSheet(
			'''
			padding-left:5; padding-right:5;
			border-radius:4px;
			background-color:#4e08b4;
			''')

class TagLineEdit( QtGui.QLineEdit ):
	def __init__(self, *args, **kwargs ):
		super( TagLineEdit, self ).__init__( *args, **kwargs )
		self.setAutoFillBackground( False )
		self.setStyleSheet(
			'''
			border:none;
			background:transparent;
			''')

	def keyPressEvent( self, ev ):
		key = ev.key()
		if key == Qt.Key_Backspace:
			if self.cursorPosition() == 0:
				self.parent().removeLastTag()
		return super( TagLineEdit, self ).keyPressEvent( ev )

class TagEdit( QtGui.QWidget ):
	def __init__(self, *args, **kwargs ):
		super( TagEdit, self ).__init__( *args, **kwargs )
		self.tags = []
		self.tagLabelMap = {}
		layout = QtGui.QHBoxLayout( self )
		layout.setMargin( 0 )
		layout.setSpacing( 2 )
		
		self.lineEdit = TagLineEdit( self )
		self.lineEdit.setAttribute(Qt.WA_MacShowFocusRect, False)
		self.lineEdit.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
		layout.addWidget( self.lineEdit )

		# self.installEventFilter( self )

	# def eventFilter( self, obj, event ):
	# 	etype = event.type()
	# 	print obj, etype
	# 	if obj == self.lineEdit:
	# 		if etype == QtCore.QEvent.KeyPress:
	# 			key = event.key()
	# 			if key == Qt.Key_Backspace:
	# 				if self.lineEdit.cursorPosition() == 0:
	# 						self.removeLastTag()
	# 						return True
	# 	return False

	def addTag( self, tag ):
		if tag in self.tags: return
		self.tags.append( tag )
		label = TagLabel( self )
		label.setText( tag )
		count = self.layout().count()
		self.layout().insertWidget( max( count - 1, 0 ) , label )
		self.tagLabelMap[ tag ] = label

	def removeTag( self, tag ):
		if not tag in self.tags: return
		self.tags.remove( tag )
		label = self.tagLabelMap.get( tag, None )
		if label:
			idx = self.layout().indexOf( label )
			if idx >= 0:
				self.layout().takeAt( idx )
			label.deleteLater()
			del self.tagLabelMap[ tag ]

	def removeLastTag( self ):
		if self.tags:
			self.removeTag( self.tags[ -1 ] )

######TEST
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)

	widget = TagEdit()
	widget.addTag( 'TestA' )
	widget.addTag( 'TestB' )
	widget.addTag( 'TestC' )
	widget.addTag( 'TestD' )
	widget.show()
	widget.raise_()

	app.exec_()

