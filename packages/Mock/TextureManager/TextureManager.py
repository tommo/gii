import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import *

from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.controls.PropertyGrid      import PropertyGrid

from gii.AssetEditor  import AssetEditorModule

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


def _fixDuplicatedName( names, name, id = None ):
	if id:
		testName = name + '_%d' % id
	else:
		id = 0
		testName = name
	#find duplicated name
	if testName in names:
		return _fixDuplicatedName( names, name, id + 1)
	else:
		return testName
##----------------------------------------------------------------##

EnumTextureFilter = EnumType(
	'TextureFilter',
	[
		( 'LINEAR',  'linear' ),
		( 'NEAREST', 'neaerest' )
	])

EnumTextureCompression = EnumType(
	'TextureCompression',
	[
		( 'NONE',  False ),
		( 'PVRTC', 'pvrtc' )
	])

EnumTextureSize = EnumType(
	'TextureSize',
	[
		( '32',   32 ),
		( '64',   64 ),
		( '128',  128 ),
		( '256',  256 ),
		( '512',  512 ),
		( '1024', 1024 ),
		( '2048', 2048 ),
		( '4096', 4096 ),
	])

TextureGroupModel = ObjectModel.fromList(
	'TextureGroup',
	[
		( 'filter',             EnumTextureFilter ),
		( 'compression'       , EnumTextureCompression, ),
		( 'mipmap'            , bool,                  dict( label = 'Mipmap') ),
		( 'wrap'              , bool,                  dict( label = 'Wrap') ),
		( 'atlas_allowed'     , bool,                  dict( label = 'Allow atlas') ),
		( 'atlas_max_width'   , EnumTextureSize,       dict( label = 'Max atlas width') ),
		( 'atlas_max_height'  , EnumTextureSize,       dict( label = 'Max atlas height') ),
		( 'atlas_force_single', bool,  dict( label = 'Single atlas') )
	]
	)


##----------------------------------------------------------------##
class TextureManager( AssetEditorModule ):
	"""docstring for MockStyleSheetEditor"""
	def __init__(self):
		super(TextureManager, self).__init__()
	
	def getName(self):
		return 'mock.texture_manager'

	def getDependency(self):
		return [ 'qt', 'moai', 'texture_library' ]

	def onLoad(self):
		self.container = self.requestDocumentWindow( 'MockTextureManager',
				title       = 'TextureManager',
				size        = (500,300),
				minSize     = (500,300),
				# allowDock = False
			)

		self.container.hide()

		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('TextureManager.ui')
		)
		
		self.treeTextures = addWidgetWithLayout(
			TextureTreeWidget( window.containerTextureTree )
		)
		self.treeTextures.module = self

		self.groupProp = addWidgetWithLayout(
			PropertyGrid(window.containerGroupProp)
		)

		window.listGroup.setSortingEnabled(True)
		window.listGroup.itemSelectionChanged.connect( self.onGroupSelectionChanged )

		window.buttonAddGroup    .clicked .connect( self.addGroup )
		window.buttonRemoveGroup .clicked .connect( self.removeGroup )
		window.buttonApplyGroup  .clicked .connect( self.applyGroup )
		window.buttonRebuild     .clicked .connect( self.rebuildTexture )


		# self.getModule( 'asset_editor' ).mainToolBar
		self.addMenuItem(
				'main/asset/texture_manager',
				{
					'label': 'Texture Manager',
					'on_click': lambda menu: self.setFocus()
				}
			)


		self.addTool( 
			'asset/show_texture_manager',
			label = 'Texture Manager',			
			on_click = lambda item: self.setFocus()
			)


	def onStart( self ):
		library = self.getModule( 'texture_library' )
		self.treeTextures.rebuild()
		self.target = {}
		for k, g in library.groups.items() :
			self.window.listGroup.addItem( g.name )
		defaultGroup = library.getGroup( 'default' )

	def onSetFocus( self ):
		self.container.show()
		self.container.raise_()

	def getTextureList( self ):
		return self.getAssetLibrary().enumerateAsset( 'texture' )

	def onGroupSelectionChanged( self ):
		for item in self.window.listGroup.selectedItems():
			groupName = item.text()
			library = self.getModule( 'texture_library' )
			group = library.getGroup( groupName )
			self.groupProp.setTarget( group, model = TextureGroupModel )
			return

	def addGroup( self ):
		name = requestString('Creating Texture Group', 'Enter group name')
		if not name: return
		library = self.getModule( 'texture_library' )
		if library.getGroup( name ):
			alertMessage( 'warning', 'group name duplicated')
			return
		g = library.addGroup( name )
		item = QtGui.QListWidgetItem( name )
		self.window.listGroup.addItem( item )
		item.setSelected( True )

	def removeGroup( self ):
		for item in self.window.listGroup.selectedItems():
			groupName = item.text()
			if groupName == 'default':
				alertMessage( 'warning', 'default texture group cannot be removed')
				return
			self.getModule( 'texture_library' ).removeGroup( groupName )
			self.listGroup.takeItem( item )
			return

	def applyGroup( self ):
		group = None
		for item in self.window.listGroup.selectedItems():
			group = item.text()
			break
		if not group: 
			alertMessage( 'warning', 'no texture group specified')
			return

		for item in self.treeTextures.selectedItems():
			node = item.node

			node.setMetaData( 'group', group, save = True )
			self.treeTextures.updateItem( node )

	def rebuildTexture( self ):
		lib = self.getModule( 'texture_library' )
		lib.saveIndex()
		lib.forceRebuildTextures()

TextureManager().register()

##----------------------------------------------------------------##
class TextureTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [('Name', 200), ('Group', 80), ('Size', 50)]

	def getRootNode( self ):
		return self.module

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.getRootNode(): return None
		return self.getRootNode()
		
	def getNodeChildren( self, node ):
		if node == self.module:
			return node.getTextureList()
		else:
			return []

	def createItem( self, node ):
		return TextureTreeItem()

	def updateItemContent( self, item, node, **option ):
		if node == self.getRootNode(): return

		path  = node.getPath()
		group = node.getMetaData( 'group', 'default' )
		w = node.getProperty('width',  0)
		h = node.getProperty('height', 0)
		item.setText( 0, path )
		item.setText( 1, group )
		item.setText( 2, '%d*%d' % (w,h) )
		
	def onItemSelectionChanged(self):
		selection = [ item.node for item in self.selectedItems() ]
		self.module.getSelectionManager().changeSelection( selection )

	def onDClicked( self, item, col ):
		node = item.node
		self.module.getModule('asset_browser').locateAsset( node )


##----------------------------------------------------------------##
class TextureTreeItem( QtGui.QTreeWidgetItem ):
	pass
