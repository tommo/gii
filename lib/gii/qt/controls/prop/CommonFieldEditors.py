from PropertyEditor import FieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class StringFieldEditor( FieldEditor ):
	def get( self ):
		return self.lineEdit.text()

	def set( self, value ):
		self.lineEdit.setText( value )

	def initEditor( self, container ):
		self.lineEdit = QtGui.QLineEdit( container )
		self.lineEdit.textEdited.connect( self.notifyChanged )
		return self.lineEdit

##----------------------------------------------------------------##
class IntFieldEditor( FieldEditor ):
	def get( self ):
		return self.spinBox.value()

	def set( self, value ):
		self.spinBox.setValue( value )

	def initEditor( self, container ):
		self.spinBox = QtGui.QSpinBox( container )
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
		self.spinBox.setValue( value )

	def initEditor( self, container ):
		self.spinBox = QtGui.QDoubleSpinBox( container )
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
		self.checkBox.setChecked( value )

	def onStateChanged( self, state ):
		return self.notifyChanged( self.get() )

	def initEditor( self, container ):
		self.checkBox = QtGui.QCheckBox( container )
		self.checkBox.stateChanged.connect( self.onStateChanged )
		return self.checkBox

##----------------------------------------------------------------##
class EnumFieldEditor( FieldEditor ):
	def get( self ):
		index = self.combo.currentIndex()
		if index >= 0:
			name, value = self.enumItems[ index ]
		return value

	def set( self, value ):
		for i, t in enumerate( self.enumItems ):
			itemName, itemValue = t
			if value == itemValue:
				self.combo.setCurrentIndex( i )
				return

	def setTarget( self, parent, fieldId ):
		super( EnumFieldEditor, self ).setTarget( parent, fieldId )
		self.enumItems = [ ('GOOD', 0), ('BAD', 1) ]

	def onIndexChanged( self, index ):
		if index >= 0:
			name, value = self.enumItems[ index ]
			return self.notifyChanged( value )

	def initEditor( self, container ):
		self.combo = QtGui.QComboBox( container )
		for item in self.enumItems:
			( name, value ) = item
			self.combo.addItem( name, value )
		self.combo.currentIndexChanged.connect( self.onIndexChanged )
		self.combo.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		return self.combo

##----------------------------------------------------------------##
class ColorFieldEditor( FieldEditor ):
	def get( self ):
		return self.checkBox.isChecked()

	def set( self, value ):
		self.checkBox.setChecked( value )

	def onStateChanged( self, state ):
		return self.notifyChanged( self.get() )

	def initEditor( self, container ):
		self.checkBox = QtGui.QCheckBox( container )
		self.checkBox.stateChanged.connect( self.onStateChanged )
		return self.checkBox
	