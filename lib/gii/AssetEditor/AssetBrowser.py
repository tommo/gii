import random
import os

from gii.core         import *
from gii.qt.dialogs   import requestString, alertMessage, confirmDialog
from gii.qt.controls.AssetTreeView import AssetTreeView
from gii.qt.helpers   import setClipboardText
from gii.SearchView   import requestSearchView, registerSearchEnumerator

from AssetEditor      import AssetEditorModule, getAssetSelectionManager

from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

##----------------------------------------------------------------##
class AssetBrowser( AssetEditorModule ):
	name       = 'asset_browser'
	dependency = ['qt', 'asset_editor']

	def __init__(self):
		AssetEditorModule.__init__( self )
		self.newCreateNodePath = None

	def onLoad(self):
		self.container = self.requestDockWindow('AssetBrowser',
				title='Asset Browser',
				dock='left',
				minSize=(250,250)
			)
		
		self.treeView  = self.container.addWidget(
				AssetBrowserTreeView(
					sorting   = True,
					multiple_selection = True,
					drag_mode = 'internal'
				)
			)
		
		signals.connect( 'module.loaded',        self.onModuleLoaded )		
		signals.connect( 'asset.deploy.changed', self.onAssetDeployChanged )

		self.treeView.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.treeView.customContextMenuRequested.connect( self.onTreeViewContextMenu)

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
			'main/find/open_asset',   dict( label = 'Open Asset', shortcut = 'ctrl+shift+O' )
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
		self.getAssetLibrary().scheduleScanProject()
		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )
		signals.connect( 'asset.moved',      self.onAssetMoved )
		signals.connect( 'asset.modified',   self.onAssetModified )

		self.treeView.rebuild()

	def onStop( self ):
		self.treeView.saveTreeStates()

	def onSetFocus( self ):
		self.getMainWindow().raise_()
		self.treeView.setFocus()
		self.container.raise_()

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
		self.treeView.setFocus( Qt.MouseFocusReason)
		item = self.treeView.getItemByNode( asset )
		if item:
			self.treeView.clearSelection()
			item.setSelected( True )
			self.treeView.scrollToItem( item )


	def loadAssetCreator(self, creator):
		label     = creator.getLabel()
		assetType = creator.getAssetType()		

		def creatorFunc(value=None):
			contextNode = getAssetSelectionManager().getSingleSelection()
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
		contextNode = getAssetSelectionManager().getSingleSelection()
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
	
	def onTreeViewContextMenu( self, point ):
		item = self.treeView.itemAt(point)
		if item:			
			node=item.node
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

	def onAssetRegister(self, node):
		pnode = node.getParent()
		if pnode:
			self.treeView.addNode( node )
		if node.getPath() == self.newCreateNodePath:
			self.newCreateNodePath=None
			self.treeView.selectNode(node)

	def onAssetUnregister(self, node):
		pnode=node.getParent()
		if pnode:
			self.treeView.removeNode(node)

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
		name=menuNode.name
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
			if not getAssetSelectionManager().getSelection():
				return AssetUtils.showFileInBrowser( getProjectPath() )
				
			for n in getAssetSelectionManager().getSelection():
				if isinstance( n, AssetNode ):
					n.showInBrowser()
					break

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

	def onSelectionChanged( self, selection, context ):
		if context == 'asset':
			self.setFocus()
			self.treeView.refreshingSelection = True
			
			firstObj = None
			for obj in selection:
				firstObj = obj
				self.treeView.selectNode( obj, add = True )
			if firstObj: self.treeView.scrollToNode( firstObj )

			self.treeView.refreshingSelection = False

	def selectAsset( self, asset ):
		if asset: self.treeView.selectNode( asset )

	def openAsset( self, asset ):
		if asset:
			self.treeView.selectNode( asset )
			asset.edit()

##----------------------------------------------------------------##
class AssetBrowserTreeView( AssetTreeView ):
	def __init__( self, *args, **option ):
		super( AssetBrowserTreeView, self ).__init__( *args, **option )
		self.refreshingSelection = False

	def onClicked(self, item, col):
		pass

	def onItemActivated(self, item, col):
		node=item.node
		if node:
			node.edit()

	def onItemSelectionChanged(self):
		if self.refreshingSelection: return
		items = self.selectedItems()
		if items:
			selections = [item.node for item in items]
			getAssetSelectionManager().changeSelection(selections)
		else:
			getAssetSelectionManager().changeSelection(None)

	def onDeletePressed( self ):
		if confirmDialog( 'delete asset', 'Confirm to delete asset(s)?' ):
			for node in self.getSelection():
				if not node.isVirtual():
					path = node.getAbsFilePath()
					os.remove( path )

##----------------------------------------------------------------##
def assetCreatorSearchEnumerator( typeId, context ):
	if not context in [ 'asset_creator' ] : return None
	result = []
	for creator in AssetLibrary.get().assetCreators:
		entry = ( creator, creator.getLabel(), 'asset_creator', None )
		result.append( entry )
	return result



