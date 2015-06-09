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

from gii.SceneEditor  import SceneEditorModule
from gii.SearchView import requestSearchView

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from mock import _MOCK, isMockInstance

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


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
		self.toolbarLayers.setOrientation( Qt.Vertical )
		self.toolbarLayers.setMaximumWidth( 20 )

		self.toolbarMain = QtGui.QToolBar( window.containerCanvas )
		self.toolbarMain.setOrientation( Qt.Horizontal )
		# self.toolbarMain.setIconSize( 32 )
		self.canvas.alwaysForcedUpdate = True
		
		self.treeLayers = TileMapLayerTreeWidget(
			window.containerLayers,
			editable = True
		 )
		self.treeLayers.parentModule = self

		canvasLayout = QtGui.QVBoxLayout( window.containerCanvas )
		canvasLayout.setSpacing( 0 )
		canvasLayout.setMargin( 0 )

		layersLayout = QtGui.QHBoxLayout( window.containerLayers )
		layersLayout.setSpacing( 0 )
		layersLayout.setMargin( 0 )

		canvasLayout.addWidget( self.canvas )
		canvasLayout.addWidget( self.toolbarMain )

		layersLayout.addWidget( self.treeLayers )
		layersLayout.addWidget( self.toolbarLayers )

		self.addToolBar( 'tilemap_layers', self.toolbarLayers )
		self.addToolBar( 'tilemap_main', self.toolbarMain )
		
		self.addTool( 'tilemap_layers/add_layer',    label = 'Add', icon = 'add' )
		self.addTool( 'tilemap_layers/remove_layer', label = 'Remove', icon = 'remove' )
		self.addTool( 'tilemap_layers/layer_up',     label = 'up', icon = 'arrow-up' )
		self.addTool( 'tilemap_layers/layer_down',   label = 'down', icon = 'arrow-down' )

		self.addTool( 'tilemap_main/tool_pen',     label = 'Pen',   icon = 'tilemap/pen' )
		self.addTool( 'tilemap_main/tool_eraser',  label = 'Eraser', icon = 'tilemap/eraser' )
		self.addTool( 'tilemap_main/tool_fill',    label = 'Fill', icon = 'tilemap/fill' )
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

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_layer':
			requestSearchView( 
				context      = 'asset',
				type         = 'tileset;named_tileset',
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

		elif name == 'tool_pen':
			self.canvas.callMethod( 'editor', 'changeEditTool', 'pen' )

		elif name == 'tool_eraser':
			self.canvas.callMethod( 'editor', 'changeEditTool', 'eraser' )

		elif name == 'tool_fill':
			self.canvas.callMethod( 'editor', 'changeEditTool', 'fill' )

		elif name == 'tool_clear':
			self.canvas.callMethod( 'editor', 'changeEditTool', 'clear' )




##----------------------------------------------------------------##
class TileMapLayerTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',90), ('Show', 30), ('Tileset',-1) ]

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
		if node.visible:
			item.setText( 1, 'Y' )
		else:
			item.setText( 1, '' )
		path = node.getTilesetPath( node ) or ''
		item.setText( 2, os.path.basename(path) )

	def onItemChanged( self, item, col ):
		self.parentModule.renameLayer( item.node, item.text( col ) )

	def onItemSelectionChanged( self ):
		self.parentModule.onLayerSelectionChanged( self.getSelection() )

