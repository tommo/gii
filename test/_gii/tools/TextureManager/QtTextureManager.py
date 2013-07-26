import subprocess
import os.path
import shutil
import time
import json

from PyQt4                      import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore               import Qt

from gii.core                   import *
from gii.qt                     import QtEditorModule
from gii.qt.helpers             import *

from gii.moai.MOAIEditCanvas       import MOAIEditCanvas
from gii.qt.controls.PropertyGrid  import PropertyGrid

##----------------------------------------------------------------##

modelTexPack = ObjectModel('TexPack')
modelTexPack.addFieldInfo( 'name',          str )
modelTexPack.addFieldInfo( 'width',         int,  label='Tex Width' )
modelTexPack.addFieldInfo( 'height',        int,  label='Tex Height' )
modelTexPack.addFieldInfo( 'allowRotate',   bool, label='Allow Rotate' )
modelTexPack.addFieldInfo( 'allowMultiple', bool, label='Multiple Atlas' )

##----------------------------------------------------------------##
def convertAtlas(inputfile,  basepath):
	f = open(inputfile, 'r')
	items   = []
	atlases = []
	for line in f.readlines():
		parts = line.split('\t')
		path  = parts[1]
		if path.startswith('\"'):
			path = path[1:-1]
		path = os.path.relpath(path, basepath)
		name = os.path.basename(path)
		atlasName = parts[0]
		if not atlasName in atlases:
			atlases.append(atlasName)
		atlasId = atlases.index(atlasName)
		data = {
			'atlas':atlasId,
			'name':name,
			'source':path,
			'rect':[int(x) for x in parts[2:]]
		}
		items.append(data)
	output = {
		'atlases':[os.path.basename(atlasPath) for atlasPath in atlases],
		'items':items,
	}

	return output

