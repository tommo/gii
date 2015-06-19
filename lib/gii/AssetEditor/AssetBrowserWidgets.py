import random
import json

from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

from gii.core         import *
from gii.qt           import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget, GenericTreeFilter
from gii.qt.controls.GenericListWidget import GenericListWidget
from gii.qt.controls.AssetTreeView import AssetTreeView, AssetTreeFilter

from AssetEditor      import AssetEditorModule, getAssetSelectionManager


##----------------------------------------------------------------##
class AssetBrowserTreeView( AssetTreeView ):
	def __init__( self, *args, **option ):
		option[ 'show_root' ] = True
		super( AssetBrowserTreeView, self ).__init__( *args, **option )
		self.refreshingSelection = False

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
		if requestConfirm( 'delete asset', 'Confirm to delete asset(s)?' ):
			for node in self.getSelection():
				if not node.isVirtual():
					path = node.getAbsFilePath()
					os.remove( path )

##----------------------------------------------------------------##
class AssetBrowserListWidget( GenericListWidget ):
	def __init__( self, *args, **option ):
		option[ 'mode' ] = 'icon'
		option[ 'drag_mode' ] = 'all'
		super( AssetBrowserListWidget, self ).__init__( *args, **option )
		self.setObjectName( 'AssetBrowserList' )
		self.setWrapping( True )
		self.setLayoutMode( QtGui.QListView.Batched )
		self.setResizeMode( QtGui.QListView.Adjust  )
		self.setHorizontalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.setVerticalScrollMode( QtGui.QAbstractItemView.ScrollPerPixel )
		self.setMovement( QtGui.QListView.Snap )
		
		self.thumbnailIconSize = ( 80, 80 )
		# self.setIconSize( QtCore.QSize( 32, 32 ) )
		
		self.setIconSize( QtCore.QSize( 120, 130 ) )
		self.setGridSize( QtCore.QSize( 120, 130 ) )
		self.setWordWrap( True )

	def getItemFlags( self, node ):
		return {}

	def getDefaultOptions( self ):
		return None

	def getNodes( self ):
		return self.parentModule.getAssetsInListView()

	def updateItemContent( self, item, node, **option ):
		item.setText( node.getName() )
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

##----------------------------------------------------------------##
class AssetBrowserTagFilterWidget( QtGui.QFrame ):
	pass


##----------------------------------------------------------------##
class AssetBrowserStatusBar( QtGui.QWidget ):
	pass
