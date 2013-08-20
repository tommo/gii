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
		self.updateTimer = self.window.startTimer( 60, self.onUpdateTimer )
		signals.connect( 'entity.modified', self.onEntityModified )
		self.updatePending = False
		self.preview = self.getModule( 'scene_preview' )

	def onStart( self ):
		self.canvas.makeCurrent()
		self.scheduleUpdate()

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			self.canvas.updateCanvas()
			self.preview.refresh()

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.window.show()
		self.window.setFocus()

	def onEntityModified( self, entity ):
		self.scheduleUpdate()

	def openScene( self, node ):
		self.window.setDocumentName( node.getPath() )
		
		self.canvas.makeCurrent()
		self.canvas.safeCall( 'openScene', node.getPath() )
		scene = self.canvas.safeCall( 'getScene' )
		self.getModule( 'scenegraph_editor' ).addScene( scene )
		self.scheduleUpdate()
		self.setFocus()

	def scheduleUpdate( self ):
		self.updatePending = True

SceneView().register()