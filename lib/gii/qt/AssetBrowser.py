import random
from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

from gii.core         import *
from gii.qt           import QtEditorModule

from gii.qt.controls.AssetTreeView import AssetTreeView

##----------------------------------------------------------------##
SortUserRole=QtCore.Qt.UserRole
##----------------------------------------------------------------##
class AssetPreviewer(object):
	def accept(self, selection):
		return False

	def createWidget(self):
		return None

	def onStart(self, selection):
		pass

	def onStop(self):
		pass
		
class NullAssetPreviewer(AssetPreviewer):
	def createWidget(self,container):
		self.label = QtGui.QLabel(container)
		self.label.setAlignment(QtCore.Qt.AlignHCenter)
		self.label.setText('NO PREVIEW')
		self.label.setSizePolicy(
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding
				)
		return self.label

	def onStart(self, selection):
		pass
		# self.label.setParent(container)

	def onStop(self):
		pass


class AssetCreator(object):
	def createAsset(self, name, contextNode, assetType):
		return False


class FolderCreator(AssetCreator):
	def createAsset(self, name, contextNode, assetType):
		if assetType == 'folder':
			if contextNode.isType('folder'):
				nodepath = contextNode.getChildPath(name)
			else:
				nodepath=contextNode.getSiblingPath(name)
			fullpath = app.getAssetLibrary().getAbsPath(nodepath)
			try:
				os.mkdir(fullpath)
			except Exception,e :
				print( 'failed create folder', e )
				return False
			return nodepath
		else:
			return False

def registerAssetPreviewer(previewer):
	return App.get().getModule('asset_browser').registerPreviewer(previewer)

def registerAssetCreator(assetType, creator, **kwargs):
	return App.get().getModule('asset_browser').registerAssetCreator(assetType,creator,**kwargs)

def setAssetIcon( assetType, iconName ):
	return App.get().getModule('asset_browser').setAssetIcon( assetType, iconName )
	
##----------------------------------------------------------------##
class AssetBrowser( QtEditorModule ):
	"""docstring for AssetBrowser"""
	def __init__(self):
		super(AssetBrowser, self).__init__()
		self.previewers        = []
		self.creators          = []
		self.assetIconMap      = {}

		self.activePreviewer   = None		
		self.newCreateNodePath = None

	def getName(self):
		return 'asset_browser'

	def getDependency(self):
		return ['qt']

	def onLoad(self):
		self.container = self.requestDockWindow('AssetBrowser',
				title='Asset Browser',
				dock='left',
				minSize=(250,400)
			)

		self.searchBox = self.container.addWidgetFromFile(
				self.getApp().getPath( 'data/ui/search.ui' ),
				expanding = False
			)
		self.treeView  = self.container.addWidget(AssetTreeView())

		self.previewerContainer = QtGui.QStackedWidget()
		self.previewerContainer.setSizePolicy(
				QtGui.QSizePolicy.Expanding, 
				QtGui.QSizePolicy.Fixed
			)
		self.previewerContainer.setMinimumSize(100,250)
		self.container.addWidget( self.previewerContainer, expanding=False )

		self.nullPreviewer = self.registerPreviewer( NullAssetPreviewer() )

		signals.connect( 'module.loaded',        self.onModuleLoaded )		
		signals.connect( 'asset.deploy.changed', self.onAssetDeployChanged )
	
		signals.connect( 'selection.changed',    self.onSelectionChanged)

		self.treeView.setContextMenuPolicy( QtCore.Qt.CustomContextMenu)
		self.treeView.customContextMenuRequested.connect( self.onTreeViewContextMenu)
		self.treeView.setAssetIconMap( self.assetIconMap )

		self.assetMenu=self.addMenu('main/asset', {'label':'&Asset'})
		self.creatorMenu=self.addMenu('main/asset/asset_create',{'label':'Create'})

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

		self.registerAssetCreator('folder', FolderCreator(), label='Folder')

	def onStart( self ):
		signals.connect( 'asset.register',   self.onAssetRegister )
		signals.connect( 'asset.unregister', self.onAssetUnregister )
		signals.connect( 'asset.moved',      self.onAssetMoved )
		self.treeView.rebuild()

	def onUnload(self):
		#persist expand state
		self.treeView.saveTreeStates()

				
	def onModuleLoaded(self):
		for previewer in self.previewers:
			self._loadPreviewer(previewer)

		for setting in self.creators:
			self._loadCreator(setting)

	def setAssetIcon(self, assetType, iconName):
		self.assetIconMap[assetType] = iconName

	def registerAssetCreator(self, assetType, creator, **kwargs):
		label=kwargs.get( 'label', assetType )
		setting={
			'assetType':assetType,
			'creator':creator,
			'label':label
			}
		self.creators.append( setting )
		if self.alive:
			self._loadCreator( setting )

	def _loadCreator(self, setting):
		label     = setting['label']
		assetType = setting['assetType']
		creator   = setting['creator']

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
				alertMessage('Asset Creation Error',repr(e))
				return
		#insert into toolbar box?
		#insert into create menu
		self.creatorMenu.addChild({
				'name':'create_'+assetType,
				'label':label,
				'onClick':creatorFunc
			})

			
	def registerPreviewer(self, previewer):
		self.previewers.insert(0, previewer) #TODO: use some dict?
		if self.alive: self._loadPreviewer(previewer)		
		return previewer

	def _loadPreviewer(self, previewer):
		widget=previewer.createWidget(self.previewerContainer)
		assert isinstance(widget,QtGui.QWidget), 'widget expected from previewer'
		idx=self.previewerContainer.addWidget(widget)
		previewer._stackedId=idx
		previewer._widget=widget

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

	def onSelectionChanged(self, selection):
		if self.activePreviewer:
			self.activePreviewer.onStop()

		if selection and isinstance(selection[0], AssetNode) :
			target=selection[0]
			for previewer in self.previewers:
				if previewer.accept(target):
					self._startPreview(previewer, target)
					return

		self._startPreview(self.nullPreviewer, None)

	def _startPreview(self, previewer, selection):
		idx=previewer._stackedId
		self.previewerContainer.setCurrentIndex(idx)
		self.activePreviewer=previewer		
		previewer.onStart(selection)
	
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
		self.treeView.updateItemContent(node, 
				basic=False, deploy=True, 
				updateChildren=True, updateDependency=True
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
					n.forceReimport()
			app.getAssetLibrary().scanProjectPath()

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


AssetBrowser().register()
