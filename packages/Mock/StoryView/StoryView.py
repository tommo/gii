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

from StoryWidget import StoryGraphView


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class StoryView( SceneEditorModule ):
	name       = 'story_view'
	dependency = [ 'mock' ]

	def onLoad( self ):
		self.window = self.requestDockWindow(
				title = 'Story'
			)
		self.toolbar = self.window.addToolBar()
		
		self.view = StoryGraphView()
		self.window.addWidget( self.view )

		self.updateTimer        = self.window.startTimer( 60, self.onUpdateTimer )
		self.updatePending      = False
		self.previewing         = False
		self.previewUpdateTimer = False		

	def onStart( self ):
		self.window.show()

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.window.show()
		self.window.setFocus()

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			#TODO
