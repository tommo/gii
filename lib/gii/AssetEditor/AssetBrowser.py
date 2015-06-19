import random
import os

from gii.core         import *
from gii.qt.dialogs   import requestString, alertMessage, requestConfirm
from gii.qt.helpers   import setClipboardText
from gii.SearchView   import requestSearchView, registerSearchEnumerator

from AssetEditor      import AssetEditorModule, getAssetSelectionManager
from gii.SceneEditor  import SceneEditorModule, getSceneSelectionManager

from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

from AssetBrowserWidgets import *


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


##----------------------------------------------------------------##
class AssetBrowser( SceneEditorModule ):
	name       = 'asset_browser'
	dependency = ['qt', 'asset_editor']

	def onLoad(self):

		self.newCreateNodePath = None
		self.currentContextTargetNode = None
		self.thumbnailSize = ( 80, 80 )
		self.updatingSelection = False

		self.window = self.requestDockWindow('AssetBrowser',
				title='Asset Browser',
				dock='left',
				minSize=(200,200)
			)

		ui = self.window.addWidgetFromFile(
			_getModulePath('AssetBrowser.ui')
		)

		#
		self.treeFilter = AssetTreeFilter(
				self.window
			)
		self.treeView  = 	AssetBrowserTreeView(
			sorting   = True,
			multiple_selection = True,
			drag_mode = 'internal',
			folder_only = True
		)
		
		self.treeView.parentModule = self
		self.treeView.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.treeView.customContextMenuRequested.connect( self.onTreeViewContextMenu)
		#

		treeLayout = QtGui.QVBoxLayout( ui.containerTree )
		treeLayout.setSpacing( 0 )
		treeLayout.setMargin( 0 )
		
		treeLayout.addWidget( self.treeFilter )
		treeLayout.addWidget( self.treeView )

		
		##
		self.listView  = AssetBrowserListWidget()
		self.tagFilter = AssetBrowserTagFilterWidget()
		self.statusBar = AssetBrowserStatusBar()

		self.listView .parentModule = self
		self.tagFilter.parentModule = self
		self.statusBar.parentModule = self

		self.listView.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.listView.customContextMenuRequested.connect( self.onListViewContextMenu )

		listLayout = QtGui.QVBoxLayout( ui.containerRight )
		listLayout.setSpacing( 0 )
		listLayout.setMargin( 0 )

		listLayout.addWidget( self.tagFilter )
		listLayout.addWidget( self.listView )
		listLayout.addWidget( self.statusBar )

		##
		self.currentFolders = []
		

		#
		signals.connect( 'module.loaded',        self.onModuleLoaded )		
		signals.connect( 'asset.deploy.changed', self.onAssetDeployChanged )

		self.creatorMenu=self.addMenu(
			'asset_create_context',
			{ 'label':'Create' }
		)
		self.addMenuItem(
			'main/asset/asset_create', dict( label = 'Create', shortcut ='Ctrl+N' )
		)
		self.addMenuItem(
			'main/find/find_asset',   dict( label = 'Find Asset', shortcut = 'ctrl+T' )
		)
		self.addMenuItem(
			'main/find/open_asset',   dict( label = 'Open Asset', shortcut = 'ctrl+O' )
		)

		self.assetContextMenu=self.addMenu('asset_context')
		self.assetContextMenu.addChild([
				{'name':'show_in_browser', 'label':'Show File'},
				{'name':'open_in_system', 'label':'Open In System'},
				{'name':'copy_node_path', 'label':'Copy Asset Path'},
				'----',
				{'name':'clone', 'label':'Clone'},
				'----',
				{'name':'reimport', 'label':'Reimport'},
				'----',
				{'name':'deploy_set', 'label':'Set Deploy'},
				{'name':'deploy_unset', 'label':'Unset Deploy'},
				{'name':'deploy_disallow', 'label':'Disallow Deploy'},
				'----',
				{'name':'create', 'label':'Create', 'link':self.creatorMenu},
			])

		signals.connect( 'selection.changed', self.onSelectionChanged )
		registerSearchEnumerator( assetCreatorSearchEnumerator  )

	def onStart( self ):
		assetLib = self.getAssetLibrary()
		assetLib.scheduleScanProject()
		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )
		signals.connect( 'asset.moved',      self.onAssetMoved )
		signals.connect( 'asset.modified',   self.onAssetModified )

		self.treeView.rebuild()

		initialSelection = self.getConfig( 'current_selection', None )
		if initialSelection:
			nodes = [ assetLib.getAssetNode( path ) for path in initialSelection ]
			self.treeView.selectNode( nodes )

	def onStop( self ):
		self.setConfig( 'current_selection', [ node.getPath() for node in self.currentFolders ] )
		self.treeView.saveTreeStates()

	def onSetFocus( self ):
		self.getMainWindow().raise_()
		self.treeView.setFocus()
		self.window.raise_()

	def onUnload(self):
		#persist expand state
		# self.treeView.saveTreeStates()

		pass

	def onModuleLoaded(self):				
		for creator in self.getAssetLibrary().assetCreators:
			self.loadAssetCreator(creator)

	def setAssetIcon(self, assetType, iconName):
		self.assetIconMap[assetType] = iconName

	def locateAsset( self, asset, **options ):
		if isinstance( asset, ( str, unicode ) ): #path
			asset = self.getAssetLibrary().getAssetNode( asset )
		if not asset: return
		self.listView.setFocus( Qt.MouseFocusReason)
		self.selectAsset( asset, goto = True )
		# item = self.treeView.getItemByNode( asset )
		# if item:
		# 	self.treeView.clearSelection()
		# 	item.setSelected( True )
		# 	self.treeView.scrollToItem( item )

	def loadAssetCreator(self, creator):
		label     = creator.getLabel()
		assetType = creator.getAssetType()		

		def creatorFunc(value=None):
			if self.currentFolders:
				contextNode = self.currentFolders[0]
			else:
				contextNode = None

			if not isinstance(contextNode, AssetNode):
				contextNode = app.getAssetLibrary().getRootNode()

			name = requestString('Create Asset <%s>' % assetType, 'Enter asset name: <%s>' % assetType )
			if not name: return

			try:
				finalpath = creator.createAsset(name, contextNode, assetType)
				self.newCreateNodePath=finalpath
			except Exception,e:
				logging.exception( e )
				alertMessage( 'Asset Creation Error', repr(e) )
				return
		#insert into toolbar box?
		#insert into create menu
		self.creatorMenu.addChild({
				'name'     : 'create_'+assetType,
				'label'    : label,
				'on_click' : creatorFunc
			})

	def createAsset( self, creator ):
		label       = creator.getLabel()
		assetType   = creator.getAssetType()		

		if self.currentFolders:
			contextNode = self.currentFolders[0]
		else:
			contextNode = None

		if not isinstance(contextNode, AssetNode):
			contextNode = app.getAssetLibrary().getRootNode()

		name = requestString('Create Asset <%s>' % assetType, 'Enter asset name: <%s>' % assetType )
		if not name: return

		try:
			finalpath=creator.createAsset(name, contextNode, assetType)
			self.newCreateNodePath=finalpath
		except Exception,e:
			logging.exception( e )
			alertMessage( 'Asset Creation Error', repr(e) )

	def popupAssetContextMenu( self, node ):
		if node:
			self.currentContextTargetNode = node
			deployState=node.deployState
			self.enableMenu( 'asset_context/open_in_system',  True )
			self.enableMenu( 'asset_context/copy_node_path',  True )
			self.enableMenu( 'asset_context/deploy_set',      deployState != True )
			self.enableMenu( 'asset_context/deploy_unset',    deployState != None )
			self.enableMenu( 'asset_context/deploy_disallow', deployState != False )
			self.findMenu('asset_context').popUp()
		else:
			self.enableMenu( 'asset_context/open_in_system', False )
			self.enableMenu( 'asset_context/copy_node_path', False )
			self.enableMenu( 'asset_context/deploy_set',     False )
			self.enableMenu( 'asset_context/deploy_unset',   False )
			self.enableMenu( 'asset_context/deploy_disallow',False )
			self.findMenu('asset_context').popUp()

	def onListViewContextMenu( self, point ):
		item = self.listView.itemAt(point)
		if item:
			node = item.node
		else:
			node = None
		self.popupAssetContextMenu( node )

	def onTreeViewContextMenu( self, point ):
		item = self.treeView.itemAt(point)
		if item:
			node = item.node
		else:
			node = None
		self.popupAssetContextMenu( node )

	def onAssetRegister(self, node):
		pnode = node.getParent()
		if node.isGroupType( 'folder', 'package' ):
			if pnode:
				self.treeView.addNode( node )

		if pnode in self.currentFolders:
			self.listView.rebuild()
			if node.getPath() == self.newCreateNodePath:
				self.newCreateNodePath=None
				self.listView.selectNode( node )

	def onAssetUnregister(self, node):
		pnode=node.getParent()
		if pnode:
			self.treeView.removeNode(node)
		if pnode in self.currentFolders:
			self.listView.removeNode( node )

	def onAssetMoved(self, node):
		pass

	def onAssetModified(self, node):
		self.treeView.refreshNodeContent( node )

	def onAssetDeployChanged(self, node):
		self.treeView.updateItem( node, 
				basic            = False,
				deploy           = True, 
				updateChildren   = True,
				updateDependency = True
			)
		app.getAssetLibrary().saveAssetTable()

	def onMenu(self, menuNode):
		name = menuNode.name
		if name in ('deploy_set', 'deploy_disallow', 'deploy_unset'):
			if name   == 'deploy_set':      newstate = True
			elif name == 'deploy_disallow': newstate = False
			elif name == 'deploy_unset':    newstate = None
			s = getAssetSelectionManager().getSelection()
			for n in s:
				if isinstance(n,AssetNode):
					n.setDeployState(newstate)
					
		elif name == 'reimport':
			s = getAssetSelectionManager().getSelection()
			for n in s:
				if isinstance( n, AssetNode ):
					n.markModified()
			app.getAssetLibrary().importModifiedAssets()

		elif name == 'clone':
			pass

		elif name == 'remove':
			pass

		elif name == 'show_in_browser':
			n = self.currentContextTargetNode
			if isinstance( n, AssetNode ):
				n.showInBrowser()

		elif name == 'open_in_system':
			for n in getAssetSelectionManager().getSelection():
				if isinstance( n, AssetNode ):
					n.openInSystem()
					break

		elif name == 'copy_node_path':
			text = ''
			for n in getAssetSelectionManager().getSelection():
				if text: text += '\n'
				text += n.getNodePath()
			setClipboardText( text )

		elif name == 'asset_create':
			requestSearchView( 
				info    = 'select asset type to create',
				context = 'asset_creator',
				type    = 'scene',
				on_selection = self.createAsset
			)

		elif name == 'find_asset':
			requestSearchView( 
				info    = 'search for asset',
				context = 'asset',
				on_test      = self.selectAsset,
				on_selection = self.selectAsset
				)

		elif name == 'open_asset':
			requestSearchView( 
				info    = 'open asset',
				context = 'asset',
				on_test      = self.selectAsset,
				on_selection = self.openAsset
				)

	def onTreeSelectionChanged( self ):
		folders = []
		for anode in self.treeView.getSelection():
			# assert anode.isType( 'folder' )
			folders.append( anode )
		self.currentFolders = folders
		self.listView.rebuild()

	def onTreeRequestDelete( self ):
		if requestConfirm( 'delete asset package/folder', 'Confirm to delete asset(s)?' ):
			for node in self.treeView.getSelection():
				node.deleteFile()

	def onListRequestDelete( self ):
		if requestConfirm( 'delete asset package/folder', 'Confirm to delete asset(s)?' ):
			for node in self.listView.getSelection():
				node.deleteFile()
				
	def onListSelectionChanged( self ):
		self.updatingSelection = True
		getAssetSelectionManager().changeSelection( self.listView.getSelection() )
		self.updatingSelection = False

	def onSelectionChanged( self, selection, context ):
		if context == 'asset':
			if self.updatingSelection: return
			#TODO
			self.setFocus()
			firstObj = None
			for obj in selection:
				firstObj = obj
				self.treeView.selectNode( obj, add = True )
			if firstObj: self.treeView.scrollToNode( firstObj )
			self.listView.rebuild()

	def onActivateNode( self, node, src ):
		if src == 'tree':
			if node.isVirtual():
				node = node.findNonVirtualParent()
			if node.isType( 'folder' ):
				node.openInSystem()
			else:
				node.edit()

		else:
			if node.isGroupType( 'folder', 'package' ):
				self.selectAsset( node )
			else:
				self.openAsset( node )

	def selectAsset( self, asset, **options ):
		if not asset: return
		#find parent package/folder
		folder = asset
		while folder:
			if folder.getGroupType() in [ 'folder', 'package' ]: break
			folder = folder.getParent()
		self.treeView.selectNode( folder )
		self.listView.selectNode( asset )
		if options.get( 'goto', False ):
			self.treeView.scrollToNode( folder )
			self.listView.scrollToNode( asset )

	def openAsset( self, asset, **option ):
		if asset:
			if option.get('select', False):
				self.treeView.selectNode( asset )
			asset.edit()

	def getCurrentFolders( self ):
		return self.currentFolders

	def getAssetsInListView( self ):
		assets = []
		for folder in self.currentFolders:
			for subNode in folder.getChildren():
				assets.append( subNode )

		def _sortFunc( x, y ):
			t1 = x.getType()
			t2 = y.getType()
			if t1 == 'folder' and t2 != 'folder': return -1
			if t2 == 'folder' and t1 != 'folder': return 1
			return cmp( x.getName(), y.getName() )

		return sorted( assets, _sortFunc )

	def getAssetThumbnailIcon( self, assetNode, size ):
		thumbnailPath = assetNode.requestThumbnail( size )
		if thumbnailPath:
			icon = QtGui.QIcon( QtGui.QPixmap( thumbnailPath ) )
			return icon
		else:
			return None

##----------------------------------------------------------------##
def assetCreatorSearchEnumerator( typeId, context ):
	if not context in [ 'asset_creator' ] : return None
	result = []
	for creator in AssetLibrary.get().assetCreators:
		entry = ( creator, creator.getLabel(), 'asset_creator', None )
		result.append( entry )
	return result

