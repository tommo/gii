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
	def get( self ):
		return self.control.value()

	def set( self, value ):
		self.control.setValue( value or 0 )

	def initEditor( self, container ):
		self.step = self.getOption( 'step', 1 )
		widget = self.getOption( 'widget', 'spin' )
		if widget == 'slider':
			self.control = self.initSlider( container )
		else: #if widget == 'spin'
			self.control = self.initSpinBox( container )
		if self.getOption( 'readonly', False):
			self.control.setEnabled( False )		
		return self.control

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

	def initSpinBox( self, container ):
		spinBox = None
		if self.getFieldType() == int:
			spineBox = FieldEditorSpinBox( container )
			step = int(self.step)
			if step <= 0: step = 1
			spineBox.setSingleStep( step )
		else:
			spineBox = FieldEditorDoubleSpinBox( container )
			spineBox.setDecimals( self.getOption( 'decimals', 5 )	)
			spineBox.setSingleStep( self.step	)

		#common part
		spineBox.setMinimumSize( 50, 16 )
		spineBox.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		spineBox.valueChanged.connect( self.notifyChanged )
		#options
		minValue = self.getOption( 'min', -16777215.0 )
		maxValue = self.getOption( 'max',  16777215.0 )
		spineBox.setRange( minValue, maxValue	)
		return spineBox

	def initSlider( self, container ):
		sliderBox = FieldEditorSliderBox( container )
		sliderBox.setMinimumSize( 50, 16 )
		sliderBox.valueChanged.connect( self.notifyChanged )
		if not self.getOption( 'min' ) and not self.getOption( 'max' ):
			logging.warn( 'no range specified for slider field: %s' % self.field )
		minValue = self.getOption( 'min', 0.0 )
		maxValue = self.getOption( 'max', 100.0 )
		sliderBox.setRange( minValue, maxValue )
		sliderBox.setNumberType( self.getFieldType() )
		return sliderBox

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
		return self.notifyChanged( bool( self.get() ) )

	def initEditor( self, container ):
		self.checkBox = QtGui.QCheckBox( container )
		self.checkBox.stateChanged.connect( self.onStateChanged )
		if self.getOption( 'readonly', False ):
			self.checkBox.setEnabled( False )
		return self.checkBox


##----------------------------------------------------------------##

registerFieldEditor( str,     StringFieldEditor )
registerFieldEditor( unicode, StringFieldEditor )
registerFieldEditor( int,     NumberFieldEditor )
registerFieldEditor( float,   NumberFieldEditor )
registerFieldEditor( bool,    BoolFieldEditor )

