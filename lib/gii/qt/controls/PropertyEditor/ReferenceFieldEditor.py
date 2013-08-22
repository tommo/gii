from PropertyEditor import FieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
##----------------------------------------------------------------##

class ReferenceWidget( QtGui.QWidget ):
	def __init__(self, *args):
		super(ReferenceWidget, self).__init__( *args )
		self.layout = layout = QtGui.QHBoxLayout( self )
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		self.buttonRef  = buttonRef  = QtGui.QButton( self )
		self.buttonGoto = buttonGoto = QtGui.QButton( self )
		buttonRef.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Fixed
			)
		buttonGoto.setSizePolicy(
			QtGui.QSizePolicy.Fixed,
			QtGui.QSizePolicy.Fixed
			)
		buttonRef.setText( '<None>' )
		buttonGoto.setText( '>' )
		layout.addWidget( buttonRef )
		layout.addWidget( buttonGoto )
		self.targetRef = None 

	def setRef( self, target ):
		self.targetRef = target
		self.buttonGoto.setEnabled( bool(target) )

##----------------------------------------------------------------##
class ReferenceFieldEditor( FieldEditor ):
	def get( self ):
		#TODO
		return None

	def set( self, value ):
		self.refWidget.setRef( value )

	def initEditor( self, container ):
		self.refWidget = ReferenceWidget( container )
		return self.refWidget


# registerFieldEditor( ReferenceType, ReferenceFieldEditor )
