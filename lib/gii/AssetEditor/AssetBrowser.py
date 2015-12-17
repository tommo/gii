import random
import os

from gii.core         import *
from gii.qt.dialogs   import requestString, alertMessage, requestConfirm
from gii.qt.helpers   import setClipboardText
from gii.SearchView   import requestSearchView, registerSearchEnumerator

from AssetEditor      import AssetEditorModule, getAssetSelectionManager
from gii.SceneEditor  import SceneEditorModule

from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

from AssetBrowserWidgets import *

from util import TagMatch
from gii.qt.helpers import repolishWidget

from AssetFilter import *

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


##----------------------------------------------------------------##
class AssetBrowser( SceneEditorModule ):
	name       = 'asset_browser'
	dependency = ['qt', 'asset_editor']

	def onLoad( self ):
		self.instances = {}

		self.assetFilterViewModes = {}
		self.assetFilterRootGroup = AssetFilterGroup()
		self.assetFilterRootGroup.setName( '__root__' )

		#create menu
		signals.connect( 'module.loaded',        self.onModuleLoaded )		

		self.creatorMenu = self.addMenu(
			'asset_create_context',
			{ 'label':'Create' }
		)

		self.findMenu( 'main/asset' ).addChild([
			'----',
			dict( name = 'open_asset', label = 'Open Asset', shortcut = 'ctrl+O' ),
			dict( name = 'create_asset', label = 'Create', shortcut ='Ctrl+N' ),
			dict( name = 'create_folder', label = 'Create Folder', shortcut ='Ctrl+Shift+N' ),
			'----',
			dict( name = 'new_asset_search', label = 'New Asset Search' ),
		], self )

		self.findMenu( 'main/find' ).addChild([
			dict( name = 'find_asset', label = 'Find Asset', shortcut = 'ctrl+T' ),
			dict( name = 'find_asset_folder', label = 'Find Folder', shortcut = 'ctrl+shift+T' ),
		], self )
		

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
			])

		#
		self.browserInstance = self.createInstance( 'main' )
		self.loadConfig()

	def onStart( self ):
		for instance in self.instances.values():
			instance.onStart()

	def onStop( self ):
		self.saveConfig()

	def loadConfig( self ):
		#load filter
		filterData = self.getConfig( 'filters', None )
		if filterData:
			self.assetFilterRootGroup.load( filterData )
		self.assetFilterViewModes = self.getConfig( 'filter_view_modes', {} )

		#load instances
		instanceConfigs = self.getConfig( 'instances', {} )
		for key, config in instanceConfigs.items():
			mode = config.get( 'mode', 'search' )
			instance = self.requestInstance( key, mode = mode )
			instance.loadConfig( config )


	def saveFilterConfig( self ):
		filterData = self.assetFilterRootGroup.save()
		self.setConfig( 'filters', filterData )
		self.setConfig( 'filter_view_modes', self.assetFilterViewModes )

	def saveConfig( self ):
		#save filter
		self.saveFilterConfig()

		#save instances
		instanceConfigs = {}
		for key, instance in self.instances.items():
			config = instance.saveConfig()
			instanceConfigs[ key ] = config
		self.setConfig( 'instances', instanceConfigs )

		for instance in self.instances.values():
			instance.onStop()

	def onSetFocus( self ):
		self.getMainWindow().raise_()
		self.browserInstance.setFocus()

	def onUnload( self ):
		#persist expand state
		# self.treeFolder.saveTreeStates()
		pass

	def onModuleLoaded( self ):				
		for creator in self.getAssetLibrary().assetCreators:
			self.loadAssetCreator(creator)

	def loadAssetCreator( self, creator ):
		label     = creator.getLabel()
		assetType = creator.getAssetType()		

		def creatorFunc( value = None ):
			self.createAsset( creator )

		#insert into create menu
		self.creatorMenu.addChild({
				'name'     : 'create_'+assetType,
				'label'    : label,
				'on_click' : creatorFunc
			})

	#
	def requestInstance( self, key, **options ):
		if key == 'main':
			options[ 'main' ] = True
		
		instance = self.getInstance( key )
		if instance: return instance

		instance = AssetBrowserInstance( key, **options )
		instance.module = self
		self.instances[ key ] = instance
		instance.onLoad()
		return instance

	def getInstance( self, key ):
		return self.instances.get( key, None )

	def createInstance( self, key = None, **options ):
		if not key:
			key = generateGUID()
		if self.getInstance( key ):
			raise Exception( 'duplicated instance key: %s' % str(key) )

		return self.requestInstance( key, **options )

	def removeInstance( self, instance ):
		key = instance.instanceId
		assert key != 'main'
		instance.onStop()
		del self.instances[ key ]

	#asset operation
	def locateAsset( self, asset, **options ):
		if isinstance( asset, ( str, unicode ) ): #path
			asset = self.getAssetLibrary().getAssetNode( asset )
		if not asset: return
		self.browserInstance.locateAsset( asset, **options )

	def selectAsset( self, asset, **options ):
		if not asset: return
		self.browserInstance.selectAsset( asset, **options )
		
	def openAsset( self, asset, **option ):
		if asset:
			if option.get('select', True ):
				self.selectAsset( asset )
			asset.edit()

	def createAsset( self, creator, instance = None ):
		if isinstance( creator, str ):
			creator = self.getAssetLibrary().getAssetCreator( creator )

		label       = creator.getLabel()
		assetType   = creator.getAssetType()		

		instance = instance or self.browserInstance
		if instance.currentFolders:
			contextNode = instance.currentFolders[0]
		else:
			contextNode = None

		if not isinstance( contextNode, AssetNode ):
			contextNode = app.getAssetLibrary().getRootNode()

		name = requestString('Create Asset <%s>' % assetType, 'Enter asset name: <%s>' % assetType )
		if not name: return

		try:
			finalPath = creator.createAsset( name, contextNode, assetType )
			self.newCreateNodePath=finalPath
		except Exception,e:
			logging.exception( e )
			alertMessage( 'Asset Creation Error', repr(e) )

	#search
	def createAssetSearch( self, **options ):
		instance = self.createInstance( mode = 'search' )
		instance.onStart()

	def getFilterRootGroup( self ):
		return self.assetFilterRootGroup

	def setFilterViewMode( self, assetFilter, mode ):
		if assetFilter.getRoot() == self.getFilterRootGroup():
			self.assetFilterViewModes[ assetFilter.getId() ] = mode
	#menu
	def popupAssetContextMenu( self, node ):
		if node:
			self.currentContextTargetNode = node
			deployState = node.deployState
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
			targetNode = self.currentContextTargetNode
			if targetNode:
				targets = [ targetNode ]	
			else:
				targets = getAssetSelectionManager().getSelection()
			for targetNode in targets:
				if isinstance( targetNode, AssetNode ):
					targetNode.markModified()
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

		elif name == 'create_asset':
			requestSearchView( 
				info    = 'select asset type to create',
				context = 'asset_creator',
				type    = 'scene',
				on_selection = self.createAsset
			)

		elif name == 'create_folder':
			self.createAsset( 'folder' )

		elif name == 'find_asset':
			requestSearchView( 
				info    = 'search for asset',
				context = 'asset',
				on_test      = self.selectAsset,
				on_selection = self.selectAsset
				)

		elif name == 'find_asset_folder':
			requestSearchView( 
				info    = 'search for asset',
				context = 'asset_folder',
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

		elif name == 'new_asset_search':
			self.createAssetSearch()
	

##----------------------------------------------------------------##
class AssetBrowserInstance( object ):
	def __init__( self, instanceId, **kwargs ):
		super(AssetBrowserInstance, self).__init__()
		self.module = None
		self.main = kwargs.get( 'main', False )
		self.instanceId = instanceId
		self.windowId = 'AssetBrowser-%s' % self.instanceId
		self.mode = ( self.main and 'browse' ) or kwargs.get( 'mode', 'search' )
		self.windowTitle = ''
		
		self.assetFilter = AssetFilter()
		self.filtering = False
		self.initialSelection = None

	def setTitle( self, title ):
		self.windowTitle = title
		prefix = self.mode == 'search' and 'Asset Search' or 'Assets'
		if title:
			self.window.setWindowTitle( '%s< %s >' % ( prefix, title ) )
		else:
			self.window.setWindowTitle( '%s' % prefix )

	def isMain( self ):
		return self.main

	def isSearch( self ):
		return self.mode == 'search'

	def onLoad( self ):
		self.viewMode = 'icon'

		self.currentFolders = []

		self.browseHistory = []
		self.historyCursor = 0
		self.updatingHistory = False
		self.updatingSelection = False
		self.newCreateNodePath = None

		self.thumbnailSize = ( 80, 80 )
		self.windowId = 'AssetBrowser-%d'
		dock = 'bottom'
		if self.isSearch():
			dock = 'float'

		self.window = self.module.requestDockWindow(
				'AssetBrowser',
				title   = 'Assets',
				dock    = dock,
				minSize = (200,200)
			)
		self.window.setCallbackOnClose( self.onClose )
		self.window.hide()
		ui = self.window.addWidgetFromFile(
			_getModulePath('AssetBrowser.ui')
		)

		self.splitter = ui.splitter
		
		#Tree folder
		self.treeFolderFilter = AssetFolderTreeFilter(
				self.window
			)
		self.treeFolder  = 	AssetFolderTreeView(
			sorting   = True,
			multiple_selection = True,
			drag_mode = 'internal',
			folder_only = True
		)

		self.treeFolderFilter.setTargetTree( self.treeFolder )
		self.treeFolder.owner = self
		self.treeFolder.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.treeFolder.customContextMenuRequested.connect( self.onTreeViewContextMenu)

		#Tree filter
		self.treeFilterFilter = AssetFolderTreeFilter(
				self.window
			)
		self.treeFilter  = 	AssetFilterTreeView(
			sorting   = True,
			multiple_selection = False
			# drag_mode = 'internal',
		)
		
		self.treeFilterFilter.setTargetTree( self.treeFilter )
		self.treeFilter.owner = self

		##
		self.iconList       = AssetBrowserIconListWidget()
		self.detailList     = AssetBrowserDetailListWidget()
		self.assetFilterWidget  = AssetBrowserTagFilterWidget()
		self.statusBar      = AssetBrowserStatusBar()
		self.navigator      = AssetBrowserNavigator()

		folderToolbar  = QtGui.QToolBar()
		contentToolbar = QtGui.QToolBar()

		self.detailList .owner = self
		self.iconList   .owner = self
		self.assetFilterWidget.owner = self
		self.statusBar  .owner = self
		self.navigator  .owner = self

		self.iconList.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.iconList.customContextMenuRequested.connect( self.onItemContextMenu )
		self.detailList.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.detailList.customContextMenuRequested.connect( self.onItemContextMenu )


		layoutLeft = QtGui.QVBoxLayout( ui.containerTree )
		layoutLeft.setSpacing( 0 )
		layoutLeft.setMargin( 0 )
		
		layoutLeft.addWidget( folderToolbar )
		layoutLeft.addWidget( self.treeFolderFilter )
		layoutLeft.addWidget( self.treeFolder )

		layoutLeft.addWidget( self.treeFilterFilter )
		layoutLeft.addWidget( self.treeFilter )
		
		layoutRight = QtGui.QVBoxLayout( ui.containerRight )
		layoutRight.setSpacing( 0 )
		layoutRight.setMargin( 0 )

		layoutRight.addWidget( contentToolbar )
		layoutRight.addWidget( self.assetFilterWidget )
		layoutRight.addWidget( self.iconList )
		layoutRight.addWidget( self.detailList )
		layoutRight.addWidget( self.statusBar )

		##Tool bar
		self.folderToolBar  = self.module.addToolBar( None, folderToolbar, owner = self )
		self.contentToolBar = self.module.addToolBar( None, contentToolbar, owner = self )

		self.contentToolBar.addTools([
			dict( name = 'detail_view', label = 'List View', type = 'check', icon = 'list',   group='view_mode' ),
			dict( name = 'icon_view',   label = 'Icon View', type = 'check', icon = 'grid-2', group='view_mode' ),
		])
		self.setViewMode( 'icon' )
		if self.isSearch():
			#search mode
			self.treeFolder.hide()
			self.treeFolderFilter.hide()

			self.folderToolBar.addTools([
				dict( name = 'create_filter', label = 'Add Filter', icon = 'add' ),
				dict( name = 'create_filter_group', label = 'Add Filter Group', icon = 'add_folder' ),
			])

			self.contentToolBar.addTools([
				'----',
				dict( name = 'locate_asset', label = 'Locate Asset', icon = 'search-2' ),
			])

		else:
			#browse mode
			self.treeFilter.hide()
			self.treeFilterFilter.hide()

			self.folderToolBar.addTools([
				dict( name = 'navigator', widget = self.navigator ),
			])
			self.contentToolBar.addTools([
				'----',
				dict( name = 'create_folder', label = 'Create Folder', icon = 'add_folder' ),
				dict( name = 'create_asset', label = 'Create Asset', icon = 'add' ),
			])

		self.setTitle( '' )
		self.setAssetFilter( None )
		

	def onStart( self ):
		assetLib = self.module.getAssetLibrary()

		self.treeFolder.rebuild()
		self.treeFilter.rebuild()

		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )
		signals.connect( 'asset.moved',      self.onAssetMoved )
		signals.connect( 'asset.modified',   self.onAssetModified )
		signals.connect( 'asset.deploy.changed', self.onAssetDeployChanged )
		signals.connect( 'selection.changed',    self.onSelectionChanged )


		if self.isSearch():
			#search mode
			self.treeFolder.hide()
			self.treeFolderFilter.hide()
			self.treeFilter.selectNode( self.assetFilter )

		else:
			#browse mode
			self.treeFilter.hide()
			self.treeFilterFilter.hide()
			if self.initialSelection:
				nodes = [ assetLib.getAssetNode( path ) for path in self.initialSelection ]
				self.treeFolder.selectNode( nodes )

		self.window.show()
		self.assetFilterWidget.rebuild()

	def onStop( self ):
		if self.isMain():
			self.treeFolder.saveTreeStates()

	def saveConfig( self ):
		sizes = self.splitter.sizes()
		if self.assetFilter.getRoot() == self.getFilterRootGroup():
			filterData = self.assetFilter.getId()
		else:
			filterData = self.assetFilter.save()
		config = {
			'mode' : self.mode,
			'current_selection' : [ node.getPath() for node in self.currentFolders ],
			'splitter_sizes'    : sizes,
			'current_filter'    : filterData
		}
		return config

	def loadConfig( self, config ):
		assetLib = self.module.getAssetLibrary()
		if not self.isSearch():
			self.initialSelection = config.get( 'current_selection', None )

		splitterSizes    = config.get( 'splitter_sizes', None )
		if splitterSizes:
			self.splitter.setSizes( splitterSizes )

		filterData = config.get( 'current_filter', None )
		if filterData:
			if isinstance( filterData, (str, unicode) ): #ref
				node = self.getFilterRootGroup().findChild( filterData )
				self.assetFilter = node
			else:
				self.assetFilter.load( filterData )

	#View control
	def setViewMode( self, mode, changeToolState = True, rebuildView = True ):
		prevSelection = self.getItemSelection()
		self.viewMode = mode
		if mode == 'icon':
			self.iconList.show()
			self.detailList.hide()
			if changeToolState: self.contentToolBar.getTool( 'icon_view' ).setValue( True )
			if rebuildView:
				self.rebuildItemView( True )
		else: #if mode == 'detail'
			self.iconList.hide()
			self.detailList.show()
			if changeToolState: self.contentToolBar.getTool( 'detail_view' ).setValue( True )
			if rebuildView:
				self.rebuildItemView( True )

		if prevSelection:
			for node in prevSelection:
				self.getCurrentView().selectNode( node, add = True, goto = False )
			self.getCurrentView().gotoNode( prevSelection[0] )

		if self.isSearch():
			self.module.setFilterViewMode( self.assetFilter, self.viewMode )

		else:
			for folder in self.getCurrentFolders():
				folder.setMetaData( 'browser_view_mode', self.viewMode, save = True )
				break

	def getCurrentView( self ):
		if self.viewMode == 'icon':
			return self.iconList
		else: #if mode == 'detail'
			return self.detailList

	def setFocus( self ):
		self.window.raise_()
		self.getCurrentView().setFocus()

	#
	def onItemContextMenu( self, point ):
		item = self.getCurrentView().itemAt(point)
		if item:
			node = item.node
		else:
			node = None
		self.module.popupAssetContextMenu( node )

	def onTreeViewContextMenu( self, point ):
		item = self.treeFolder.itemAt(point)
		if item:
			node = item.node
		else:
			node = None
		self.module.popupAssetContextMenu( node )

	def removeItemFromView( self, node ):
		self.getCurrentView().removeNode( node )

	def getItemSelection( self ):
		return self.getCurrentView().getSelection()

	def getFolderSelection( self ):
		return self.treeFolder.getSelection()

	def rebuildItemView( self, retainSelection = False ):
		if self.viewMode == 'icon':
			self.iconList.rebuild()
		else: #if mode == 'detail'
			self.detailList.rebuild()

	def onTreeSelectionChanged( self ):
		folders = []
		for anode in self.getFolderSelection():
			# assert anode.isType( 'folder' )
			folders.append( anode )
		self.pushHistory()
		self.currentFolders = folders
		if folders:
			folderNode = folders[0]
			viewMode = folderNode.getMetaData( 'browser_view_mode', 'icon' )
			self.setViewMode( viewMode, True, False )
		self.rebuildItemView()
		self.updateStatusBar()

	def onTreeRequestDelete( self ):
		if requestConfirm( 'delete asset package/folder', 'Confirm to delete asset(s)?' ):
			for node in self.getFolderSelection():
				node.deleteFile()

	def onListRequestDelete( self ):
		if requestConfirm( 'delete asset package/folder', 'Confirm to delete asset(s)?' ):
			for node in self.getItemSelection():
				node.deleteFile()
			
	def onListSelectionChanged( self ):
		self.updatingSelection = True
		selection = self.getItemSelection()
		if self.isMain():
			getAssetSelectionManager().changeSelection( selection )
		self.updatingSelection = False

	def onSelectionChanged( self, selection, context ):
		#global selection
		if not self.isMain(): return
		if context == 'asset':
			if not self.updatingSelection:
				#TODO
				self.setFocus()
				firstSelection = None
				for obj in selection:
					firstSelection = obj
					self.treeFolder.selectNode( obj, add = True )
				if firstSelection: self.treeFolder.scrollToNode( firstSelection )
				self.rebuildItemView()
			
			self.updateStatusBar()

	def onActivateNode( self, node, src ):
		if src == 'tree' or self.isSearch(): #direct open
			if node.isVirtual():
				node = node.findNonVirtualParent()
				self.openAsset( node, select = False )
			if node.isType( 'folder' ):
				node.openInSystem()
			else:
				self.openAsset( node, select = False )

		else:
			if node.isGroupType( 'folder', 'package' ):
				self.selectAsset( node, enter_folder = True )
			else:
				self.openAsset( node, select = False )

	#status bar/ tags
	def editAssetTags( self ):
		target = None
		itemSelection = self.getItemSelection()
		if itemSelection:
			target = itemSelection[0]
		else:
			folders = self.getCurrentFolders()
			if folders:
				target = folders[0]
		if not target: return
		text = requestString( 
			'Tags', 
			'Enter Tags:',
			target.getTagString()
		)
		if text != None:
			target.setTagString( text )
			self.updateStatusBar()

	def updateStatusBarForAsset( self, asset, forFolder = False ):
		if forFolder:
			self.statusBar.setText( '[' + asset.getNodePath() + ']' )
		else:
			self.statusBar.setText( asset.getNodePath() )
		self.statusBar.setTags( asset.getTagString() )

	def updateStatusBar( self ):
		self.statusBar.show()
		selection = self.getItemSelection()
		count = len( selection )
		if count == 1:
			node = selection[0]
			self.updateStatusBarForAsset( node )
			return
		elif count > 1:
			self.statusBar.setText( '%d asset selected' % count )
			return
		else:
			folders = self.getCurrentFolders()
			countFolder = len( folders )
			if countFolder == 1:
				folder = folders[0]
				self.updateStatusBarForAsset( folder, True )
				return
			elif countFolder > 1:
				self.statusBar.setText( '%d folders/packages selected' % countFolder )
				return
		self.statusBar.setText( 'no selection' )
		self.statusBar.hide()
	
	#browsing support
	def pushHistory( self ):
		if self.updatingHistory: return
		currentSelection = self.getFolderSelection()
		if not currentSelection: return
		count = self.historyCursor
		if count > 0 and currentSelection == self.browseHistory[ count - 1 ]: return
		self.browseHistory = self.browseHistory[ 0: count ]
		self.browseHistory.append( currentSelection )
		self.historyCursor = count + 1

	def clearHistory( self ):
		self.browseHistory = []
		self.historyCursor = 0

	def forwardHistory( self ):
		count = len( self.browseHistory )
		if self.historyCursor >= count: return
		self.updatingHistory = True
		self.historyCursor = min( self.historyCursor + 1, count )
		selection = self.browseHistory[ self.historyCursor - 1 ]
		for asset in selection:
			self.selectAsset( asset, update_history = False, enter_folder = True )
		self.updatingHistory = False

	def backwardHistory( self ):
		if self.historyCursor <= 1: return #no more history
		self.historyCursor = max( self.historyCursor - 1, 0 )
		self.updatingHistory = True
		selection = self.browseHistory[ self.historyCursor - 1 ]
		for asset in selection:
			self.selectAsset( asset, update_history = False, goto = True, enter_folder = True )
		self.updatingHistory = False

	def goUpperLevel( self ):
		for folder in self.currentFolders:
			self.selectAsset( folder, goto = True )
			return

	#commands
	def locateAsset( self, asset, **options ):
		if isinstance( asset, ( str, unicode ) ): #path
			asset = self.getAssetLibrary().getAssetNode( asset )
		if not asset: return
		self.getCurrentView().setFocus( Qt.MouseFocusReason)
		self.selectAsset( asset, goto = True )

	def selectAsset( self, asset, **options ):
		if not asset: return
		#find parent package/folder
		if options.get( 'enter_folder', False ):
			folder = asset
		else:
			folder = asset.getParent()
		while folder:
			if folder.getGroupType() in [ 'folder', 'package' ]: break
			folder = folder.getParent()
		itemView = self.getCurrentView()
		self.treeFolder.selectNode( folder )
		if options.get( 'update_history', True ):
			self.pushHistory()

		itemView.selectNode( asset )
		if options.get( 'goto', False ):
			self.setFocus()
			self.treeFolder.scrollToNode( folder )
			itemView.scrollToNode( asset )

	def openAsset( self, asset, **option ):
		return self.module.openAsset( asset, **option )

	def getCurrentFolders( self ):
		return self.currentFolders

	def getAssetsInList( self ):
		assetFilter = self.assetFilter
		assetFilter.updateRule()
		if self.isSearch(): #search for all assets:
			assetLib = self.module.getAssetLibrary()
			assets = []
			if not assetFilter.hasItem():
				pass
			else:
				for assetNode in assetLib.getAllAssets():
					if assetFilter.evaluate( assetNode ):
						assets.append( assetNode )

		else: #filter current folder
			assets = []
			filtering = assetFilter.compiledRule
			for folder in self.currentFolders:
				for assetNode in folder.getChildren():
					if filtering and ( not assetFilter.evaluate( assetNode ) ): continue
					assets.append( assetNode )

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

	def onAssetRegister( self, node ):
		pnode = node.getParent()
		if node.isGroupType( 'folder', 'package' ):
			if pnode:
				self.treeFolder.addNode( node )

		if pnode in self.currentFolders:
			self.rebuildItemView()
			if node.getPath() == self.newCreateNodePath:
				self.newCreateNodePath=None
				self.selectAsset( node )

	def onAssetUnregister( self, node ):
		pnode=node.getParent()
		if pnode:
			self.treeFolder.removeNode(node)
		if pnode in self.currentFolders:
			self.removeItemFromView( node )

	def onAssetMoved( self, node ):
		pass

	def onAssetModified( self, node ):
		self.treeFolder.refreshNodeContent( node )

	def onAssetDeployChanged( self, node ):
		self.treeFolder.updateItem( node, 
				basic            = False,
				deploy           = True, 
				updateChildren   = True,
				updateDependency = True
			)
		app.getAssetLibrary().saveAssetTable()
	
	def updateTagFilter( self ):
		prevFiltering = self.filtering
		self.assetFilter.updateRule()
		self.filtering = self.assetFilter.isFiltering()
		if self.filtering != prevFiltering:
			self.getCurrentView().setProperty( 'filtered', self.filtering )
			repolishWidget( self.getCurrentView() )
		self.rebuildItemView()

	def createAsset( self, creator ):
		self.module.createAsset( creator, self )

	#tool
	def onTool( self, tool ):
		name = tool.name
		if name == 'icon_view':
			self.setViewMode( 'icon', False )
		elif name == 'detail_view':
			self.setViewMode( 'detail', False )

		#content toolbar
		elif name == 'create_asset':
			requestSearchView( 
				info    = 'select asset type to create',
				context = 'asset_creator',
				type    = 'scene',
				on_selection = self.createAsset
			)

		elif name == 'create_folder':
			self.createAsset( 'folder' )

		elif name == 'locate_asset':
			for node in self.getItemSelection():
				self.module.locateAsset( node, goto = True )
				break

		elif name in ( 'create_filter', 'create_filter_group' ):
			node = self.treeFilter.getFirstSelection()
			if not node:
				contextGroup = self.getFilterRootGroup()
			elif isinstance( node, AssetFilterGroup ):
				contextGroup = node
			else:
				contextGroup = node.getParent()
			if name == 'create_filter':
				node = AssetFilter()
				node.setName ( 'filter' )
			else:
				node = AssetFilterGroup()
				node.setName ( 'group' )

			contextGroup.addChild( node )

			self.treeFilter.addNode( node )
			self.treeFilter.editNode( node )
			self.treeFilter.selectNode( node )

	def onClose( self ):
		if not self.isMain():
			self.module.removeInstance( self )
		return True

	#asset fitler
	def getFilterRootGroup( self ):
		return self.module.getFilterRootGroup()

	def	setAssetFilter( self, f ):
		if isinstance( f, AssetFilterGroup ):
			return

		elif isinstance( f, AssetFilter ):
			self.assetFilter = f
			self.assetFilterWidget.setTargetFilter( self.assetFilter )
			self.module.saveFilterConfig()
			viewMode = self.module.assetFilterViewModes.get( self.assetFilter.getId(), 'icon' )
			self.setViewMode( viewMode )

		else:
			self.assetFilter = AssetFilter()
			self.assetFilterWidget.setTargetFilter( self.assetFilter )

	def renameFilter( self, node, name ):
		node.setName( name )
		self.module.saveFilterConfig()

	def onAsseotFilterRequestDelete( self, node ):
		if requestConfirm( 'Confirm Deletion', 'Delete this filter (group)?' ):
			node.remove()
		self.module.saveFilterConfig()
		self.assetFilterWidget.rebuild()