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


class EditCanvasTest( SceneEditorModule ):
	def getName( self ):
		return 'editor_canvas_test'

	def getDependency( self ):
		return ['mock']

	def onLoad( self ):
		self.window = self.requestDocumentWindow()
		self.canvas = self.window.addWidget( MOAIEditCanvas() )
		self.canvas.loadScript( _getModulePath('test.lua') )

	def onStart( self ):
		self.window.show()
		self.canvas.makeCurrent()
		self.canvas.safeCall( 'onStart' )

EditCanvasTest().register()