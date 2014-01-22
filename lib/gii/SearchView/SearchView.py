from gii.core import *
from gii.core.model import *

from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.helpers    import addWidgetWithLayout
from gii.qt.IconCache  import getIcon

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject

import re

from subdist import get_score

_SEARCHVIEW_ITEM_LIMIT = 100

class FuzzyMatcher():
	def __init__(self):
		self.pattern = ''

	def setPattern(self, pattern):
		self.pattern = '.*?'.join(map(re.escape, list(pattern)))

	def score(self, string):
		match = re.search(self.pattern, string)
		if match is None:
			return 0
		else:
			return 100.0 / ((1 + match.start()) * (match.end() - match.start() + 1))

# import difflib
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
def _sortMatchScore( e1, e2 ):
	diff = e2.matchScore - e1.matchScore
	if diff > 0 : return 1
	if diff < 0 : return -1
	if e2.name > e1.name: return 1
	if e2.name < e1.name: return -1
	return 0
	
##----------------------------------------------------------------##
class SearchViewWidget( QtGui.QWidget ):
	def __init__(self, *args ):
		super( SearchViewWidget, self ).__init__( *args )
		self.searchState = None

		self.setWindowFlags( Qt.Popup )
		self.ui = SearchViewForm()
		self.ui.setupUi( self )
		
		self.installEventFilter( WindowAutoHideEventFilter( self ) )
		self.editor = None
		self.treeResult = addWidgetWithLayout( 
				SearchViewTree(
					self.ui.containerResultTree,
					multiple_selection = False,
					editable = False,
					sorting  = False
				) 
			)
		self.treeResult.hideColumn( 0 )
		self.textTerms = addWidgetWithLayout (
			SearchViewTextTerm(self.ui.containerTextTerm )
			)
		self.textTerms.browser = self
		self.textTerms.textEdited.connect( self.onTermsChanged )
		self.textTerms.returnPressed.connect( self.onTermsReturn )

		self.treeResult.browser = self
		self.entries = None
		self.setMinimumSize( 400, 300  )
		self.setMaximumSize( 600, 600  )
		self.multipleSelection = False

		self.setInfo( None )
		self.ui.buttonOK     .clicked .connect( self.onButtonOK )
		self.ui.buttonCancel .clicked .connect( self.onButtonCancel )

		self.ui.buttonAll     .clicked .connect( self.onButtonAll )
		self.ui.buttonInverse .clicked .connect( self.onButtonInverse )
		self.ui.buttonNone    .clicked .connect( self.onButtonNone )

	def sizeHint( self ):
		return QtCore.QSize( 300, 250 )

	def initEntries( self, entries ):
		self.entries = entries or []
		self.textTerms.setText('')
		self.textTerms.setFocus()		
		self.searchState = None
		self.updateVisibleEntries( self.entries )
		self.selectFirstItem()

	def updateVisibleEntries( self, entries, forceSort = False ):
		tree = self.treeResult
		tree.hide()
		root = tree.rootItem
		root.takeChildren()
		entries1 = entries
		# self.visEntries  = entries		
		if entries != self.entries or forceSort:
			entries1 = sorted( entries, cmp = _sortMatchScore )
		if len( entries1 ) > _SEARCHVIEW_ITEM_LIMIT:
			entries1 = entries1[:_SEARCHVIEW_ITEM_LIMIT]
		for e in entries1:
			if not e.treeItem:
				e.treeItem = tree.addNode( e )				 
			else:
				root.addChild( e.treeItem )
		tree.show()

	def updateSearchTerms( self, text ):
		tree = self.treeResult
		if text:
			textU = text.upper()
			globs = textU.split()
			visEntries = []
			for entry in self.entries:
				if entry.matchQuery( globs, textU ):
					visEntries.append( entry )				
			self.updateVisibleEntries( visEntries, True )
		else:
			self.updateVisibleEntries( self.entries )			
		self.selectFirstItem()

	def confirmSelection( self, obj ):
		self.selected = True
		if self.multipleSelection:
			result = []
			for entry in self.entries:
				if entry.checked:
					result.append( entry.obj )
			self.module.selectMultipleObjects( result )
		else:
			self.module.selectObject( obj )

	def setFocus( self ):
		QtGui.QWidget.setFocus( self )
		self.textTerms.setFocus()

	def onTermsChanged( self, text ):
		self.updateSearchTerms( text )		

	def selectFirstItem( self ):
		# if not self.treeResult.getSelection():
		self.treeResult.clearSelection()
		item = self.treeResult.itemAt( 0, 0 )
		if item:
			item.setSelected( True )
			self.treeResult.scrollToItem( item )

	def onTermsReturn( self ):
		for node in self.treeResult.getSelection():
			self.confirmSelection( node.obj )
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

	def setInitialSelection( self, selection ):
		if self.multipleSelection:
			if not selection: return
			for entry in self.entries:
				if entry.obj in selection:
					entry.checked = True
					self.treeResult.refreshNodeContent( entry )
		else:
			for entry in self.entries:
				if entry.obj == selection:
					self.treeResult.selectNode( entry, goto = True )
					break

	def setMultipleSelectionEnabled( self, enabled ):
		self.multipleSelection = enabled
		if enabled:
			self.treeResult.showColumn( 0 )
			self.treeResult.setColumnWidth( 0, 50 )
			self.treeResult.setColumnWidth( 1, 250 )
			self.treeResult.setColumnWidth( 2, 50 )
			self.ui.containerBottom.show()
		else:
			self.treeResult.hideColumn( 0 )
			self.treeResult.setColumnWidth( 0, 0 )
			self.treeResult.setColumnWidth( 1, 300 )
			self.treeResult.setColumnWidth( 2, 50 )
			self.ui.containerBottom.hide()

	def onButtonOK( self ):
		if self.multipleSelection:
			self.confirmSelection( None )

	def onButtonCancel( self ):
		self.hide()

	def onButtonAll( self ):
		if not self.multipleSelection: return
		for entry in self.entries:
			if not entry.checked:
				entry.checked = True
				self.treeResult.refreshNodeContent( entry )

	def onButtonInverse( self ):
		if not self.multipleSelection: return
		for entry in self.entries:
			entry.checked = not entry.checked
			self.treeResult.refreshNodeContent( entry )

	def onButtonNone( self ):
		if not self.multipleSelection: return
		for entry in self.entries:
			if entry.checked:
				entry.checked = False
				self.treeResult.refreshNodeContent( entry )


