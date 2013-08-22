from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class FieldEditorLineEdit(QtGui.QLineEdit):
	def __init__(self, *arg):
		super(FieldEditorLineEdit, self).__init__( *arg )

	def focusInEvent( self, ev ):
		self.selectAll()
		super(FieldEditorLineEdit, self).focusInEvent( ev )
		

##----------------------------------------------------------------##
class FieldEditorSpinBox(QtGui.QSpinBox):
	def __init__(self, *arg):
		super(FieldEditorSpinBox, self).__init__( *arg )

	def focusInEvent( self, ev ):
		self.selectAll()
		super(FieldEditorSpinBox, self).focusInEvent( ev )
		
##----------------------------------------------------------------##
class FieldEditorDoubleSpinBox(QtGui.QDoubleSpinBox):
	def __init__(self, *arg):
		super(FieldEditorDoubleSpinBox, self).__init__( *arg )

	def focusInEvent( self, ev ):
		self.selectAll()
		super(FieldEditorDoubleSpinBox, self).focusInEvent( ev )
		

##----------------------------------------------------------------##
class DraggableLabel( QtGui.QLabel ):
	dragged = QtCore.pyqtSignal( int )

	def __init__( self, *args ):
		super( DraggableLabel, self ).__init__( *args )
		self.dragging = False
		self.x0 = 0
		self.setCursor( Qt.PointingHandCursor )

	def mousePressEvent( self, ev ):
		if ev.button() == Qt.LeftButton:
			self.dragging = True
			self.grabMouse()
			self.x0 = ev.x()

	def mouseReleaseEvent( self, ev ):
		if ev.button() == Qt.LeftButton:
			if self.dragging:
				self.dragging = False
				self.releaseMouse()

	def mouseMoveEvent( self, ev ):
		if self.dragging:
			delta = ev.x() - self.x0
			self.x0 = ev.x()
			self.dragged.emit( delta )
