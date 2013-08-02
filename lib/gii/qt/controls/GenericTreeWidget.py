
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class GenericTreeWidget( QtGui.QTreeWidget ):
	def __init__( self, *args ):
		super(GenericTreeWidget, self).__init__(*args)
		self.rootItem = self.invisibleRootItem()

		headerInfo = self.getHeaderInfo()
		headerItem = QtGui.QTreeWidgetItem()
		self.setHeaderItem(headerItem)
		for i in range( 0, len(headerInfo) ):
			info =  headerInfo[i]
			headerItem.setText  ( i, info[0] )
			w = info[1]
			if w>0:
				self.setColumnWidth ( i, info[1] )

		self.clear()
		self.setSortingEnabled( True )
		self.setSelectionMode( QtGui.QAbstractItemView.ExtendedSelection )
		self.setExpandsOnDoubleClick( False )
		self.sortByColumn(0, 0)

		self.itemDoubleClicked    .connect( self.onDClicked )
		self.itemClicked          .connect( self.onClicked )
		self.itemSelectionChanged .connect( self.onItemSelectionChanged )

		self.setIndentation( 15 )


	def clear( self ):
		super( GenericTreeWidget, self ).clear()
		self.rootItem.node = None
		self.nodeDict = {}

	def rebuild( self ):
		self.clear()
		rootNode = self.getRootNode()
		self.addNode( rootNode )
		self.loadTreeStates()

	def addNode( self, node, addChildren = True ):
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
			pitem.addChild( item )
		self.nodeDict[ node ]=item

		# if pnode:
		self.updateItem( node )
		if addChildren:
			children = self.getNodeChildren( node )
			if children:
				for child in children:
					self.addNode( child )
		return item

	def getItemByNode(self, node):
		return self.nodeDict.get( node, None )

	def getNodeByItem( self, item ):
		if hasattr( item, 'node' ):
			return item.node
		return None

	def refreshNode(self, node):
		item=self.getItemByNode( node )
		if item:
			if item==self.rootItem:
				self.rebuild()
				return
			self.removeNode( node )
			self.addNode( node )

	def updateItem(self, node, **option ):
		return self._updateItem( node, None, **option )

	def _updateItem(self, node, updateLog=None, **option):
		item = self.getItemByNode(node)
		if not item: return False
		if not updateLog: updateLog={} #for avoiding duplicated updates
		if updateLog.has_key(node): return False
		updateLog[node]=True
		
		self.updateItemContent( item, node, **option )

		if option.get('updateChildren',False):
			children = self.getNodeChildren( node )
			if children:
				for child in children:
					self._updateItem(child, updateLog, **option)

		return True

	def removeNode(self, node):		
		item = self.getItemByNode(node)
		if item and item!=self.rootItem:
			(item.parent() or self.rootItem).removeChild(item)

	def selectNode(self, node):
		item=self.getItemByNode(node)
		if item:
			self.selectionModel().clearSelection()
			item.setSelected(True)
			self.scrollToItem(item)
	
		
	##----------------------------------------------------------------##
	## VIRTUAL Functions
	##----------------------------------------------------------------##
	def onClicked(self, item, col):
		pass

	def onDClicked(self, item, col):
		pass
		
	def onItemSelectionChanged(self):
		pass
	
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
		return QtGui.QTreeWidgetItem( )

	def updateItemContent( self, item, node, **option ):
		pass

	def getHeaderInfo( self ):
		return [('Name',100), ('State',30)]


		
