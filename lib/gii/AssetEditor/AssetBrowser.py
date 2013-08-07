import random
from abc import ABCMeta, abstractmethod

from gii.core         import *
from gii.qt.dialogs   import requestString, alertMessage
from gii.qt.controls.AssetTreeView import AssetTreeView
from gii.qt.helpers   import setClipboardText

from AssetEditor      import AssetEditorModule

from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

##----------------------------------------------------------------##
class AssetBrowser( AssetEditorModule ):
	"""docstring for AssetBrowser"""
	def __init__(self):
		super(AssetBrowser, self).__init__()
		self.newCreateNodePath = None

	def getName(self):
		return 'asset_browser'

	def getDependency(self):
		return ['qt']

	def onLoad(self):
		self.container = self.requestDockWindow('AssetBrowser',
				title='Asset Browser',
				dock='left',
				minSize=(250,250)
			)

		self.searchBox = self.container.addWidgetFromFile(
				self.getApp().getPath( 'data/ui/search.ui' ),
				expanding = False
			)
		self.treeView  = self.container.addWidget(AssetBrowserTreeView())


		signals.connect( 'module.loaded',        self.onModuleLoaded )		
		signals.connect( 'asset.deploy.changed', self.onAssetDeployChanged )
		# signals.connect( 'selection.changed',    self.onSelectionChanged)

		self.treeView.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.treeView.customContextMenuRequested.connect( self.onTreeViewContextMenu)

		self.creatorMenu=self.addMenu(
			'main/asset/asset_create',
			{ 'label':'Create' }
			)

		self.assetContextMenu=self.addMenu('asset_context')
		self.assetContextMenu.addChild([
				{'name':'show_in_browser', 'label':'Show File'},
				{'name':'open_in_system', 'label':'Open In System'},
				{'name':'copy_node_path', 'label':'Copy Asset Path'},
				'----',
				{'name':'reimport', 'label':'Reimport'},
				'----',
				{'name':'deploy_set', 'label':'Set Deploy'},
				{'name':'deploy_unset', 'label':'Unset Deploy'},
				{'name':'deploy_disallow', 'label':'Disallow Deploy'},
				'----',
				{'name':'create', 'label':'Create', 'link':self.creatorMenu},
			])


	def onStart( self ):
		self.getAssetLibrary().scheduleScanProject()
		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )
		signals.connect( 'asset.moved',      self.onAssetMoved )

		self.treeView.rebuild()

	def onStop( self ):
		self.treeView.saveTreeStates()


	def onUnload(self):
		#persist expand state
		# self.treeView.saveTreeStates()
		pass

	def onModuleLoaded(self):				
		for creator in self.getAssetLibrary().assetCreators:
			self.loadAssetCreator(creator)

	def setAssetIcon(self, assetType, iconName):
		self.assetIconMap[assetType] = iconName

	def locateAsset( self, assetNode ):
		item = self.treeView.getItemByNode( assetNode )
		if item:
			self.treeView.clearSelection()
			item.setSelected( True )
			self.treeView.scrollToItem( item )

	def loadAssetCreator(self, creator):
		label     = creator.getLabel()
		assetType = creator.getAssetType()		

		def creatorFunc(value=None):
			contextNode = app.getSelectionManager().getSingleSelection()
			if not isinstance(contextNode, AssetNode):
				contextNode = app.getAssetLibrary().getRootNode()

			name = requestString('Create Asset <%s>' % assetType, 'Enter asset name' )
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

	def onTreeViewContextMenu(self, point):
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
		pass

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
			s = app.getSelectionManager().getSelection()
			for n in s:
				if isinstance(n,AssetNode):
					n.setDeployState(newstate)
					
		if name == 'reimport':
			s = app.getSelectionManager().getSelection()
			for n in s:
				if isinstance( n, AssetNode ):
					n.markModified()
			app.getAssetLibrary().importModifiedAssets()

		if name == 'show_in_browser':
			if not app.getSelectionManager().getSelection():
				return AssetUtils.showFileInBrowser( getProjectPath() )
				
			for n in app.getSelectionManager().getSelection():
				if isinstance( n, AssetNode ):
					n.showInBrowser()
					break

		if name == 'open_in_system':
			for n in app.getSelectionManager().getSelection():
				if isinstance( n, AssetNode ):
					n.openInSystem()
					break

		if name == 'copy_node_path':
			text = ''
			for n in app.getSelectionManager().getSelection():
				text += n.getNodePath() + '\n'
				setClipboardText( text )

##----------------------------------------------------------------##
class AssetBrowserTreeView( AssetTreeView ):
	def onClicked(self, item, col):
		pass

	def onItemActivated(self, item, col):
		node=item.node
		if node:
			node.edit()

	def onItemSelectionChanged(self):
		items = self.selectedItems()
		if items:
			selections = [item.node for item in items]
			app.getSelectionManager().changeSelection(selections)
		else:
			app.getSelectionManager().changeSelection(None)
##----------------------------------------------------------------##


AssetBrowser().register()
