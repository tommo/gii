import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.IconCache                  import getIcon
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.controls.GenericListWidget import GenericListWidget

from gii.SceneEditor import SceneEditorModule, SceneTool, SceneToolMeta, SceneToolButton
from gii.SearchView  import requestSearchView

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from mock import _MOCK, isMockInstance

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class SceneToolTilemapPen( SceneTool ):
	name = 'tilemap_pen'
	def onStart( self, **context ):
		app.getModule( 'tilemap_editor' ).changeEditTool( 'pen' )

##----------------------------------------------------------------##
class SceneToolTilemapEraser( SceneTool ):
	name = 'tilemap_eraser'
	def onStart( self, **context ):
		app.getModule( 'tilemap_editor' ).changeEditTool( 'eraser' )

##----------------------------------------------------------------##
class SceneToolTilemapFill( SceneTool ):
	name = 'tilemap_fill'
	def onStart( self, **context ):
		app.getModule( 'tilemap_editor' ).changeEditTool( 'fill' )

##----------------------------------------------------------------##
class SceneToolTilemapTerrain( SceneTool ):
	name = 'tilemap_terrain'
	def onStart( self, **context ):
		app.getModule( 'tilemap_editor' ).changeEditTool( 'terrain' )

##----------------------------------------------------------------##
class TileMapEditor( SceneEditorModule ):
	name       = 'tilemap_editor'
	dependency = [ 'mock' ]

	def onLoad( self ):
		self.container = self.requestDockWindow(
				title = 'Tilemap'
			)
		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('TileMapEditor.ui')
		)

		self.canvas = MOAIEditCanvas( window.containerCanvas )
		self.canvas.loadScript( 
				_getModulePath('TileMapEditor.lua'),
				{
					'_module': self
				}
			)		

		self.toolbarLayers = QtGui.QToolBar( window.containerLayers )
		self.toolbarLayers.setOrientation( Qt.Horizontal )
		self.toolbarLayers.setMaximumHeight( 20 )

		self.toolbarMain = QtGui.QToolBar( window.containerCanvas )
		self.toolbarMain.setOrientation( Qt.Horizontal )
		# self.toolbarMain.setIconSize( 32 )
		
		self.treeLayers = TileMapLayerTreeWidget(
			window.containerLayers,
			editable = True
		 )
		self.treeLayers.parentModule = self

		self.listTerrain = TileMapTerrainList(
			window.containerLayers,
			editable = False,
			mode = 'list'
		)
		self.listTerrain.parentModule = self
		self.listTerrain.setFixedHeight( 70 )
		self.listTerrain.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed )

		self.listCodeTile = CodeTilesetList(
			window.containerLayers,
			editable = False,
			mode = 'list'
		)
		self.listCodeTile.parentModule = self
		self.listCodeTile.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
		self.listCodeTile.hide()

		self.canvas.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

		canvasLayout = QtGui.QVBoxLayout( window.containerCanvas )
		canvasLayout.setSpacing( 0 )
		canvasLayout.setMargin( 0 )

		layersLayout = QtGui.QVBoxLayout( window.containerLayers )
		layersLayout.setSpacing( 0 )
		layersLayout.setMargin( 0 )

		canvasLayout.addWidget( self.canvas )
		canvasLayout.addWidget( self.listTerrain )
		canvasLayout.addWidget( self.listCodeTile )
		canvasLayout.addWidget( self.toolbarMain )

		layersLayout.addWidget( self.toolbarLayers )
		layersLayout.addWidget( self.treeLayers )

		self.addToolBar( 'tilemap_layers', self.toolbarLayers )
		self.addToolBar( 'tilemap_main', self.toolbarMain )
		
		self.addTool( 'tilemap_layers/add_layer',    label = 'Add', icon = 'add' )
		self.addTool( 'tilemap_layers/remove_layer', label = 'Remove', icon = 'remove' )
		self.addTool( 'tilemap_layers/layer_up',     label = 'up', icon = 'arrow-up' )
		self.addTool( 'tilemap_layers/layer_down',   label = 'down', icon = 'arrow-down' )
		self.addTool( 'tilemap_layers/----' )
		self.addTool( 'tilemap_layers/inc_subdiv',   label = 'subD +' )
		self.addTool( 'tilemap_layers/dec_subdiv',   label = 'subD -' )


		self.addTool( 'tilemap_main/tool_pen', 
			widget = SceneToolButton( 'tilemap_pen',
				icon = 'tilemap/pen',
				label = 'Pen'
			)
		)
		self.addTool( 'tilemap_main/tool_terrain', 
			widget = SceneToolButton( 'tilemap_terrain',
				icon = 'tilemap/terrain',
				label = 'Terrain'
			)
		)
		self.addTool( 'tilemap_main/tool_eraser', 
			widget = SceneToolButton( 'tilemap_eraser',
				icon = 'tilemap/eraser',
				label = 'Eraser'
			)
		)
		self.addTool( 'tilemap_main/tool_fill', 
			widget = SceneToolButton( 'tilemap_fill',
				icon = 'tilemap/fill',
				label = 'Fill'
			)
		)
		self.addTool( 'tilemap_main/----' )
		self.addTool( 'tilemap_main/tool_random',   label = 'Random', icon = 'tilemap/random', type = 'check' )
		self.addTool( 'tilemap_main/----' )
		self.addTool( 'tilemap_main/tool_clear',    label = 'Clear', icon = 'tilemap/clear' )

		signals.connect( 'selection.changed', self.onSceneSelectionChanged )

		self.targetTileMap = None
		self.targetTileMapLayer = None

	def onStart( self ):
		self.container.show()
		self.container.setEnabled( False )

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.container.show()
		self.container.setFocus()

	def onSceneSelectionChanged( self, selection, key ):
		if key != 'scene': return
		#find animator component
		target = self.canvas.callMethod( 'editor', 'findTargetTileMap' )
		self.setTargetTileMap( target )

	def onLayerSelectionChanged( self, selection ):
		if selection:
			self.setTargetTileMapLayer( selection[0] )
		else:
			self.setTargetTileMapLayer( None )
		signals.emit( 'scene.update' )

	def onTerrainSelectionChanged( self, selection ):
		if selection:
			self.canvas.callMethod( 'editor', 'setTerrainBrush', selection[0] )
			self.changeSceneTool( 'tilemap_terrain' )

	def onCodeTileSelectionChanged( self, selection ):
		if selection:
			self.canvas.callMethod( 'editor', 'selectCodeTile', selection[0] )

	def clearTerrainSelection( self ):
		self.listTerrain.selectNode( None )

	def setTargetTileMap( self, tileMap ):
		self.setTargetTileMapLayer( None )
		self.canvas.callMethod( 'editor', 'setTargetTileMap', tileMap )
		self.targetTileMap = tileMap
		if not self.targetTileMap:
			self.treeLayers.clear()
			self.container.setEnabled( False )
			return
		self.container.setEnabled( True )
		self.treeLayers.rebuild()
		layers = self.getLayers()
		if layers:
			self.treeLayers.selectNode( layers[0] )

	def setTargetTileMapLayer( self, layer ):
		self.canvas.callMethod( 'editor', 'setTargetTileMapLayer', layer )
		self.canvas.updateCanvas()
		self.targetTileMapLayer = layer
		if isMockInstance( layer, 'CodeTileMapLayer' ):
			self.listCodeTile.show()
			self.listTerrain.hide()
			self.canvas.hide()
			self.listCodeTile.rebuild()
		else:
			self.listCodeTile.hide()
			self.listTerrain.show()
			self.canvas.show()
			self.listTerrain.rebuild()

	def getTerrainTypeList( self ):
		if self.targetTileMapLayer:
			tileset = self.targetTileMapLayer.tileset
			brushTable = tileset.getTerrainBrushes( tileset )
			return [ brush for brush in brushTable.values() ]
		return []

	def getCodeTilesetList( self ):
		if self.targetTileMapLayer:
			tileset = self.targetTileMapLayer.tileset
			return [ key for key in tileset.nameToTile.values() ]
		return []

	def getLayers( self ):
		if not self.targetTileMap: return []
		layers = self.targetTileMap.getLayers( self.targetTileMap )
		return [ layer for layer in layers.values() ]

	def createLayer( self, tilesetNode ):
		layer = self.canvas.callMethod( 'editor', 'createTileMapLayer', tilesetNode.getPath() )
		if layer:
			self.treeLayers.addNode( layer )
			self.treeLayers.selectNode( layer )
			self.treeLayers.editNode( layer )

	def renameLayer( self, layer, name ):
		layer.name = name

	def listTileMapLayerTypes( self, typeId, context ):
		res = self.canvas.callMethod( 'editor', 'requestAvailTileMapLayerTypes' )
		entries = []
		for n in res.values():
			entry = ( n, n, 'LayerTypes', 'obj' )
			entries.append( entry )
		return entries

	def changeEditTool( self, toolId ):
		self.canvas.callMethod( 'editor', 'changeEditTool', toolId )
		if toolId == 'terrain':
			currentBrush = self.canvas.callMethod( 'editor', 'getTerrainBrush' )
			self.listTerrain.selectNode( currentBrush )
			

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_layer':
			if not self.targetTileMap: return
			supportedTilesetTypes = self.targetTileMap.getSupportedTilesetType( self.targetTileMap )
			requestSearchView( 
				context      = 'asset',
				type         = supportedTilesetTypes,
				multiple_selection = False,
				on_selection = self.createLayer,
				# on_search    = self.listTileMapLayerTypes	
			)

		elif name == 'remove_layer':
			self.canvas.callMethod( 'editor', 'removeTileMapLayer' )
			self.treeLayers.rebuild()

		elif name == 'layer_up':
			self.canvas.callMethod( 'editor', 'moveTileMapLayerUp' )
			self.treeLayers.rebuild()

		elif name == 'layer_down':
			self.canvas.callMethod( 'editor', 'moveTileMapLayerDown' )
			self.treeLayers.rebuild()

		elif name == 'tool_clear':
			self.canvas.callMethod( 'editor', 'clearLayer' )
		
		elif name == 'tool_random':
			self.canvas.callMethod( 'editor', 'toggleToolRandom', tool.getValue() )

		elif name == 'inc_subdiv':
			if self.targetTileMapLayer:
				self.canvas.callMethod( 'editor', 'incSubDivision' )
				self.treeLayers.refreshNodeContent( self.targetTileMapLayer )

		elif name == 'dec_subdiv':
			if self.targetTileMapLayer:
				self.canvas.callMethod( 'editor', 'decSubDivision' )
				self.treeLayers.refreshNodeContent( self.targetTileMapLayer )