##----------------------------------------------------------------##
class SearchViewTextTerm( QtGui.QLineEdit):
	def keyPressEvent( self, ev ):
		key = ev.key()
		if key == Qt.Key_Down:
			self.browser.focusResultTree()
			self.browser.treeResult.keyPressEvent( ev )
			return
		return super( SearchViewTextTerm, self ).keyPressEvent( ev )

##----------------------------------------------------------------##
class SearchViewTree(GenericTreeWidget):
	def getHeaderInfo( self ):
		return [('Sel', 50), ('Name', 300), ('Type', 80)]

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
		item.setIcon( 0, getIcon( node.checked and 'checkbox_checked' or 'checkbox_unchecked' ) )
		item.setText( 1, node.name )
		item.setText( 2, node.typeName )
		if node.iconName:
			item.setIcon( 1, getIcon( node.iconName ) )

	# def onItemSelectionChanged(self):
	# 	for node in self.getSelection():
	# 		self.browser.confirmSelection( node.obj )
	# 		return

	def createItem( self, node ):
		item = SearchViewItem()
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
		if self.option.get( 'editable', False ):
			flags |= Qt.ItemIsEditable 
		item.setFlags ( flags )
		return item

	def onClicked( self, item, col ):
		node = item.node
		if self.browser.multipleSelection:
			node.checked = not node.checked
			self.refreshNodeContent( node )
		else:
			self.browser.confirmSelection( node.obj )

	def onItemActivated( self, item, col ):
		node = item.node
		self.browser.confirmSelection( node.obj )

	def onClipboardCopy( self ):
		clip = QtGui.QApplication.clipboard()
		out = None
		for node in self.getSelection():
			if out:
				out += "\n"
			else:
				out = ""
			out += node.name
		clip.setText( out )
		return True

	def keyPressEvent(self, event):
		key = event.key()		
		if event.modifiers() == Qt.NoModifier:
			if key in ( Qt.Key_Return, Qt.Key_Enter ):
				for node in self.getSelection():
					self.browser.confirmSelection( node.obj )
					return
			if ( int(key) >= int(Qt.Key_0) and int(key) <= int(Qt.Key_Z) ) \
				or key in [ Qt.Key_Delete, Qt.Key_Backspace, Qt.Key_Space ] :
				self.browser.textTerms.setFocus()
				self.browser.textTerms.keyPressEvent( event )
				return
		return super( SearchViewTree, self ).keyPressEvent( event )

