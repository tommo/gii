from PropertyEditor import FieldEditor, registerFieldEditor
from FieldEditorControls import *

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class StringFieldEditor( FieldEditor ):
	def get( self ):
		return self.lineEdit.text()

	def set( self, value ):
		self.lineEdit.setText( value or '' )

	def initEditor( self, container ):
		self.lineEdit = FieldEditorLineEdit( container )
		self.lineEdit.setMinimumSize( 50, 16 )
		self.lineEdit.textEdited.connect( self.notifyChanged )
		if self.getOption( 'readonly', False ):
			self.lineEdit.setReadOnly( True )
		return self.lineEdit

##----------------------------------------------------------------##
class NumberFieldEditor( FieldEditor ):
	def initLabel( self, label, container ):
		self.labelWidget = DraggableLabel( container )
		self.labelWidget.setText( label )
		self.labelWidget.setMinimumSize( 50, 16 )
		self.labelWidget.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.labelWidget.dragged.connect( self.onDragAdjust )
		return self.labelWidget

	def onDragAdjust( self, delta ):
		pass


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

		

##----------------------------------------------------------------##
class IntFieldEditor( NumberFieldEditor ):
	def get( self ):
		return self.spinBox.value()

	def set( self, value ):
		self.spinBox.setValue( value or 0 )

	def initEditor( self, container ):
		self.spinBox = FieldEditorSpinBox( container )
		self.spinBox.setMinimumSize( 50, 16 )
		self.spinBox.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.spinBox.valueChanged.connect( self.notifyChanged )

		#options
		minValue = self.getOption( 'min', -16777215.0 )
		maxValue = self.getOption( 'max',  16777215.0 )

		self.spinBox.setRange( minValue, maxValue	)

		self.spinBox.setSingleStep( 
			self.getOption( 'step', 1 )
			)
		
		if self.getOption( 'readonly', False):
			self.spinBox.setEnabled( False )

		return self.spinBox

	def onDragAdjust( self, delta ):
		v = self.get()
		self.set( v + delta )

##----------------------------------------------------------------##
class FloatFieldEditor( NumberFieldEditor ):
	def get( self ):
		return self.spinBox.value()

	def set( self, value ):
		self.spinBox.setValue( value or 0 )

	def initEditor( self, container ):
		self.spinBox = FieldEditorDoubleSpinBox( container )
		self.spinBox.setMinimumSize( 50, 16 )
		self.spinBox.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.spinBox.valueChanged.connect( self.notifyChanged )
		#options
		minValue = self.getOption( 'min', -16777215.0 )
		maxValue = self.getOption( 'max',  16777215.0 )

		self.spinBox.setRange( minValue, maxValue	)

		self.spinBox.setDecimals( 
			self.getOption( 'decimals', 5 )
			)
		
		self.step = self.getOption( 'step', 0.1 )
		self.spinBox.setSingleStep( self.step )
		
		if self.getOption( 'readonly', False):
			self.spinBox.setEnabled( False )

		return self.spinBox

	def onDragAdjust( self, delta ):
		v = self.get()
		self.set( v + delta * self.step )

##----------------------------------------------------------------##
class BoolFieldEditor( FieldEditor ):
	def get( self ):
		return self.checkBox.isChecked()

	def set( self, value ):		
		self.checkBox.setChecked( bool(value) )

	def onStateChanged( self, state ):
		return self.notifyChanged( self.get() )

	def initEditor( self, container ):
		self.checkBox = QtGui.QCheckBox( container )
		self.checkBox.stateChanged.connect( self.onStateChanged )
		if self.getOption( 'readonly', False ):
			self.checkBox.setEnabled( False )
		return self.checkBox


##----------------------------------------------------------------##

registerFieldEditor( str,     StringFieldEditor )
registerFieldEditor( unicode, StringFieldEditor )
registerFieldEditor( int,     IntFieldEditor )
registerFieldEditor( float,   FloatFieldEditor )
registerFieldEditor( bool,    BoolFieldEditor )

