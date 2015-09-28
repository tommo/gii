import random
import json
import os

from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt, QSize

from PyQt4.QtGui      import QBrush, QStyle, QColor

from gii.core         import *
from gii.qt           import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget, GenericTreeFilter
from gii.qt.controls.GenericListWidget import GenericListWidget
from gii.qt.dialogs   import requestString, alertMessage, requestConfirm

from AssetEditor      import AssetEditorModule, getAssetSelectionManager



##----------------------------------------------------------------##
#TODO: allow sort by other column
class AssetFolderTreeItem(QtGui.QTreeWidgetItem):
	def __lt__(self, other):
		node0 = self.node
		node1 = hasattr(other, 'node') and other.node or None
		if not node1:
			return True
		tree = self.treeWidget()

		# if not tree:
		# 	col = 0
		# else:
		# 	col = tree.sortColumn()		
		t0 = node0.getType()
		t1 = node1.getType()
		if t1!=t0:			
			if tree.sortOrder() == 0:
				if t0 == 'folder': return True
				if t1 == 'folder': return False
			else:
				if t0 == 'folder': return False
				if t1 == 'folder': return True
		return super( AssetFolderTreeItem, self ).__lt__( other )
		# return node0.getName().lower()<node1.getName().lower()

##----------------------------------------------------------------##

class AssetFolderTreeFilter( GenericTreeFilter ):
	pass

##----------------------------------------------------------------##
class AssetFolderTreeView( GenericTreeWidget ):
	def __init__( self, *args, **option ):
		option[ 'show_root' ] = True
		super( AssetFolderTreeView, self ).__init__( *args, **option )
		self.refreshingSelection = False
		self.setHeaderHidden( True )

	def saveTreeStates( self ):
		for node, item in self.nodeDict.items():
			node.setProperty( 'expanded', item.isExpanded() )

	def loadTreeStates( self ):
		for node, item in self.nodeDict.items():
			item.setExpanded( node.getProperty( 'expanded', False ) )
		self.getItemByNode( self.getRootNode() ).setExpanded( True )
		
	def getRootNode( self ):
		return app.getAssetLibrary().getRootNode()

	def getNodeParent( self, node ): # reimplemnt for target node
		return node.getParent()

	def getNodeChildren( self, node ):
		result = []
		for node in node.getChildren():
			if node.getProperty( 'hidden', False ): continue
			if not node.getGroupType() in ( 'folder', 'package' ) :continue
			result.append( node )
		return result

	def createItem( self, node ):
		return AssetFolderTreeItem()

	def updateItemContent( self, item, node, **option ):
		assetType = node.getType()
		item.setText( 0, node.getName() )
		iconName = app.getAssetLibrary().getAssetIcon( assetType )
		item.setIcon(0, getIcon(iconName,'normal'))

	def onClipboardCopy( self ):
		clip = QtGui.QApplication.clipboard()
		out = None
		for node in self.getSelection():
			if out:
				out += "\n"
			else:
				out = ""
			out += node.getNodePath()
		clip.setText( out )
		return True

	def getHeaderInfo( self ):
		return [ ('Name',120) ]

	def _updateItem(self, node, updateLog=None, **option):
		super( AssetFolderTreeView, self )._updateItem( node, updateLog, **option )

		if option.get('updateDependency',False):
			for dep in node.dependency:
				self._updateItem(dep, updateLog, **option)

	def onClicked(self, item, col):
		pass

	def onItemActivated(self, item, col):
		node=item.node
		self.parentModule.onActivateNode( node, 'tree' )

	def onItemSelectionChanged(self):
		self.parentModule.onTreeSelectionChanged()
		# if self.refreshingSelection: return
		# items = self.selectedItems()
		# if items:
		# 	selections = [item.node for item in items]
		# 	getAssetSelectionManager().changeSelection(selections)
		# else:
		# 	getAssetSelectionManager().changeSelection(None)

	def onDeletePressed( self ):
		self.parentModule.onTreeRequestDelete()
		

##----------------------------------------------------------------##

class AssetListItemDelegate( QtGui.QStyledItemDelegate ):
	pass
	# def initStyleOption(self, option, index):
	# 	# let the base class initStyleOption fill option with the default values
	# 	super( AssetListItemDelegate, self ).initStyleOption(option, index)
	# 	# override what you need to change in option
	# 	if option.state & QStyle.State_Selected:
	# 		# option.state &= ~ QStyle.State_Selected
	# 		option.backgroundBrush = QBrush(QColor(100, 200, 100, 200))
		
