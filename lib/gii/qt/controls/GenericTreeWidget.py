
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class NoEditItemDelegate( QtGui.QStyledItemDelegate ):
	def createEditor( *args ):
		return None

##----------------------------------------------------------------##
class GenericTreeWidget( QtGui.QTreeWidget ):
	def __init__( self, *args, **option ):
		super(GenericTreeWidget, self).__init__(*args)
		self.noEditItemDelegate = NoEditItemDelegate( self )
		self.refreshing = False
		self.option = option

		self.rootItem = self.invisibleRootItem()
		
		headerInfo = self.getHeaderInfo()
		headerItem = QtGui.QTreeWidgetItem()
		self.setHeaderItem(headerItem)
		for i in range( 0, len(headerInfo) ):
			info =  headerInfo[i]
			headerItem.setText ( i, info[0] )
			w = info[1]
			if w>0:
				self.setColumnWidth ( i, info[1] )
			if i > 0:
				self.setItemDelegateForColumn( i, self.noEditItemDelegate )

		self.setSortingEnabled( option.get('sorting', True) )
		if option.get( 'multiple_selection', False ):
			self.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection )
		else:
			self.setSelectionMode( QtGui.QAbstractItemView.SingleSelection )

		dragMode = option.get( 'drag_mode', None )
		if dragMode:
			self.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
			
		self.setAlternatingRowColors( option.get('alternating_color', False) )
		self.setExpandsOnDoubleClick( False )
		self.sortByColumn( 0, 0 )

		self.itemDoubleClicked    .connect( self.onDClicked )
		self.itemClicked          .connect( self.onClicked )
		self.itemSelectionChanged .connect( self.onItemSelectionChanged )
		self.itemActivated        .connect( self.onItemActivated )
		self.itemChanged          .connect( self._onItemChanged )

		self.setIndentation( 15 )
		self.clear()


	def clear( self ):
		super( GenericTreeWidget, self ).clear()
		self.rootItem.node = None
		self.nodeDict = {}

	def rebuild( self ):
		self.clear()
		rootNode = self.getRootNode()
		if rootNode:
			self.addNode( rootNode )
			self.loadTreeStates()

	def addNode( self, node, addChildren = True, **option ):
		assert not node is None, 'attempt to insert null node '
		if self.nodeDict.has_key( node ): return
		pnode = self.getNodeParent( node )
		assert pnode != node, 'parent is item itself'
		if not pnode :
			item = self.rootItem
		else:
			pitem = self.getItemByNode( pnode )
			if not pitem:
				pitem = self.addNode( pnode, False )
			item  = self.createItem( node )			
			item.node = node
			assert pitem, ( 'node not found in tree:%s' % repr(pnode) )
			#find best new item index
			if not self.isSortingEnabled():
				newindex = None
				for i in range( pitem.childCount() ):
					childItem = pitem.child( i )
					node1 = childItem.node
					if self.compareNodes( node, node1 ):
						newindex = i
						break
				if newindex:
					pitem.insertChild( i, item )
				else:
					pitem.addChild( item )
			else:
				pitem.addChild( item )

		self.nodeDict[ node ]=item

		if option.get( 'expand', True ):
			item.setExpanded( True )
			
		# if pnode:
		self.updateItem( node )
		if addChildren:
			children = self.getNodeChildren( node )
			if children:
				for child in children:
					self.addNode( child, True, **option )
		return item


	def getItemByNode(self, node):
		return self.nodeDict.get( node, None )

	def getNodeByItem( self, item ):
		if hasattr( item, 'node' ):
			return item.node
		return None

	def hasNode( self, node ):
		return self.getItemByNode( node ) != None

	def setNodeExpanded( self, node, expanded = True ):
		item = self.getItemByNode( node )
		if not item: return False
		item.setExpanded( expanded )
		return True

	def setAllExpanded( self, expanded = True ):
		for item in self.nodeDict.values():
			item.setExpanded( expanded )

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
		item=self.getItemByNode( node )
		if item:
			self.updateItemContent( item, node, **option )
			if option.get('updateChildren', False):
				children = self.getNodeChildren( node )
				if children:
					for child in children:
						self.refreshNodeContent( child , **option )

	def updateItem(self, node, **option ):
		return self._updateItem( node, None, **option )

	def _updateItem(self, node, updateLog=None, **option):
		item = self.getItemByNode(node)
		if not item: return False
		if not updateLog: updateLog={} #for avoiding duplicated updates
		if updateLog.has_key(node): return False
		updateLog[node]=True

		self.refreshing = True
		self.updateItemContent( item, node, **option )
		self.refreshing = False

		if option.get('updateChildren',False):
			children = self.getNodeChildren( node )
			if children:
				for child in children:
					self._updateItem(child, updateLog, **option)

		return True

	def _removeItem( self, item ):
		for child in item.takeChildren():
			self._removeItem( child )
		node = item.node
		item.node = None
		del self.nodeDict[ node ]
		( item.parent() or self.rootItem ).removeChild( item )
		return True

	def removeNode(self, node):		
		item = self.getItemByNode( node )
		if item and item!=self.rootItem:
			self._removeItem( item )
			return True
		return False

	def selectNode( self, node, **kw ):
		if not kw.get( 'add', False ):
				self.selectionModel().clearSelection()
		if not node: return
		if isinstance( node, (tuple, list) ):
			for n in node:
				item = self.getItemByNode( n )
				if item:
					item.setSelected( True )
			if item and kw.get('goto',True):
				self.scrollToItem( item )
		else:
			item=self.getItemByNode(node)
			if item:
				item.setSelected(True)
				if kw.get('goto',True) : self.scrollToItem(item)

	def editNode( self, node, col = 0 ):
		item = self.getItemByNode( node )
		if item:
			self.editItem( item, col )

	def scrollToNode( self, node ):
		item = self.getItemByNode( node )
		if item:
			self.scrollToItem( item )

	def setNodeVisible( self, node, visible = True ):
		item = self.getItemByNode( node )
		if item:
			item.setHidden( not visible )

	def sortOrder( self ):
		headerView = self.header()
		return headerView.sortIndicatorOrder()
	
	def getSelection( self )	:
		return [ item.node for item in self.selectedItems() ]

	def foldAllItems( self ):
		for item in self.nodeDict.values():
			if item:
				item.setExpanded( False )

	def expandAllItems( self ):
		for item in self.nodeDict.values():
			if item:
				item.setExpanded( True )

	##----------------------------------------------------------------##
	## VIRTUAL Functions
	##----------------------------------------------------------------##	
	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getRootNode( self ):
		return None

	def getNodeParent( self, node ): # reimplemnt for target node
		return None

	def getNodeChildren( self, node ):
		return []

	def createItem( self, node ):
		item = QtGui.QTreeWidgetItem()
		flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
		if self.option.get( 'editable', False ):
			flags |= Qt.ItemIsEditable 
		item.setFlags ( flags )
		return item

	def updateItemContent( self, item, node, **option ):
		pass

	def getHeaderInfo( self ):
		return [('Name',100), ('State',30)]

	def compareNodes( self, n1, n2 ):
		return False


	# def dropEvent( self, ev ):		
	# 	p = self.dropIndicatorPosition()
	# 	pos = False
	# 	if p == QtGui.QAbstractItemView.OnItem: #reparent
	# 		pos = 'on'
	# 	elif p == QtGui.QAbstractItemView.AboveItem:
	# 		pos = 'above'
	# 	elif p == QtGui.QAbstractItemView.BelowItem:
	# 		pos = 'below'
	# 	else:
	# 		pos = 'viewport'

	# 	target = self.itemAt( ev.pos() )
	# 	self.onDropEvent( target, pos, ev )
	# 	super( GenericTreeWidget, self ).dropEvent( ev )
		
	##----------------------------------------------------------------##
	# Event Callback
	##----------------------------------------------------------------##
	def onClicked(self, item, col):
		pass

	def onDClicked(self, item, col):
		pass
		
	def onItemSelectionChanged(self):
		pass

	def onItemActivated(self, item, col):
		pass

	def _onItemChanged( self, item, col ):
		if self.refreshing: return
		return self.onItemChanged( item, col )

	def onItemChanged( self, item, col ):
		pass

	def keyPressEvent( self, ev ):
		key = ev.key()
		if key in ( Qt.Key_Delete, Qt.Key_Backspace ):			
			self.onDeletePressed()
		return super( GenericTreeWidget, self ).keyPressEvent( ev )

	def onDeletePressed( self ):
		pass
	

		
