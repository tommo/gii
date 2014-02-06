from PropertyEditor import FieldEditor, registerFieldEditor
from FieldEditorControls import *

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class VecEditorWidget( QtGui.QWidget ):
	def __init__( self, dim, parent ):
		super(VecEditorWidget, self).__init__( parent )
		self.dim = dim
		self.layout = layout = QtGui.QHBoxLayout( self )
		layout.setSpacing(0)
		layout.setMargin(0)		

		self.fields = fields = []
		for i in range( dim ):
			field = FieldEditorDoubleSpinBox( self )
			field.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding
				)
			layout.addWidget( field )
			fields.append( field )

		self.setLayout( layout )

	def getValue( self ):
		return tuple( field.value() for field in self.fields  )

	def setValue( self, value ):
		if value:
			for i, v in enumerate( value ):
				self.fields[i].setValue( v )
		else:
			for field in self.fields:
				field.setValue( 0 )
		
	def setRange( self, min, max ):
		for field in  self.fields:
			field.setRange( min, max )

	def setSingleStep( self, step ):
		for field in  self.fields:
			field.setSingleStep( step )

		
##----------------------------------------------------------------##
class GenericVecFieldEdtior( FieldEditor ):
	def getDimension( self ):
		return 2

	def get( self ):
		return self.editor.getValue()

	def set( self, value ):
		self.editor.setValue( value )

	def onValueChanged( self, v ):
		return self.notifyChanged( self.get() )

	def initEditor( self, container )	:
		self.editor = VecEditorWidget( self.getDimension(), container )
		# self.editor.setMinimumSize( 50, 16 )
		minValue = self.getOption( 'min', -16777215.0 )
		maxValue = self.getOption( 'max',  16777215.0 )

		for field in  self.editor.fields:
			field.valueChanged.connect( self.onValueChanged )
			field.setRange( minValue, maxValue	)
			field.setSingleStep( self.getOption( 'step', 1 ) )
			field.setDecimals( self.getOption( 'decimals', 4 ) )

		return self.editor

##----------------------------------------------------------------##
class Vec2FieldEdtior( GenericVecFieldEdtior ):
	def getDimension( self ):
		return 2

registerFieldEditor( 'vec2', Vec2FieldEdtior )

##----------------------------------------------------------------##
class Vec3FieldEdtior( GenericVecFieldEdtior ):
	def getDimension( self ):
		return 3

registerFieldEditor( 'vec3', Vec3FieldEdtior )