##----------------------------------------------------------------##
class AssetBrowserIconListWidget( GenericListWidget ):
	def __init__( self, *args, **option ):
		option[ 'mode' ] = 'icon'
		option[ 'drag_mode' ] = 'all'
		option[ 'multiple_selection' ] = True
		super( AssetBrowserIconListWidget, self ).__init__( *args, **option )
		self.setObjectName( 'AssetBrowserList' )
		self.setWrapping( True )
		self.setLayoutMode( QtGui.QListView.Batched )
		self.setResizeMode( QtGui.QListView.Adjust  )
		self.setHorizontalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.setVerticalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.setMovement( QtGui.QListView.Snap )
		self.setTextElideMode( Qt.ElideRight )
		
		self.thumbnailIconSize = ( 80, 80 )
		# self.setIconSize( QtCore.QSize( 32, 32 ) )
		self.setItemDelegate( AssetListItemDelegate( self ) )
		
		self.setIconSize( QtCore.QSize( 120, 130 ) )
		self.setGridSize( QtCore.QSize( 120, 130 ) )
		self.setWordWrap( True )


	def getItemFlags( self, node ):
		return {}

	def getDefaultOptions( self ):
		return None

	def getNodes( self ):
		return self.parentModule.getAssetsInList()

	def updateItemContent( self, item, node, **option ):
		rawName = node.getName()
		dotIdx = rawName.find( '.' )
		if dotIdx > 0:
			name = rawName[ 0:dotIdx ]
			ext  = rawName[ dotIdx: ]
			item.setText( name + '\n' + ext )
		else:
			item.setText( rawName )
		thumbnailIcon = self.parentModule.getAssetThumbnailIcon( node, self.thumbnailIconSize )
		if not thumbnailIcon:
			thumbnailIcon = getIcon( 'thumbnail/%s' % node.getType(), 'thumbnail/default' )

		item.setIcon( thumbnailIcon )
		item.setSizeHint( QtCore.QSize( 120, 130 ) )
		# item.setTextAlignment( Qt.AlignLeft | Qt.AlignVCenter )
		item.setTextAlignment( Qt.AlignCenter | Qt.AlignVCenter )
		item.setToolTip( node.getPath() )

	def onItemSelectionChanged(self):
		self.parentModule.onListSelectionChanged()

	def onItemActivated( self, item ):
		node = item.node
		self.parentModule.onActivateNode( node, 'list' )

	def mimeData( self, items):
		data = QtCore.QMimeData()
		output = []
		for item in items:
			asset = item.node
			output.append( asset.getPath() )
		assetListData = json.dumps( output ).encode('utf-8')
		data.setData( GII_MIME_ASSET_LIST, assetListData )
		return data

	def onDeletePressed( self ):
		self.parentModule.onListRequestDelete()

	def onClipboardCopy( self ):
		clip = QtGui.QApplication.clipboard()
		out = None
		for node in self.getSelection():
			if out:
				out += "\n"
			else:
				out = ""
			out += node.getNodePath()
		clip.setText( out )
		return True


##----------------------------------------------------------------##
class AssetBrowserDetailListWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',150), ('Type', 60), ( 'Desc', 50 ) ]

	def getRootNode( self ):
		return self.parentModule

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.parentModule: return None
		return self.parentModule

	def getNodeChildren( self, node ):
		if node == self.parentModule:
			return self.parentModule.getAssetsInList()
		else:
			return []

	def createItem( self, node ):
		return AssetFolderTreeItem()
		
	def updateItemContent( self, item, node, **option ):
		if node == self.parentModule: return 
		assetType = node.getType()
		item.setText( 0, node.getName() )
		iconName = app.getAssetLibrary().getAssetIcon( assetType )
		item.setIcon(0, getIcon(iconName,'normal'))
		item.setText( 1, assetType )

	def onItemSelectionChanged(self):
		self.parentModule.onListSelectionChanged()

	def onItemActivated( self, item ):
		node = item.node
		self.parentModule.onActivateNode( node, 'list' )

##----------------------------------------------------------------##
class AssetBrowserTagFilterWidget( QtGui.QFrame ):
	pass

##----------------------------------------------------------------##
class AssetBrowserStatusBar( QtGui.QWidget ):
	pass


##----------------------------------------------------------------##
class AssetBrowserNavigatorCrumbBar( QtGui.QWidget ):
	pass

##----------------------------------------------------------------##
class AssetBrowserNavigator( QtGui.QWidget ):
	def __init__( self, *args, **kwargs ):
		super( AssetBrowserNavigator, self ).__init__( *args, **kwargs )
		layout = QtGui.QHBoxLayout( self )
		layout.setSpacing( 1 )
		layout.setMargin( 0 )
		self.buttonForward  = QtGui.QToolButton()
		self.buttonBackward = QtGui.QToolButton()
		self.buttonForward.setIconSize( QSize( 16, 16 )  )
		self.buttonBackward.setIconSize( QSize( 16, 16 )  )
		self.buttonForward.setIcon( getIcon( 'history_forward' ) )
		self.buttonBackward.setIcon( getIcon( 'history_backward' ) )
		layout.addWidget( self.buttonBackward )
		layout.addWidget( self.buttonForward )
		self.buttonForward.clicked.connect( self.onHistoryForward )
		self.buttonBackward.clicked.connect( self.onHistoryBackward )

		self.crumbBar = AssetBrowserNavigatorCrumbBar()
		layout.addWidget( self.crumbBar )
		self.crumbBar.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
		self.setFixedHeight( 20 )

	def onHistoryForward( self ):
		self.parentModule.forwardHistory()

	def onHistoryBackward( self ):
		self.parentModule.backwardHistory()