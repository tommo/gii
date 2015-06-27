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

from StoryGraphView import StoryGraphView


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class StoryView( SceneEditorModule ):
	name       = 'story_view'
	dependency = [ 'mock' ]

	def onLoad( self ):
		self.container = self.requestDocumentWindow(
				title = 'Story'
			)
		self.window = window = self.container.addWidgetFromFile(
			_getModulePath('StoryView.ui')
		)
		self.view = StoryGraphView( window.containerGraph )
		addWidgetWithLayout( self.view )

		self.updateTimer        = self.container.startTimer( 60, self.onUpdateTimer )
		self.updatePending      = False
		self.previewing         = False
		self.previewUpdateTimer = False		

	def onStart( self ):
		self.container.show()
		# pass

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.container.show()
		self.container.setFocus()

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			#TODO
