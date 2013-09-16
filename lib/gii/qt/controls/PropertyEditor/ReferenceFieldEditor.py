from gii.core import *
from gii.core.model import *
from PropertyEditor import FieldEditor, registerFieldEditor
from gii.qt.helpers import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject


##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

ReferenceBrowserForm,BaseClass = uic.loadUiType(getModulePath('referenceBrowser.ui'))

##----------------------------------------------------------------##
class WindowAutoHideEventFilter(QObject):
	def eventFilter(self, obj, event):
		e = event.type()
		if e == QEvent.WindowDeactivate:
			obj.hide()
		return QObject.eventFilter( self, obj, event )

##----------------------------------------------------------------##
class ReferenceBrowser( QtGui.QWidget ):
	_singleton = None
	@staticmethod
	def get():
		if ReferenceBrowser._singleton:
			return ReferenceBrowser._singleton
		return ReferenceBrowser( None )

	@staticmethod
	def start( editor, targetType, context ):
		browser = ReferenceBrowser.get()
		browser.setEditor( editor )
		browser.move( editor.getBrowserPos() )
		browser.setTarget( targetType, context )
		browser.show()

		
	def __init__(self, *args ):
		super( ReferenceBrowser, self ).__init__( *args )
		ReferenceBrowser._singleton = self

		self.setWindowFlags( Qt.Popup )
		self.ui = ReferenceBrowserForm()
		self.ui.setupUi( self )
		
		self.installEventFilter( WindowAutoHideEventFilter( self ) )
		self.editor = None
		self.treeResult = addWidgetWithLayout( 
				ReferenceBrowserTree(
					self.ui.containerResultTree,
					multiple_selection = False,
					editable = False
				) 
			)
		self.ui.textTerms.textEdited.connect( self.onTermsChanged )
		self.ui.textTerms.returnPressed.connect( self.onTermsReturn )
		self.treeResult.browser = self
		self.entries = None
		self.setFixedSize( 400, 250 )

	def sizeHint( self ):
		return QtCore.QSize( 300, 250 )

	def setTarget( self, typeId, context = None ):
		self.ui.textTerms.setText('')
		self.targetType = typeId
		self.entries = ModelManager.get().enumerateObjects( typeId, context )
		self.ui.textTerms.setFocus()
		self.treeResult.rebuild()

	def setEditor( self, editor ):
		self.editor = editor		

	def setSelection( self, obj ):
		if self.editor:
			self.editor.setValue( obj )
			self.editor.setFocus()
			self.hide()

	def getObjectRepr( self, obj ):
		return ModelManager.get().getObjectRepr( obj )

	def getObjectTypeRepr( self, obj ):
		return ModelManager.get().getObjectTypeRepr( obj )

	def onTermsChanged( self, text ):
		#TODO: set filter
		pass

	def onTermsReturn( self ):
		self.treeResult.setFocus()		
		#todo:select first

	def hideEvent( self, ev ):
		self.setEditor( None )
		self.treeResult.clear()
		return super( ReferenceBrowser, self ).hideEvent( ev )
	
##----------------------------------------------------------------##
class ReferenceBrowserTree(GenericTreeWidget):
	def getHeaderInfo( self ):
		return [('Name', 300), ('Type', 80)]

	def getRootNode( self ):
		return self.browser

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.getRootNode(): return None
		return self.getRootNode()
		
	def getNodeChildren( self, node ):
		if node == self.browser:
			return self.browser.entries
		else:
			return []

	def updateItemContent( self, item, node, **option ):
		if node == self.getRootNode(): return
		name = self.browser.getObjectRepr( node )
		typeName = self.browser.getObjectTypeRepr( node )		
		item.setText( 0, name )
		item.setText( 1, typeName )
		
	def onItemSelectionChanged(self):
		for node in self.getSelection():
			self.browser.setSelection( node )
			return

	def onItemActivated( self, item, col ):
		node = item.node
		self.browser.setSelection( node )


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
			self.buttonRef.setText( 'Object' ) #TODO:
			self.buttonGoto.show()
			self.buttonClear.show()

	def setRefName( self, name ):
		if isinstance( name, (unicode, str) ):
			self.buttonRef.setText( name )
		else:
			logging.error('unknown ref name type:' + repr( name ) )
			self.buttonRef.setText( repr( name ) )

##----------------------------------------------------------------##
class ReferenceFieldEditor( FieldEditor ):	
	def setTarget( self, parent, field ):
		super( ReferenceFieldEditor, self ).setTarget( parent, field )
		self.targetType    = field.getType()
		self.targetContext = None  #TODO
		self.target = None

	def clear( self ):
		ReferenceBrowser.get().hide()

	def get( self ):
		#TODO
		return None

	def set( self, value ):
		self.target = value
		self.refWidget.setRef( value )
		if value:
			name = ModelManager.get().getObjectRepr( value )
			self.refWidget.setRefName( name )

	def setValue( self, value ):		
		self.set( value )
		self.notifyChanged( value )

	def initEditor( self, container ):
		self.refWidget = widget = ReferenceFieldWidget( container )
		widget.buttonRef.clicked.connect( self.openBrowser )
		widget.buttonGoto.clicked.connect( self.gotoObject )
		widget.buttonClear.clicked.connect( self.clearObject )
		return self.refWidget

	def openBrowser( self ):			
		ReferenceBrowser.start( self, self.targetType, self.targetContext)

	def getBrowserPos( self ):
		size = self.refWidget.size()
		w, h = size.width(), size.height()
		p = self.refWidget.mapToGlobal( QtCore.QPoint( 0, h ) )
		return p

	def gotoObject( self ):
		signals.emit( 'selection.hint', self.target )

	def clearObject( self ):
		self.setValue( None )

	def setFocus( self ):
		self.refWidget.setFocus()


##----------------------------------------------------------------##

registerFieldEditor( ReferenceType, ReferenceFieldEditor )
