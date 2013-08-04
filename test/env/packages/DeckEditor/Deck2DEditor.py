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

from gii.qt.controls.PropertyGrid  import PropertyGrid

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

class MockStyleSheetEditor( AssetEditorModule ):
	"""docstring for MockStyleSheetEditor"""
	def __init__(self):
		super(MockStyleSheetEditor, self).__init__()
		self.editingAsset  = None
		self.editingPack   = None
		self.editingItem   = None
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
		
		self.propGrid = addWidgetWithLayout(
			PropertyGrid(window.settingsContainer),
			window.settingsContainer
		)

		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas(window.canvasContainer),
			window.canvasContainer
		)
		self.canvas.loadScript( _getModulePath('Deck2DEditor.lua') )
		self.canvas.setDelegateEnv( 'updateEditor', self.onCanvasUpdateRequested )

		#setup listwidget
		listSprites = window.listSprites
		listSprites.itemSelectionChanged.connect(self.onItemSelectionChanged)
		listSprites.setSortingEnabled(True)
		#header item
		headerItem=QtGui.QTreeWidgetItem()		
		headerItem.setText( 0, 'Name' ) ; listSprites.setColumnWidth( 0, 140 )
		headerItem.setText( 1, 'Type' ) ; listSprites.setColumnWidth( 1, 40 )
		listSprites.setHeaderItem(headerItem)

		#signals
		window.toolAddQuad         .clicked. connect( self.onAddQuad )
		window.toolAddQuadArray    .clicked. connect( self.onAddQuadArray )
		window.toolAddTileset      .clicked. connect( self.onAddTileset )
		window.toolAddStretchPatch .clicked. connect( self.onAddStretchPatch )
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


		self.propGrid .propertyChanged .connect(self.onPropertyChanged)
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
		self.canvas.safeCall('openAsset', node.getPath())

	def refreshList(self):
		self.window.listSprites.clear()

	def onCanvasUpdateRequested(self):
		item = self.editingItem
		if not item : return		
		self.propGrid.refreshAll()

	def onAddQuad( self ):
		return self.addItem('quad')

	def onAddQuadArray( self ):
		return self.addItem('quad_array')

	def onAddTileset( self ):
		return self.addItem('tileset')

	def onAddStretchPatch( self ):
		return self.addItem('stretchpatch')

	def findSpriteItem(self, name):
		if not self.editingPack: return None
		for item in self.editingPack['items'] :
			if item['name'] == name : return item
		return None

	def addItem( self, atype ):
		if not self.editingAsset: return
		s = self.getSelectionManager().getSelection()
		if not s: return		
		self.saveAsset()

	def addListItem( self, item ):
		rootItem = self.window.listSprites.invisibleRootItem()
		listItem = QtGui.QTreeWidgetItem()
		listItem.setText( 0, item['name'])
		listItem.setText( 1, item['type'])
		if item['type'] == 'stretchpatch':
			listItem.setIcon( 0, getIcon('deck_patch'))
		elif item['type'] == 'tileset':
			listItem.setIcon( 0, getIcon('deck_tileset'))
		elif item['type'] == 'quad_array':
			listItem.setIcon( 0, getIcon('deck_quad_array'))
		else:
			listItem.setIcon( 0, getIcon('deck_quad'))

		rootItem.addChild( listItem )
		return listItem

	def onRemoveItem( self ):
		listSprites=self.window.listSprites
		selected=listSprites.selectedItems()
		if not selected: return
		items = self.editingPack['items']
		for item in selected:
			name = item.text( 0 )
			sp = self.findSpriteItem( name )
			assert sp
			idx =  items.index( sp )
			items.pop(idx)
			(item.parent() or listSprites.invisibleRootItem()).removeChild(item)
		self.saveAsset()

	def onCloneItem( self ):
		pass

	def setOrigin( self, direction ):
		if not self.editingItem: return 
		self.canvas.safeCall( 'setOrigin', direction )		

	def onPreviewTextChanged( self ):
		pass

	def onAssetModified( self, asset ):
		pass

	def onItemSelectionChanged( self ):
		listSprites = self.window.listSprites
		self.editingItem = None
		for item in listSprites.selectedItems():
			name = item.text(0)
			sp = self.findSpriteItem( name )
			self.editingItem = sp
			deckType = sp ['type']
			
			self.propGrid.setTarget( sp, model = deckModels[ deckType ] )
			self.canvas.safeCall('selectItem', sp)
			break

	def onPropertyChanged( self, obj, id, value ):
		self.canvas.safeCall('updateItemFromEditor', obj, id, value)
		self.canvas.updateCanvas()

	def onUnload( self ):
		self.saveAsset()


MockStyleSheetEditor().register()
