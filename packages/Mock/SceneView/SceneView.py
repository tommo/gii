import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.SceneEditor  import SceneEditorModule

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class SceneView( SceneEditorModule ):
	def getName( self ):
		return 'scene_view'

	def getDependency( self ):
		return [ 'mock', 'scene_editor', 'scenegraph_editor' ]

	def onLoad( self ):
		self.window = self.requestDocumentWindow(
				title = 'Scene'
			)
		self.canvas = self.window.addWidget( MOAIEditCanvas() )
		self.canvas.loadScript( _getModulePath('SceneView.lua') )
		self.canvas.setDelegateEnv( '_view', self )

		self.updateTimer = self.window.startTimer( 60, self.onUpdateTimer )
		self.updatePending = False
		self.previewing = False
		self.previewUpdateTimer = False
		self.preview = self.getModule( 'scene_preview' )

		signals.connect( 'entity.modified',   self.onEntityModified   )
		signals.connect( 'asset.post_import_all',   self.onAssetReimport  )
		signals.connect( 'scene.open',        self.onSceneOpen        )
		signals.connect( 'scene.close',       self.onSceneClose       )
		signals.connect( 'scene.update',      self.onSceneUpdate      )
		signals.connect( 'selection.changed', self.onSelectionChanged )

		signals.connect( 'preview.resume', self.onPreviewResume )
		signals.connect( 'preview.pause', self.onPreviewStop )
		signals.connect( 'preview.stop', self.onPreviewStop )

		self.addShortcut( 'main', 'W', self.changeEditTool, 'translation' )
		self.addShortcut( 'main', 'E', self.changeEditTool, 'rotation' )
		self.addShortcut( 'main', 'R', self.changeEditTool, 'scale' )
		self.addShortcut( 'main', 'F', self.focusSelection )

		self.addShortcut( 'main', '/', self.toggleDebugLines )


	def onStart( self ):
		self.canvas.makeCurrent()
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
			self.canvas.updateCanvas( no_sim = self.previewing )
			self.preview.refresh()

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
		self.canvas.makeCurrent()
		self.canvas.safeCall( 'openScene', scene )
		self.scheduleUpdate()
		self.setFocus()
		# self.preview.update

	def onSceneClose( self, node ):
		self.window.setDocumentName( None )
		self.canvas.hide()
		self.canvas.makeCurrent()
		self.canvas.safeCall( 'closeScene' )

	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'view', 'onSelectionChanged', selection )

	def updateInPreview( self ):
		self.scheduleUpdate()
		introspector = self.getModule('introspector')
		if introspector:
			introspector.refresh()

	def onPreviewResume( self ):
		self.previewing = True
		self.previewUpdateTimer = self.window.startTimer( 3, self.updateInPreview )

	def onPreviewStop( self ):
		self.previewing = False
		self.previewUpdateTimer.stop()

	def scheduleUpdate( self ):
		self.updatePending = True

	def focusSelection( self ):
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'view', 'focusSelection' )


SceneView().register()
