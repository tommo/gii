from gii.core.model import *
from PropertyEditor import FieldEditor, registerFieldEditor
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
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
		browser.show()
		browser.setTarget( targetType, context )

		
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

	def sizeHint( self ):
		return QtCore.QSize( 400, 250 )

	def setTarget( self, typeId, context = None ):
		self.targetType = typeId
		entries = ModelManager.get().enumerateObjects( typeId, context )
		# for entry in entries:
		# 	# obj, name, className = entry
		# 	self.treeResult.addNode( entry )
		self.entries = entries
		self.ui.textTerms.setFocus()
		self.treeResult.rebuild()

	def setEditor( self, editor ):
		self.editor = editor		

	def setSelection( self, obj ):
		if self.editor:
			self.editor.set( obj )
			self.editor.setFocus()
			self.hide()

	def onTermsChanged( self, text ):
		#TODO: set filter
		pass

	def onTermsReturn( self ):
		self.treeResult.setFocus()		
		#todo:select first

	def hideEvent( self, ev ):
		self.setEditor( None )
		return super( ReferenceBrowser, self ).hideEvent( ev )
	
##----------------------------------------------------------------##
class ReferenceBrowserTree(GenericTreeWidget):
	def getHeaderInfo( self ):
		return [('Name', 200), ('Type', 80)]

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
		item.setText( 0, node[1] )
		item.setText( 1, node[2] )
		
	def onItemSelectionChanged(self):
		for node in self.getSelection():
			self.browser.setSelection( node[0] )
			return

	def onItemActivated( self, item, col ):
		node = item.node
		self.browser.setSelection( node[0] )


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
			self.buttonRef.setText( '<None>' )
			self.buttonGoto.hide()
		else:
			self.buttonRef.setText( 'Object' ) #TODO:
			self.buttonGoto.show()

##----------------------------------------------------------------##
class ReferenceFieldEditor( FieldEditor ):	
	def setTarget( self, parent, field ):
		super( ReferenceFieldEditor, self ).setTarget( parent, field )
		self.targetType    = field.getType()
		self.targetContext = None  #TODO

	def clear( self ):
		ReferenceBrowser.get().hide()

	def get( self ):
		#TODO
		return None

	def set( self, value ):
		self.refWidget.setRef( value )

	def setValue( self, value ):		
		self.set( value )
		self.notifyChanged( value )

	def initEditor( self, container ):
		self.refWidget = widget = ReferenceFieldWidget( container )
		widget.buttonRef.clicked.connect( self.openBrowser )
		widget.buttonGoto.clicked.connect( self.gotoObject )
		return self.refWidget

	def openBrowser( self ):			
		ReferenceBrowser.start( self, self.targetType, self.targetContext)

	def getBrowserPos( self ):
		size = self.refWidget.size()
		w, h = size.width(), size.height()
		p = self.refWidget.mapToGlobal( QtCore.QPoint( 0, h ) )
		return p

	def gotoObject( self ):
		pass

	def setFocus( self ):
		self.refWidget.setFocus()




registerFieldEditor( ReferenceType, ReferenceFieldEditor )