##----------------------------------------------------------------##
class TileMapLayerTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',120),  ('SubD', 30),  ('Show', 30), ('Tileset',-1) ]

	def getRootNode( self ):
		return self

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	
	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self:
			return None
		return self

	def getNodeChildren( self, node ):
		if node == self:
			return self.parentModule.getLayers()
		return[]

	def updateItemContent( self, item, node, **option ):
		if node == self: return
		item.setIcon( 0, getIcon( 'tilemap/layer' ) )
		item.setText( 0, node.name )

		item.setText( 1, '%d' % node.subdivision )

		if node.visible:
			item.setText( 2, 'Y' )
		else:
			item.setText( 2, '' )
		path = node.getTilesetPath( node ) or ''
		item.setText( 3, os.path.basename(path) )

	def onItemChanged( self, item, col ):
		self.parentModule.renameLayer( item.node, item.text( col ) )

	def onItemSelectionChanged( self ):
		self.parentModule.onLayerSelectionChanged( self.getSelection() )


##----------------------------------------------------------------##
class TileMapTerrainList( GenericListWidget ):
	def getNodes( self ):
		return self.parentModule.getTerrainTypeList()

	def updateItemContent( self, item, node, **option ):
		item.setText( node.name )
		item.setIcon( getIcon( 'tilemap/terrain_item' ) )

	def onItemSelectionChanged( self ):
		self.parentModule.onTerrainSelectionChanged( self.getSelection() )


##----------------------------------------------------------------##
class CodeTilesetList( GenericListWidget ):
	def getNodes( self ):
		return self.parentModule.getCodeTilesetList()

	def updateItemContent( self, item, node, **option ):
		item.setText( node.name )
		item.setIcon( getIcon( 'tilemap/code_item' ) )

	def onItemSelectionChanged( self ):
		self.parentModule.onCodeTileSelectionChanged( self.getSelection() )
