from gii.core import *
from gii.core.model import *
from PropertyEditor import FieldEditor, registerFieldEditor
from gii.qt.helpers import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.SearchView import requestSearchView

##----------------------------------------------------------------##
class SearchFieldButton( QtGui.QToolButton ):
	def sizeHint( self ):
		return QtCore.QSize( 20, 20)
		
##----------------------------------------------------------------##
class SearchFieldWidget( QtGui.QWidget ):
	def __init__(self, *args):
		super(SearchFieldWidget, self).__init__( *args )
		self.layout = layout = QtGui.QHBoxLayout( self )
		layout.setSpacing( 0 )
		layout.setMargin( 0 )
		self.buttonRef   = buttonRef   = SearchFieldButton( self )
		self.buttonGoto  = buttonGoto  = SearchFieldButton( self )
		self.buttonClear = buttonClear = SearchFieldButton( self )
		buttonRef.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Fixed
			)
		buttonGoto.setSizePolicy(
			QtGui.QSizePolicy.Fixed,
			QtGui.QSizePolicy.Fixed
			)
		buttonClear.setSizePolicy(
			QtGui.QSizePolicy.Fixed,
			QtGui.QSizePolicy.Fixed
			)
		buttonRef.setText( '<None>' )
		buttonRef.setStyleSheet ("text-align: left;"); 
		buttonGoto.setText( '...' )
		buttonClear.setText( 'x' )
		layout.addWidget( buttonRef )
		layout.addWidget( buttonGoto )
		layout.addWidget( buttonClear )
		self.targetRef = None 
		self.setRef( None )


	def setRef( self, target ):
		self.targetRef = target
		if not target:
			self.buttonRef.setText( '<None>' )
			self.buttonGoto.hide()
			self.buttonClear.hide()
		else:
			self.buttonRef.setText( 'Object' ) 
			self.buttonGoto.show()
			self.buttonClear.show()

	def setRefName( self, name ):
		if isinstance( name, (unicode, str) ):
			self.buttonRef.setText( name )
		else:
			logging.error('unknown ref name type:' + repr( name ) )
			self.buttonRef.setText( repr( name ) )

##----------------------------------------------------------------##
class SearchFieldEditorBase( FieldEditor ):	
	def setTarget( self, parent, field ):
		FieldEditor.setTarget( self, parent, field )
		self.target = None

	def clear( self ):
		pass

	def get( self ):
		#TODO
		return None

	def set( self, value ):
		self.target = value
		self.refWidget.setRef( value )
		if value:			
			self.refWidget.setRefName( self.getValueRepr( value ) )
	
	def initEditor( self, container ):
		self.refWidget = widget = SearchFieldWidget( container )
		if self.getOption( 'readonly', False ):
			widget.buttonRef.setEnabled( False )
			widget.buttonClear.setEnabled( False )
		else:
			widget.buttonRef.clicked.connect( self.openBrowser )
			widget.buttonClear.clicked.connect( self.clearObject )
		widget.buttonGoto.clicked.connect( self.gotoObject )
		return self.refWidget

	def openBrowser( self ):
		requestSearchView( 
			context      = self.getSearchContext(),
			type         = self.getSearchType(),
			on_selection = self.onSearchSelection,
			on_cancel    = self.onSearchCancel,
			initial      = self.getSearchInitial()
			)

	def getBrowserPos( self ):
		size = self.refWidget.size()
		w, h = size.width(), size.height()
		p = self.refWidget.mapToGlobal( QtCore.QPoint( 0, h ) )
		return p

	def setFocus( self ):
		self.refWidget.setFocus()

	def onSearchSelection( self, target ):
		self.setValue( target )
		self.setFocus()

	def onSearchCancel( self ):
		self.setFocus()

	def setValue( self, value ):	#virtual
		self.set( value )
		self.notifyChanged( value )

	def getValueRepr( self, value ): #virtual
		return ModelManager.get().getObjectRepr( value )

	def getSearchType( self ): #virtual
		return self.field.getType()

	def getSearchContext( self ): #virtual
		return ""

	def getSearchInitial( self ): #virtual
		return self.target

	def gotoObject( self ): #virtual
		pass		

	def clearObject( self ): #virtual
		self.setValue( None )
