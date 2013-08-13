import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *

from gii.qt           import *
from gii.qt.IconCache import getIcon
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget

from gii.qt.controls.PropertyEditor  import PropertyEditor

from gii.AssetEditor  import AssetEditorModule

from gii.moai.MOAIEditCanvas    import MOAIEditCanvas

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

class Deck2DEditor( AssetEditorModule ):
	"""docstring for Deck2DEditor"""
	def __init__(self):
		super(Deck2DEditor, self).__init__()
		self.editingAsset  = None
		self.editingPack   = None
		self.editingDeck   = None
		self.spriteToItems = {}
	
	def getName(self):
		return 'deck2d_editor'

	def getDependency(self):
		return [ 'qt', 'mock' ]

	def onLoad(self):
		self.windowTitle = 'Deck2D Pack Editor'
		self.container = self.requestDocumentWindow('MockDeck2DEditor',
				title       = 'Deck2D Pack Editor',
				size        = (500,300),
				minSize     = (500,300),
				dock        = 'right'
				# allowDock = False
			)
		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('Deck2DEditor.ui')
		)
		
		self.propEditor = addWidgetWithLayout(
			PropertyEditor(window.settingsContainer),
			window.settingsContainer
		)

		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas( window.canvasContainer ),
			window.canvasContainer
		)
		self.canvas.loadScript( _getModulePath('Deck2DEditor.lua') )
		self.canvas.setDelegateEnv( 'updateEditor', self.onCanvasUpdateRequested )

		#setup listwidget
		treeSprites = addWidgetWithLayout( 
			SpriteTreeWidget( self.window.containerSpriteTree )
			)
		treeSprites.module = self
		treeSprites.itemSelectionChanged.connect(self.onItemSelectionChanged)
		treeSprites.setSortingEnabled(True)
		self.treeSprites = treeSprites

		#signals
		window.toolAddQuad         .clicked. connect( lambda: self.addItem('quad') )
		window.toolAddQuadArray    .clicked. connect( lambda: self.addItem('quad_array') )
		window.toolAddTileset      .clicked. connect( lambda: self.addItem('tileset') )
		window.toolAddStretchPatch .clicked. connect( lambda: self.addItem('stretchpatch') )

		window.toolRemove          .clicked. connect( self.onRemoveItem )
		window.toolClone           .clicked. connect( self.onCloneItem )

		window.toolOriginE         .clicked. connect( lambda: self.setOrigin('E') )
		window.toolOriginS         .clicked. connect( lambda: self.setOrigin('S') )
		window.toolOriginW         .clicked. connect( lambda: self.setOrigin('W') )
		window.toolOriginN         .clicked. connect( lambda: self.setOrigin('N') )
		window.toolOriginSE        .clicked. connect( lambda: self.setOrigin('SE') )
		window.toolOriginSW        .clicked. connect( lambda: self.setOrigin('SW') )
		window.toolOriginNE        .clicked. connect( lambda: self.setOrigin('NE') )
		window.toolOriginNW        .clicked. connect( lambda: self.setOrigin('NW') )
		window.toolOriginC         .clicked. connect( lambda: self.setOrigin('C') )


		self.propEditor .propertyChanged .connect(self.onPropertyChanged)
		signals.connect('asset.modified', self.onAssetModified)

		self.container.setEnabled( False )

	def onSetFocus(self):
		self.container.show()
		self.container.raise_()
		self.container.activateWindow()
		self.container.setFocus()

	def saveAsset(self):
		if self.editingAsset and self.editingPack:
			self.editingAsset.saveAsJson( self.editingPack )

	def startEdit(self, node, subnode=None):
		self.setFocus()
		if self.editingAsset == node: return
		self.saveAsset()
		self.container.setEnabled( True )
		
		assert node.getType() == 'deck2d'
		self.editingAsset = node
		self.container.setDocumentName( node.getNodePath() )
		self.canvas.safeCall( 'openAsset', node.getPath() )

	def getSpriteList( self ):
		return []

	def onCanvasUpdateRequested(self):
		item = self.editingDeck
		if not item : return		
		self.propEditor.refreshAll()

	def addItem( self, atype ):
		if not self.editingAsset: return
		selection = self.getSelectionManager().getSelection()
		if not selection: return

		newItems = []
		for n in selection:
			if not isinstance(n, AssetNode): continue
			if not n.isType( 'texture' ): continue
			#create item
			item = { 
				'name' : n.getBaseName(),
				'src'  : n.getPath(),
				'type' : atype
				}
			deck = self.canvas.safeCall( 'addItem', item )
			self.treeSprites.addNode( deck )
		self.saveAsset()

	def onRemoveItem( self ):
		selection = self.treeSprites.getSelection()
		for deck in selection:
			#todo: remove from pack
			self.treeSprites.removeNode( deck )
		self.saveAsset()

	def onCloneItem( self ):
		pass

	def setOrigin( self, direction ):
		if not self.editingDeck: return 
		self.canvas.safeCall( 'setOrigin', direction )		

	def onPreviewTextChanged( self ):
		pass

	def onAssetModified( self, asset ):
		pass

	def onItemSelectionChanged( self ):
		treeSprites = self.treeSprites
		self.editingDeck = None
		for deck in treeSprites.getSelection():
			self.editingDeck = deck
			self.propEditor.setTarget( deck )
			self.canvas.safeCall( 'selectDeck', deck )			

	def onPropertyChanged( self, obj, id, value ):
		self.canvas.safeCall( 'updateDeck' )

	def onUnload( self ):
		self.saveAsset()


Deck2DEditor().register()

##----------------------------------------------------------------##
class SpriteTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name', 140), ('Type', 40) ]

	def getRootNode( self ):
		return self.module

	def getNodeParent( self, node ):
		if node == self.getRootNode(): return None
		return self.getRootNode()

	def getNodeChildren( self, node ):
		if node == self.module:
			return node.getSpriteList()
		else:
			return []

	def updateItemContent( self, item, node, **option ):
		if node == self.getRootNode() : return
		
		item.setText( 0, node['name'] )
		item.setText( 1, node['type'] )

		if node['type'] == 'stretchpatch':
			item.setIcon( 0, getIcon('deck_patch'))
		elif node['type'] == 'tileset':
			item.setIcon( 0, getIcon('deck_tileset'))
		elif node['type'] == 'quad_array':
			item.setIcon( 0, getIcon('deck_quad_array'))
		else:
			item.setIcon( 0, getIcon('deck_quad'))

	def onItemSelectionChanged( self ):
		pass

	def onItemActivated( self, item, col ):
		pass