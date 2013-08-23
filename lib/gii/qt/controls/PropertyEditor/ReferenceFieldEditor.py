from gii.core.model import *
from PropertyEditor import FieldEditor, registerFieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
##----------------------------------------------------------------##

class ReferenceBrowser( QtGui.QWidget ):
	def __init__(self, *args ):
		super(ReferenceBrowser, self).__init__( *args )

	def sizeHint( self ):
		return QtCore.QSize( 500, 300) 

	def focusOutEvent( self, ev ):
		self.hide()

##----------------------------------------------------------------##
class ReferenceFieldButton( QtGui.QToolButton ):
	def sizeHint( self ):
		return QtCore.QSize( 20, 20)
		
##----------------------------------------------------------------##
class ReferenceFieldWidget( QtGui.QWidget ):
	def __init__(self, *args):
		super(ReferenceFieldWidget, self).__init__( *args )
		self.layout = layout = QtGui.QHBoxLayout( self )
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		self.buttonRef  = buttonRef  = ReferenceFieldButton( self )
		self.buttonGoto = buttonGoto = ReferenceFieldButton( self )
		buttonRef.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Fixed
			)
		buttonGoto.setSizePolicy(
			QtGui.QSizePolicy.Fixed,
			QtGui.QSizePolicy.Fixed
			)
		buttonRef.setText( '<None>' )
		buttonRef.setStyleSheet ("text-align: left;"); 
		buttonGoto.setText( '...' )
		layout.addWidget( buttonRef )
		layout.addWidget( buttonGoto )
		self.targetRef = None 
		self.setRef( None )


	def setRef( self, target ):
		self.targetRef = target
		if not target:
			self.buttonGoto.hide()
		else:
			self.buttonGoto.show()

##----------------------------------------------------------------##
class ReferenceFieldEditor( FieldEditor ):	
	def setTarget( self, parent, field ):
		super( ReferenceFieldEditor, self ).setTarget( parent, field )
		self.targetType = field.getType()

	def get( self ):
		#TODO
		return None

	def set( self, value ):
		self.refWidget.setRef( value )

	def initEditor( self, container ):
		self.refWidget = widget = ReferenceFieldWidget( container )
		widget.buttonRef.clicked.connect( self.openBrowser )
		widget.buttonGoto.clicked.connect( self.gotoObject )
		return self.refWidget

	def openBrowser( self ):
		browser = ReferenceBrowser( None )
		p = self.refWidget.mapToGlobal( QtCore.QPoint( 0,0 ) )
		browser.move( p )
		browser.show()
		browser.setFocus( Qt.ActiveWindowFocusReason )
		self.browser = browser

	def gotoObject( self ):
		pass


registerFieldEditor( ReferenceType, ReferenceFieldEditor )