##----------------------------------------------------------------##
class SearchEntry(object):
	def __init__( self, obj, name, typeName, iconName ):
		self.visible    = False
		self.treeItem   = None
		self.matchScore = 0
		self.obj        = obj
		self.name       = name
		self.typeName   = typeName
		self.iconName   = iconName
		self.typeNameU  = typeName.upper()
		self.nameU      = name.upper()
		self.compareStr = typeName + ': ' + name
		self.checked    = False	

	def matchQuery( self, globs, text ):
		#method 1
		# score = 0
		# name = self.nameU
		# typeName = self.typeNameU
		# for i, t in enumerate( globs ):
		# 	pos = name.find( t )
		# 	if pos >= 0:
		# 		score += ( 2 + len(t) + i*0.5 )
		# if globs[0] in typeName:
		# 	findInType = True
		# 	score += 1		
		score = 0
		name = self.nameU
		typeName = self.typeNameU
		for i, t in enumerate( globs ):
			pos = name.find( t )
			if pos >= 0:
				score += 2
			else:
				score += get_score( t, name ) * 1
		
		if globs[0] in typeName:
			findInType = True
			score += 0.5

		# score1 = SequenceMatcher( None, self.typeNameU, text ).ratio()
		# score2 = SequenceMatcher( None, self.nameU, text ).ratio()
		# score = score1 + score2 * 5		
		
		self.matchScore = score
		return score > 0

##----------------------------------------------------------------##
class SearchView( EditorModule ):	
	def __init__( self ):
		self.enumerators = []
		self.onCancel    = None
		self.onSelection = None
		self.onSearch    = None
		self.visEntries  = None

	def getName( self ):
		return 'search_view'

	def getDependency( self ):
		return ['qt']

	def onLoad( self ):
		self.window = SearchViewWidget( None )
		self.window.module = self

	def request( self, **option ):
		pos        = option.get( 'pos', QtGui.QCursor.pos() )
		typeId     = option.get( 'type', None )
		context    = option.get( 'context', None )
		action     = option.get( 'action', 'select' )
		info       = option.get( 'info', None )
		initial    = option.get( 'initial', None )
		multiple   = option.get( 'multiple_selection', False )

		self.onSelection = option.get( 'on_selection', None )
		self.onCancel    = option.get( 'on_cancel',    None )
		self.onSearch    = option.get( 'on_search',    None )

		self.window.move( pos )
		self.window.show()
		self.window.raise_()
		self.window.setFocus()
		self.window.setInfo( info )
		entries = self.enumerateSearch( typeId, context )
		self.window.initEntries( entries )
	
		self.window.setMultipleSelectionEnabled( multiple )
		if initial:
			self.window.setInitialSelection( initial )

	def selectObject( self, obj ):
		if self.window.searchState: return
		self.window.searchState = 'selected'
		if self.onSelection:
			self.onSelection( obj )
		self.window.hide()

	def selectMultipleObjects( self, objs ):
		if self.window.searchState: return
		self.window.searchState = 'selected'
		if self.onSelection:
			self.onSelection( objs )
		self.window.hide()		

	def cancelSearch( self ):
		if self.window.searchState: return
		self.window.searchState = 'cancel'
		if self.onCancel:
			self.onCancel()
		self.window.hide() 

	def registerSearchEnumerator( self, enumerator ):
		#format [  ( obj,  objName, objTypeName, objIcon ), ...  ] or None
		self.enumerators.append( enumerator )

	def enumerateSearch( self, typeId, context ):
		allResult = []
		if self.onSearch:
			allResult = self.onSearch( typeId, context )
		else:
			for e in self.enumerators:
				result = e( typeId, context )
				if result:
					allResult += result
		return [ SearchEntry( *r ) for r in allResult ]

##----------------------------------------------------------------##
class SearchViewItem( QtGui.QTreeWidgetItem ):
	def __lt__( self, other ):
		node0 = self.node
		node1 = hasattr(other, 'node') and other.node or None
		if not node1:
			return True
		t0 = - node0.matchScore
		t1 = - node1.matchScore
		if t0 < t1: return True
		if t0 == t1 : return node0.name < node1.name
		return False
		
##----------------------------------------------------------------##
searchView = SearchView()
searchView.register()
def requestSearchView( **option ):
	return searchView.request( **option )

def registerSearchEnumerator( enumerator ):
	searchView.registerSearchEnumerator( enumerator )

