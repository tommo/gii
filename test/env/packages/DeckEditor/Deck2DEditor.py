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
deckModels={
	'quad' : ObjectModel.fromList( 
		'Quad',
		[
			( 'name', unicode,  dict(label = 'Name', readonly = True) ),
			( 'src',  unicode,  dict(label = 'Source', readonly = True) ),
			( 'ox',   int,      dict(label = 'Origin X')),
			( 'oy',   int,      dict(label = 'Origin Y')),
		]
	),

	'stretchpatch' : ObjectModel.fromList( 
		'Stretch Patch',
		[
			( 'name', unicode,  dict(label = 'Name', readonly = True) ),
			( 'src',  unicode,  dict(label = 'Source', readonly = True) ),
			( 'ox',   int,      dict(label = 'Origin X')),
			( 'oy',   int,      dict(label = 'Origin Y')),
			( 'row1', float ),
			( 'row2', float ),
			( 'row3', float ),
			( 'col1', float ),
			( 'col2', float ),
			( 'col3', float ),
		]
	),

	'tileset' : ObjectModel.fromList( 
		'Tile Set',
		[
			( 'name',    unicode,  dict(label = 'Name', readonly = True) ),
			( 'src',     unicode,  dict(label = 'Source', readonly = True) ),
			( 'ox',      int,      dict(label = 'Origin X')),
			( 'oy',      int,      dict(label = 'Origin Y')),
			( 'width',   int ),
			( 'height',  int ),
			( 'gutter',  int ),
			( 'offsetX', int ),
			( 'offsetY', int ),
		]
	)
}

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

		self.previewCanvas = addWidgetWithLayout(
			MOAIEditCanvas(window.canvasContainer),
			window.canvasContainer
		)
		self.previewCanvas.loadScript( _getModulePath('Deck2DEditor.lua') )
		self.previewCanvas.setDelegateEnv( 'updateEditor', self.onCanvasUpdateRequested )

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
		# window.textPreview.textChanged.connect( self.onPreviewTextChanged )
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
		self.propGrid.setTarget(node)
		
		self.window.show()
		self.refreshList()
		self.editingPack = node.loadAsJson()
		
		for item in self.editingPack.get('items', []):
			self.addListItem( item )

		self.previewCanvas.safeCall('openAsset', node.getPath().encode('utf-8'))

	def refreshList(self):
		self.window.listSprites.clear()

	def onCanvasUpdateRequested(self):
		item = self.editingItem
		if not item : return
		canvas = self.previewCanvas
		
		item [ 'ox' ] = canvas.getDelegateEnv( 'originX', 0 )
		item [ 'oy' ] = canvas.getDelegateEnv( 'originY', 0 )

		if item['type'] == 'stretchpatch':
			item [ 'row1' ] = canvas.getDelegateEnv( 'row1', 0.33 )
			item [ 'row2' ] = canvas.getDelegateEnv( 'row2', 0.33 )
			item [ 'row3' ] = canvas.getDelegateEnv( 'row3', 0.33 )
			item [ 'col1' ] = canvas.getDelegateEnv( 'col1', 0.33 )
			item [ 'col2' ] = canvas.getDelegateEnv( 'col2', 0.33 )
			item [ 'col3' ] = canvas.getDelegateEnv( 'col3', 0.33 )
			
		if item['type'] == 'tileset':
			item [ 'width' ]   = canvas.getDelegateEnv( 'tileWidth', 32 )
			item [ 'height' ]  = canvas.getDelegateEnv( 'tileHeight', 32 )
			item [ 'gutter' ]  = canvas.getDelegateEnv( 'gutter', 0 )
			item [ 'offsetX' ] = canvas.getDelegateEnv( 'offsetX', 0 )
			item [ 'offsetY' ] = canvas.getDelegateEnv( 'offsetY', 0 )
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
		newItems = []
		for n in s:
			if not isinstance(n, AssetNode): continue
			if n==self.editingAsset: continue
			if self.editingAsset.hasDependency(n): continue
			if n.hasDependency(self.editingAsset): continue
			if not n.getType() in ( 'texture', 'sub_texture' ): continue #TODO: support sub_texture
			#create item
			item = { 
				'name' : n.getBaseName(),
				'src'  : n.getPath(),
				'type' : atype
				}
			newItems.append( item )

		#rename duplicated one		
		packItems = self.editingPack['items']
		names = [ item0['name'] for item0 in packItems ]
		for item in newItems: 
			name = _fixDuplicatedName( names , item['name'] )
			item['name'] = name
			names.append( name )
			packItems.append( item )

		for item in newItems: 
			#insert into listWidget
			self.addListItem( item )
			pass

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
		self.previewCanvas.safeCall( 'setOrigin', direction )		

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
			self.previewCanvas.safeCall('selectItem', sp)
			break

	def onPropertyChanged( self, obj, id, value ):
		self.previewCanvas.safeCall('updateItemFromEditor', obj, id, value)
		self.previewCanvas.updateCanvas()

	def onUnload( self ):
		self.saveAsset()


MockStyleSheetEditor().register()
