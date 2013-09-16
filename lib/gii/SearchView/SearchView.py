from fuzzywuzzy import fuzz

from gii.core import *
from gii.core.model import *

from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.helpers import addWidgetWithLayout

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject

##----------------------------------------------------------------##
def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

SearchViewForm,BaseClass = uic.loadUiType(getModulePath('SearchView.ui'))

class WindowAutoHideEventFilter(QObject):
	def eventFilter(self, obj, event):
		e = event.type()		
		if e == QEvent.WindowDeactivate:
			obj.hide()
		return QObject.eventFilter( self, obj, event )

##----------------------------------------------------------------##
class SearchViewWidget( QtGui.QWidget ):
	def __init__(self, *args ):
		super( SearchViewWidget, self ).__init__( *args )

		self.setWindowFlags( Qt.Popup )
		self.ui = SearchViewForm()
		self.ui.setupUi( self )
		
		self.installEventFilter( WindowAutoHideEventFilter( self ) )
		self.editor = None
		self.treeResult = addWidgetWithLayout( 
				SearchViewTree(
					self.ui.containerResultTree,
					multiple_selection = False,
					editable = False
				) 
			)
		self.textTerms = addWidgetWithLayout (
			SearchViewTextTerm(self.ui.containerTextTerm )
			)
		self.textTerms.browser = self
		self.textTerms.textEdited.connect( self.onTermsChanged )
		self.textTerms.returnPressed.connect( self.onTermsReturn )

		self.treeResult.browser = self
		self.entries = None
		self.setFixedSize( 400, 250 )		

		self.setInfo( None )

	def sizeHint( self ):
		return QtCore.QSize( 300, 250 )

	def setQuery( self, typeId, context = None ):
		self.textTerms.setText('')
		self.textTerms.setFocus()
		self.targetType = typeId
		self.entries = self.module.enumerateSearch( typeId, context )
		self.treeResult.rebuild()
		self.searchState = None
		self.selectFirstItem()


	def setSelection( self, obj ):
		self.selected = True
		self.module.selectObject( obj )

	def setFocus( self ):
		QtGui.QWidget.setFocus( self )
		self.textTerms.setFocus()

	def onTermsChanged( self, text ):
		if text:
			globs = text.split()
			globs1 = []
			for g in globs:
				if len(g) > 1: globs1.append( g.upper() )
			for entry in self.entries:
				entry.visible = entry.matchQuery( globs1 )
				self.treeResult.setNodeVisible( entry, entry.visible )
		else:
			for entry in self.entries:
				entry.visible = True
				self.treeResult.setNodeVisible( entry, True )

		self.selectFirstItem()

	def selectFirstItem( self ):
		if not self.treeResult.getSelection():
			item = self.treeResult.itemAt( 0, 0 )
			if item:
				item.setSelected( True )

	def onTermsReturn( self ):
		for node in self.treeResult.getSelection():
			self.setSelection( node.obj )
			return

	def hideEvent( self, ev ):
		if not self.searchState:
			self.module.cancelSearch()
		self.treeResult.clear()
		return super( SearchViewWidget, self ).hideEvent( ev )

	def focusResultTree( self ):
		self.selectFirstItem()
		self.treeResult.setFocus()

	def setInfo( self, text ):
		if text:
			self.ui.labelInfo.setText( text )
			self.ui.labelInfo.show()
		else:
			self.ui.labelInfo.hide()


##----------------------------------------------------------------##
class SearchViewTextTerm( QtGui.QLineEdit):
	def keyPressEvent( self, ev ):
		key = ev.key()
		if key == Qt.Key_Down:
			self.browser.focusResultTree()

		return super( SearchViewTextTerm, self ).keyPressEvent( ev )

##----------------------------------------------------------------##
class SearchViewTree(GenericTreeWidget):
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
		item.setText( 0, node.name )
		item.setText( 1, node.typeName )
		
	# def onItemSelectionChanged(self):
	# 	for node in self.getSelection():
	# 		self.browser.setSelection( node.obj )
	# 		return

	def onClicked( self, item, col ):
		node = item.node
		self.browser.setSelection( node.obj )


	def onItemActivated( self, item, col ):
		node = item.node
		self.browser.setSelection( node.obj )

	def keyPressEvent(self, event):
		key = event.key()		
		if key in ( Qt.Key_Return, Qt.Key_Enter ):
			for node in self.getSelection():
				self.browser.setSelection( node.obj )
				return

		return super( SearchViewTree, self ).keyPressEvent( event )

##----------------------------------------------------------------##
class SearchEntry(object):
	def __init__( self, obj, name, typeName, iconName ):
		self.visible    = True

		self.obj      = obj
		self.name     = name
		self.typeName = typeName
		self.iconName = iconName

	def matchQuery( self, globs ):
		# ratio = fuzz.partial_ratio( text, self.name )
		# if ratio > 80: return True
		# ratio = fuzz.partial_ratio( text, self.typeName )
		# if ratio > 80: return True
		for t in globs:
			if t in self.name.upper(): return True
			if t in self.typeName.upper(): return True
		return False


##----------------------------------------------------------------##
class SearchView( EditorModule ):	
	def __init__( self ):
		self.enumerators = []
		self.onCancel    = None
		self.onSelection = None

	def getName( self ):
		return 'search_view'

	def getDependency( self ):
		return ['qt']

	def onLoad( self ):
		self.window = SearchViewWidget( None )
		self.window.module = self

	def request( self, **option ):
		pos     = option.get( 'pos', QtGui.QCursor.pos() )
		typeId  = option.get( 'type', None )
		context = option.get( 'context', None )
		action  = option.get( 'action', 'select' )
		info    = option.get( 'info', None )

		self.onSelection = option.get( 'on_selection', None )
		self.onCancel    = option.get( 'on_cancel', None )

		self.window.move( pos )
		self.window.show()
		self.window.raise_()
		self.window.setFocus()
		self.window.setQuery( typeId, context )
		self.window.setInfo( info )

	def selectObject( self, obj ):
		if self.window.searchState: return
		self.window.searchState = 'selected'
		if self.onSelection:
			self.onSelection( obj )
		self.window.hide()

	def cancelSearch( self ):
		if self.window.searchState: return
		self.window.searchState = 'cancel'
		if self.onCancel:
			self.onCancel( obj )
		self.window.hide() 

	def registerSearchEnumerator( self, enumerator ):
		#format [  ( obj,  objName, objTypeName, objIcon ), ...  ] or None
		self.enumerators.append( enumerator )

	def enumerateSearch( self, typeId, context ):
		allResult = []
		for e in self.enumerators:
			result = e( typeId, context )
			if result:
				allResult += result
		return [ SearchEntry( *r ) for r in allResult ]

##----------------------------------------------------------------##
searchView = SearchView()
searchView.register()
def requestSearchView( **option ):
	return searchView.request( **option )

def registerSearchEnumerator( enumerator ):
	searchView.registerSearchEnumerator( enumerator )

