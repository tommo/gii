from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt, QSize
from PyQt4.QtGui import QApplication
##----------------------------------------------------------------##
class no_editItemDelegate( QtGui.QStyledItemDelegate ):
	def createEditor( *args ):
		return None


##----------------------------------------------------------------##
class GenericListWidget( QtGui.QListWidget ):
	def __init__( self, *args, **option ):
		super( GenericListWidget, self ).__init__( *args )
		
		self.nodeDict = {}
		self.refreshing = False
		self.option = option

		if option.get( 'mode', 'list' ) == 'icon':
			self.setViewMode( QtGui.QListView.IconMode )
			
		self.itemDoubleClicked    .connect( self.onDClicked )
		self.itemClicked          .connect( self.onClicked )
		self.itemSelectionChanged .connect( self.onItemSelectionChanged )
		self.itemActivated        .connect( self.onItemActivated )
		self.itemChanged          .connect( self._onItemChanged )

	def getOption( self, k, v ):
		defOption = self.getDefaultOptions()
		option    = self.option
		if defOption:
			defValue = defOption.get( k, v )
		else:
			defValue = v
		return option.get( k, defValue )


	def rebuild( self ):
		self.clear()
		self.nodeDict = {}
		nodes = self.getNodes()
		for node in nodes:
			self.addNode( node )

	def getItemByNode( self, node ):
		return self.nodeDict.get( node, None )

	def getNodeByItem( self, item ):
		if hasattr( item, 'node' ):
			return item.node
		return None

	def refreshNode(self, node):
		item = self.getItemByNode( node )
		if item:
			if item == self.rootItem:
				self.rebuild()
				return
			self.removeNode( node )
			self.addNode( node )

	def refreshAllContent( self ):
		for node in self.nodeDict.keys():
			self.refreshNodeContent( node )

	def refreshNodeContent( self, node, **option ):
		prevRefreshing = self.refreshing
		self.refreshing = True
		item=self.getItemByNode( node )
		if item:
			self.updateItemContent( item, node, **option )
		self.refreshing = prevRefreshing

	def refreshAllContent( self ):
		for node in self.nodeDict.keys():
			self.refreshNodeContent( node )

	def hasNode( self, node ):
		return self.getItemByNode( node ) != None

	def addNode( self, node, **option ):
		assert not node is None, 'attempt to insert null node '
		item = self.nodeDict.get( node, None )
		if item: return item
		item = QtGui.QListWidgetItem( self )
		self.nodeDict[ node ] = item
		item.node = node
		self.updateItem( node )
		return item

	def getItemFlags( self, node ):
		return {}

	def _calcItemFlags( self, node ):
		flags = Qt.ItemIsEnabled 
		flagNames = self.getItemFlags( node )
		if flagNames.get( 'selectable', True ): flags |= Qt.ItemIsSelectable
		if flagNames.get( 'draggable',  True ): flags |= Qt.ItemIsDragEnabled
		if flagNames.get( 'droppable',  True ): flags |= Qt.ItemIsDropEnabled
		if self.getOption( 'editable', False ):
			if flagNames.get( 'editable',   True ): flags |= Qt.ItemIsEditable
		return flags

	def updateItem( self, node, **option ):
		item = self.getItemByNode(node)
		if not item: return False
		self.refreshing = True
		self.updateItemContent( item, node, **option )
		flags = self._calcItemFlags( node )
		item.setFlags( flags )
		self.refreshing = False

	def selectNode( self, node, **kwargs ):
		if not kwargs.get( 'add', False ):
				self.selectionModel().clearSelection()
		if not node: return
		if isinstance( node, (tuple, list) ):
			for n in node:
				item = self.getItemByNode( n )
				if item:
					item.setSelected( True )
			if kwargs.get('goto',True) : 
				first = len( node ) > 0 and node[0]
				if first:
					self.gotoNode( first )
		else:
			item = self.getItemByNode( node )
			if item:
				item.setSelected( True )
				if kwargs.get('goto',True) : 
					self.gotoNode( node )

	def getSelection( self ):
		return [ item.node for item in self.selectedItems() ]

	def getFirstSelection( self ):
		for item in self.selectedItems():
			return item.node
		return None

	def setFocusedItem(self, item ):
		idx = self.indexFromItem( item )
		if idx:
			self.setCurrentIndex( idx )

	def editNode( self, node ):
		item = self.getItemByNode( node )
		if item:
			self.editItem( item )

	def scrollToNode( self, node ):
		item = self.getItemByNode( node )
		if item:
			self.scrollToItem( item )

	def gotoNode( self, node ):
		item = self.getItemByNode( node )
		if item:
			self.scrollToItem( item )
			self.setCurrentItem( item, QtGui.QItemSelectionModel.Current )
			# self.moveCursor( self.MoveUp, Qt.NoModifier )
	
	##----------------------------------------------------------------##
	##Virtual
	##----------------------------------------------------------------##
	def getDefaultOptions( self ):
		return None

	def getNodes( self ):
		return []		

	def updateItemContent( self, item, node, **option ):
		pass


	##----------------------------------------------------------------##
	# Event Callback
	##----------------------------------------------------------------##
	def onClicked(self, item ):
		pass

	def onDClicked(self, item ):
		pass
		
	def onItemSelectionChanged(self):
		pass

	def onItemActivated(self, item):
		pass

	def onClipboardCopy( self ):
		pass

	def onClipboardCut( self ):
		pass

	def onClipboardPaste( self ):
		pass

	def _onItemChanged( self, item ):
		if self.refreshing: return
		return self.onItemChanged( item )

	def onItemChanged( self, item ):
		pass

	def onDeletePressed( self ):
		pass