from gii.core import *
from gii.core.model import *
from PropertyEditor import FieldEditor, registerSimpleFieldEditorFactory
from gii.qt.helpers import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.IconCache  import getIcon

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
		self.buttonRef.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
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
		buttonGoto.setIcon( getIcon('search-2') )
		buttonClear.setIcon( getIcon('remove') )
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

	def setRefName( self, name, formatted ):
		if isinstance( formatted, (unicode, str) ):
			self.buttonRef.setText( formatted )
			self.buttonRef.setToolTip( name )
		else:
			logging.error('unknown ref name type:' + repr( formatted ) )
			self.buttonRef.setText( repr( formatted ) )
			self.buttonRef.setToolTip( '<unkown ref name>' )

	def setRefIcon( self, iconName ):
		icon = getIcon( iconName )
		self.buttonRef.setIcon( icon )

##----------------------------------------------------------------##
class SearchFieldEditorBase( FieldEditor ):	
	def setTarget( self, parent, field ):
		FieldEditor.setTarget( self, parent, field )
		self.target = None
		self.defaultTerms = self.getOption( 'search_terms' )

	def clear( self ):
		pass

	def get( self ):
		#TODO
		return None

	def set( self, value ): #update button text
		self.target = value
		self.refWidget.setRef( value )
		if value:
			r = self.getValueRepr( value )
			if isinstance( r, tuple ):
				( name, icon ) = r
				self.refWidget.setRefIcon( icon )
				self.refWidget.setRefName( name, self.formatRefName( name ) )
			else:
				self.refWidget.setRefIcon( None )
				self.refWidget.setRefName( r, self.formatRefName( r ) )
	
	def initEditor( self, container ):
		widget = SearchFieldWidget( container )
		widget.buttonRef   .clicked .connect( self.openBrowser )
		widget.buttonClear .clicked .connect( self.clearObject )
		widget.buttonGoto  .clicked .connect( self.gotoObject  )

		if self.getOption( 'readonly', False ):
			widget.buttonRef.setEnabled( False )
			widget.buttonClear.setEnabled( False )		
		else:
			if self.getOption( 'no_nil', False ):
				widget.buttonClear.setEnabled( False )
		
		self.refWidget = widget
		return self.refWidget

	def openBrowser( self ):
		self.prevValue = self.getSearchInitial()
		self.testApplied = False
		requestSearchView( 
			context      = self.getSearchContext(),
			type         = self.getSearchType(),
			on_selection = self.onSearchSelection,
			on_test      = self.onSearchSelectionTest,
			on_cancel    = self.onSearchCancel,
			initial      = self.getSearchInitial(),
			terms        = self.defaultTerms
			)
			#TODO: allow persist previous search terms

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

	def onSearchSelectionTest( self, target ):
		self.setValue( target )
		self.testApplied = True

	def onSearchCancel( self ):
		if self.testApplied:
			self.setValue( self.prevValue )
		self.setFocus()
		self.prevValue = None		

	def setValue( self, value ):	#virtual
		self.set( value )
		self.notifyChanged( value )

	def getValueRepr( self, value ): #virtual
		return ModelManager.get().getObjectRepr( value )

	def getIcon( self, value ): #virtual
		return None

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

	def formatRefName( self, name ): #virtual
		return name