##----------------------------------------------------------------##
class QtTexturePacker( QtEditorModule ):
	"""docstring for QtTexturePacker"""
	def __init__(self):
		super(QtTexturePacker, self).__init__()
		self.textureSet     = {}
		self.editingAsset   = None
		self.generatedAtlas = None
	
	def getName(self):
		return 'texture_packer'

	def getDependency(self):
		return ['qt','moai.runtime']

	def onLoad(self):
		self.container = self.requestDockWindow( 'TexturePacker',
				title   = 'Texture Packer',
				size    = (500,300),
				minSize = (500,300),
				dock    = 'main'
				# allowDock=False
			)
		self.window = window = self.container.addWidgetFromFile(
				Project.get().getToolPath( '_ui/TexpackEditor.ui' )
			)
		self.propGrid = addWidgetWithLayout(
			PropertyGrid(window.settingsContainer),
			window.settingsContainer
		)

		layout = QtGui.QVBoxLayout( window.previewContainer )
		layout.setMargin(0)
		layout.setSpacing(0)

		self.pageTab = QtGui.QTabBar( window.previewContainer )
		self.pageTab.setDocumentMode(True)
		layout.addWidget(self.pageTab)
		self.pageTab.addTab('Output')

		self.previewCanvas = MOAIEditCanvas( window.previewContainer )
		layout.addWidget(	self.previewCanvas )
		self.previewCanvas.loadScript( Project.get().getToolPath('_lua/TexturePackerCanvas.lua') )
		self.previewCanvas.setDelegateEnv('selectSubTexture', self.selectSubTexture)

		window.listTextures.itemSelectionChanged.connect(self.onItemSelectionChanged)
		window.listTextures.setSortingEnabled(True)

		window.toolAdd.clicked      .connect( self.onAddTexture )
		window.toolRemove.clicked   .connect( self.onRemoveTexture )
		window.toolGenerate.clicked .connect( self.generateAtlas )

		signals.connect('asset.modified', self.onAssetModified)

	def onSetFocus(self):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def edit(self, node, subnode=None):
		if self.editingAsset!=node:
			assert node.getType()=='texpack'
			metadata = node.getMetaData()			
			self.propGrid.setTarget( metadata, model = modelTexPack )
			self.propGrid.propertyChanged.connect( self.onSettingChanged )
			self.container.setWindowTitle('Texture Packer <%s>'%node.getNodePath())
			self.editingAsset = node
			self.textureSet={}
			#load texpack
			try:
				f=open(node.getAbsFilePath(),'r')
				data=json.load(f)
				f.close()
			except Exception, e:
				#TODO: pop some alert
				return

			if data.has_key('items'):
				for item in data['items']:
					source  = item.get('source',None)
					if not source: continue
					srcnode = AssetLibrary.get().getAssetNode(source)
					if srcnode:
						self.textureSet[srcnode]=True

			self.previewCanvas.safeCall('openAsset', node.getPath().encode('utf-8'))

		self.window.show()
		self.refreshTextureView()

	def refreshTextureView(self):
		listTextures = self.window.listTextures
		listTextures.clear()
		for n in self.textureSet:
			listTextures.addItem(n.getNodePath())

	def onAddTexture(self):
		if not self.editingAsset: return
		s = SelectionManager.get().getSelection()
		listTextures = self.window.listTextures
		listTextures.selectionModel().clearSelection()
		#check selection
		for n in s:
			if not isinstance(n, AssetNode): continue
			if n == self.editingAsset: continue
			if self.editingAsset.hasDependency(n): continue
			if n.hasDependency(self.editingAsset): continue
			if not n.getType() in ('texture'): continue
			if not self.textureSet.has_key(n):
				self.textureSet[n]=True #todo: subtexture option
				item=QtGui.QListWidgetItem(n.getNodePath())				
				listTextures.addItem(item)
				item.setSelected(True)

	def onRemoveTexture(self):
		listTextures = self.window.listTextures
		selected     = listTextures.selectedItems()
		if not selected: return
		for item in selected:
			path = item.text()
			node = AssetLibrary.get().getAssetNode(path)
			assert(self.textureSet.has_key(node))
			del self.textureSet[node]
			row = listTextures.row(item)
			listTextures.takeItem(row)

	def onItemSelectionChanged(self):
		listTextures = self.window.listTextures
		s = [ item.text() for item in listTextures.selectedItems() ]
		self.previewCanvas.safeCall('setSelectedItem', s)

	def generateAtlas(self):
		tmpDir = TempDir()
		editingAsset = self.editingAsset
		if not editingAsset: return
		sourceList = [ node.getAbsFilePath() for node in self.textureSet ]
		name,ext=os.path.splitext( editingAsset.getName() )
		name += '_atlas'
		prefix=tmpDir( name )
		
		arglist = ['python', Project.get().getToolPath('_ext_tools/atlasgenerator.py'), '--prefix', prefix, '1024', '1024']
		arglist += sourceList
		try:
			ex = subprocess.call(arglist) #run packer
			#conversion
			srcFile = prefix+'.txt'
			data    = convertAtlas(srcFile,  getProjectPath())
			dstPath = editingAsset.getAbsDir()
			#copy generated atlas
			for i in range(0,len(data['atlases'])):
				src, dst = '%s%d.png'%(prefix,i),  '%s/%s%d.png'%( dstPath, name, i)
				print( src, dst )
				shutil.copy( src, dst )

			#update texpack
			data['sources'] = sourceList
			fp = open( editingAsset.getAbsFilePath(), 'w' )
			json.dump(data, fp, sort_keys=True,indent=2)
			fp.close()

		except Exception,e:
			print('failed to pack atlas',e)
			return False

		return True

	def selectSubTexture(self, source, multiSelecting):
		if not self.editingAsset: return
		#find source in listview
		listTextures=self.window.listTextures

		if multiSelecting:
			for item in listTextures.findItems( source, QtCore.Qt.MatchExactly ):
				item.setSelected(not item.isSelected()) #toggle
		else:
			listTextures.selectionModel().clearSelection()
			for item in listTextures.findItems( source, QtCore.Qt.MatchExactly ):
				item.setSelected( True )

	def onAssetModified(self, asset):
		if asset == self.editingAsset:
			self.previewCanvas.safeCall('openAsset', self.editingAsset.getPath().encode('utf-8'))

	def onSettingChanged(self, data, field, value):
		print('setting:', field, value )

QtTexturePacker().register()
