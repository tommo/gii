import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.SceneEditor  import SceneEditorModule, SceneTool

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt



##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


##----------------------------------------------------------------##
class SceneView( SceneEditorModule ):
	name       = 'scene_view'
	dependency = [ 'mock', 'scene_editor', 'scenegraph_editor', 'scene_tool_box' ]

	def onLoad( self ):
		self.window = self.requestDocumentWindow(
				title = 'Scene'
			)
		self.toolbar = self.window.addToolBar()

		self.canvas = self.window.addWidget( MOAIEditCanvas() )
		self.canvas.loadScript( _getModulePath('SceneView.lua') )
		
		self.canvas.setDelegateEnv( '_giiSceneView', self )

		self.updateTimer        = self.window.startTimer( 60, self.onUpdateTimer )
		self.updatePending      = False
		self.previewing         = False
		self.previewUpdateTimer = False

		signals.connect( 'entity.modified',       self.onEntityModified   )
		signals.connect( 'asset.post_import_all', self.onAssetReimport    )
		signals.connect( 'scene.open',            self.onSceneOpen        )
		signals.connect( 'scene.close',           self.onSceneClose       )
		signals.connect( 'scene.change',          self.onSceneUpdate      )
		signals.connect( 'scene.update',          self.onSceneUpdate      )
		signals.connect( 'selection.changed',     self.onSelectionChanged )

		signals.connect( 'animator.start', self.onAnimatorStart )
		signals.connect( 'animator.stop',  self.onAnimatorStop )

		signals.connect( 'preview.resume', self.onPreviewResume )
		signals.connect( 'preview.pause',  self.onPreviewStop   )
		signals.connect( 'preview.stop',   self.onPreviewStop   )

		signals.connect( 'tool.change',   self.onSceneToolChanged   )

		self.addShortcut( 'main', 'Q', self.changeEditTool, 'selection' )
		self.addShortcut( 'main', 'W', self.changeEditTool, 'translation' )
		self.addShortcut( 'main', 'E', self.changeEditTool, 'rotation' )
		self.addShortcut( 'main', 'R', self.changeEditTool, 'scale' )
		self.addShortcut( 'main', 'F', self.focusSelection )

		self.addShortcut( 'main', '/', self.toggleDebugLines )

		self.mainToolBar = self.addToolBar( 'scene_view_tools', 
			self.getMainWindow().requestToolBar( 'view_tools' )
			)
		self.mainToolBar.qtToolbar.setIconSize( QtCore.QSize( 24, 24 ) )

		self.addTool( 'scene_view_tools/tool_selection',
			label = 'Selection',
			icon = 'tools/selection',
			type = 'check'
			)

		self.addTool( 'scene_view_tools/tool_translation',
			label = 'Translate',
			icon = 'tools/translate',
			type = 'check'
			)

		self.addTool( 'scene_view_tools/tool_rotation',
			label = 'Rotate',
			icon = 'tools/rotate',
			type = 'check'
			)

		self.addTool( 'scene_view_tools/tool_scale',
			label = 'Scale',
			icon = 'tools/scale',
			type = 'check'
			)


	def onStart( self ):
		self.scheduleUpdate()

	def changeEditTool( self, name ):
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'view', 'changeEditTool', name )

	def toggleDebugLines( self ):
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'view', 'toggleDebugLines' )

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			self.canvas.updateCanvas( no_sim = self.previewing, forced = True )
			if not self.previewing:
				self.getModule( 'scene_preview' ).refresh()

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.window.show()
		self.window.setFocus()

	def onEntityModified( self, entity, context = None ):
		self.scheduleUpdate()

	def onAssetReimport( self ):
		self.scheduleUpdate()

	def onSceneUpdate( self ):
		self.scheduleUpdate()

	def onSceneOpen( self, node, scene ):
		self.window.setDocumentName( node.getPath() )
		self.canvas.show()
		self.canvas.safeCall( 'onSceneOpen', scene )
		self.scheduleUpdate()
		self.setFocus()
		self.changeEditTool( 'translation' )
		# self.preview.update

	def onSceneClose( self, node ):
		self.window.setDocumentName( None )
		self.canvas.safeCall( 'onSceneClose' )
		self.canvas.hide()

	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		self.canvas.safeCallMethod( 'view', 'onSelectionChanged', selection )

	def updateInPreview( self ):
		self.scheduleUpdate()
		introspector = self.getModule('introspector')
		if introspector:
			introspector.refresh()

	def onPreviewResume( self ):
		self.previewing = True
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: 1px solid rgb(0, 120, 0); }')
		self.previewUpdateTimer = self.window.startTimer( 3, self.updateInPreview )

	def onPreviewStop( self ):
		self.previewing = False
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: none }')
		self.previewUpdateTimer.stop()

	def onAnimatorStart( self ):
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: 1px solid rgb(255, 0, 120); }')
		self.animating = True

	def onAnimatorStop( self ):
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: none }')
		self.animating = True

	def scheduleUpdate( self ):
		self.updatePending = True

	def forceUpdate( self ):
		self.scheduleUpdate()
		self.onUpdateTimer()

	def focusSelection( self ):
		self.canvas.safeCallMethod( 'view', 'focusSelection' )

	def onTool( self, tool ):
		name = tool.name
		if name == 'tool_selection':
			self.changeEditTool( 'selection' )
		elif name == 'tool_translation':
			self.changeEditTool( 'translation' )
		elif name == 'tool_rotation':
			self.changeEditTool( 'rotation' )
		elif name == 'tool_scale':
			self.changeEditTool( 'scale' )

	def onSceneToolChanged( self, tool ):
		pass
