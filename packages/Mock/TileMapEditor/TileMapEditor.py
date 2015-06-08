import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget

from gii.SceneEditor  import SceneEditorModule

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
		self.toolbarTileset = QtGui.QToolBar( window.containerCanvas )
		self.toolbarTileset.setOrientation( Qt.Vertical )
		self.toolbarTileset.setMaximumWidth( 20 )
		self.canvas.alwaysForcedUpdate = True
		
		self.treeLayers = TileMapLayerTreeWidget( window.containerLayers )
		self.treeLayers.parentModule = self

		canvasLayout = QtGui.QHBoxLayout( window.containerCanvas )
		canvasLayout.setSpacing( 0 )
		canvasLayout.setMargin( 0 )

		layersLayout = QtGui.QHBoxLayout( window.containerLayers )
		layersLayout.setSpacing( 0 )
		layersLayout.setMargin( 0 )

		canvasLayout.addWidget( self.canvas )
		canvasLayout.addWidget( self.toolbarTileset )

		layersLayout.addWidget( self.treeLayers )
		layersLayout.addWidget( self.toolbarLayers )

		self.addToolBar( 'tilemap_layers', self.toolbarLayers )
		self.addToolBar( 'tilemap_canvas', self.toolbarTileset )
		self.toolbarTileset.hide()
		self.addTool( 'tilemap_layers/add_layer',    label = 'Add', icon = 'add' )
		self.addTool( 'tilemap_layers/remove_layer', label = 'Remove', icon = 'remove' )
		self.addTool( 'tilemap_layers/layer_up',     label = 'up', icon = 'arrow-up' )
		self.addTool( 'tilemap_layers/layer_down',   label = 'down', icon = 'arrow-down' )

		signals.connect( 'selection.changed', self.onSceneSelectionChanged )


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
		target = self.canvas.callMethod( 'editor', 'findTargetMap' )
		self.setTargetTileMap( target )

	def onLayerSelectionChanged( self, selection ):
		pass

	def setTargetTileMap( self, tileMap ):
		self.targetTileMap = tileMap
		if not self.targetTileMap:
			self.treeLayers.clear()
			self.container.setEnabled( False )
			return
		self.container.setEnabled( True )
		self.treeLayers.rebuild()

	def getLayers( self ):
		if not self.targetTileMap: return []
		return self.targetTileMap.getLayers( self.targetTileMap )

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_layer':
			pass #TODO
		elif name == 'remove_layer':
			pass #TODO
		elif name == 'layer_up':
			pass #TODO
		elif name == 'layer_down':
			pass #TODO


##----------------------------------------------------------------##
class TileMapLayerTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',150), ('View', 30), ('Tileset',-1) ]

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
		pass

	def onSelectionChanged( self, selection ):
		self.parentModule.onLayerSelectionChanged( selection )

