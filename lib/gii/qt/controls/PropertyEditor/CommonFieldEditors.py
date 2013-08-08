from PropertyEditor import FieldEditor, registerFieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class StringFieldEditor( FieldEditor ):
	def get( self ):
		return self.lineEdit.text()

	def set( self, value ):
		self.lineEdit.setText( value or '' )

	def initEditor( self, container ):
		self.lineEdit = QtGui.QLineEdit( container )
		self.lineEdit.setMinimumSize( 50, 16 )
		self.lineEdit.textEdited.connect( self.notifyChanged )
		return self.lineEdit

##----------------------------------------------------------------##
class IntFieldEditor( FieldEditor ):
	def get( self ):
		return self.spinBox.value()

	def set( self, value ):
		self.spinBox.setValue( value or 0 )

	def initEditor( self, container ):
		self.spinBox = QtGui.QSpinBox( container )
		self.spinBox.setMinimumSize( 50, 16 )
		self.spinBox.setRange( -16777215, 16777215 )
		self.spinBox.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.spinBox.valueChanged.connect( self.notifyChanged )

		return self.spinBox

##----------------------------------------------------------------##
class FloatFieldEditor( FieldEditor ):
	def get( self ):
		return self.spinBox.value()

	def set( self, value ):
		self.spinBox.setValue( value or 0 )

	def initEditor( self, container ):
		self.spinBox = QtGui.QDoubleSpinBox( container )
		self.spinBox.setMinimumSize( 50, 16 )
		self.spinBox.setRange( -16777215, 16777215 )
		self.spinBox.setDecimals( 5 )
		self.spinBox.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.spinBox.valueChanged.connect( self.notifyChanged )

		return self.spinBox

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
		return self.checkBox


##----------------------------------------------------------------##

registerFieldEditor( str,     StringFieldEditor )
registerFieldEditor( unicode, StringFieldEditor )
registerFieldEditor( int,     IntFieldEditor )
registerFieldEditor( float,   FloatFieldEditor )
registerFieldEditor( bool,    BoolFieldEditor )

