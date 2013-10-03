from gii.core import *
from gii.core.model import *
from PropertyEditor import FieldEditor, registerFieldEditor
from gii.qt.helpers import addWidgetWithLayout, QColorF, unpackQColor

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.SearchView import requestSearchView

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
		self.buttonRef   = buttonRef   = ReferenceFieldButton( self )
		self.buttonGoto  = buttonGoto  = ReferenceFieldButton( self )
		self.buttonClear = buttonClear = ReferenceFieldButton( self )
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
			self.buttonRef.setText( '...' ) #TODO:
			self.buttonGoto.show()
			self.buttonClear.show()

	def setRefName( self, name ):
		if isinstance( name, (unicode, str) ):
			self.buttonRef.setText( name )
		else:
			logging.error('unknown ref name type:' + repr( name ) )
			self.buttonRef.setText( repr( name ) )

##----------------------------------------------------------------##
class AssetRefFieldEditor( FieldEditor ):	
	def setTarget( self, parent, field ):
		super( AssetRefFieldEditor, self ).setTarget( parent, field )
		t = field.getType()
		self.targetType    = t.assetType
		self.targetContext = None  #TODO
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
			self.refWidget.setRefName( value )

	def setValue( self, node ):
		if node:
			value = node.getNodePath()
		else:
			value = None
		self.set( value )
		self.notifyChanged( value )

	def initEditor( self, container ):
		self.refWidget = widget = ReferenceFieldWidget( container )
		widget.buttonRef.clicked.connect( self.openBrowser )
		widget.buttonGoto.clicked.connect( self.gotoObject )
		widget.buttonClear.clicked.connect( self.clearObject )
		return self.refWidget

	def openBrowser( self ):			
		requestSearchView( 
			context = 'asset',
			type    = self.targetType,
			on_selection = self.onSearchSelection,
			on_cancel    = self.onSearchCancel
			)

	def onSearchSelection( self, target ):
		self.setValue( target )
		self.setFocus()

	def onSearchCancel( self ):
		self.setFocus()

	def getBrowserPos( self ):
		size = self.refWidget.size()
		w, h = size.width(), size.height()
		p = self.refWidget.mapToGlobal( QtCore.QPoint( 0, h ) )
		return p

	def gotoObject( self ):
		assetBrowser = app.getModule( 'asset_browser' )
		if assetBrowser:
			assetBrowser.locateAsset( self.target )

	def clearObject( self ):
		self.setValue( None )

	def setFocus( self ):
		self.refWidget.setFocus()


##----------------------------------------------------------------##

registerFieldEditor( AssetRefType, AssetRefFieldEditor )
