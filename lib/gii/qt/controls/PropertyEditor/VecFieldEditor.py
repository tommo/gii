from PropertyEditor import FieldEditor, registerFieldEditor
from FieldEditorControls import *

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt


class VecEditorWidget( QtGui.QWidget ):
	def __init__( self, *args ):
		super(VecEditorWidget, self).__init__( *args )
		self.layout = layout = QtGui.QHBoxLayout( self )
		layout.setSpacing(0)
		layout.setMargin(0)		
		for i in range()
		self.valueX = FieldEditorDoubleSpinBox( self )
		self.valueX.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.valueY = FieldEditorDoubleSpinBox( self )
		self.valueY.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		layout.addWidget( self.valueX )
		layout.addWidget( self.valueY )
		self.setLayout( layout )

		
##----------------------------------------------------------------##
class Vec2FieldEdtior( FieldEditor ):
	def get( self ):
		return ( self.editor.valueX.value(), self.editor.valueY.value() )

	def set( self, value ):
		if isinstance( value, tuple ):
			x, y = value
		else:
			x, y = 0, 0
		self.editor.valueX.setValue( x )
		self.editor.valueY.setValue( y )

	def onValueChanged( self, v ):
		return self.notifyChanged( self.get() )

	def initEditor( self, container )	:
		self.editor = VecEditorWidget( container )
		# self.editor.setMinimumSize( 50, 16 )
		minValue = self.getOption( 'min', -16777215.0 )
		maxValue = self.getOption( 'max',  16777215.0 )

		for spinBox in ( self.editor.valueX, self.editor.valueY ):
			spinBox.valueChanged.connect( self.onValueChanged )
			spinBox.setRange( minValue, maxValue	)
			spinBox.setSingleStep( self.getOption( 'step', 1 ) )

		return self.editor

registerFieldEditor( 'vec2', Vec2FieldEdtior )
