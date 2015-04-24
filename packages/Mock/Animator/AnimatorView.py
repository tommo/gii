import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                   import getIcon
from gii.qt.controls.GenericTreeWidget  import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule, getSceneSelectionManager
from gii.qt.helpers       import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##
from AnimatorWidget import AnimatorWidget
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
class AnimatorView( SceneEditorModule ):
	name = 'animator'
	dependency = [ 'scene_editor' ]
	def onLoad( self ):
		#UI
		self.windowTitle = 'Animator'
		self.window = self.requestDockWindow( 'AnimatorView',
			title     = 'Animator',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'bottom'
			)
		
		self.widget = AnimatorWidget()
		self.window.addWidget( self.widget )
		self.toolbarClips = self.addToolBar( 'animator_clips', self.widget.toolbarClips )
		self.toolbarPlay  = self.addToolBar( 'animator_play',  self.widget.toolbarPlay )
		# self.toolbarEdit  = self.addToolBar( 'animator_play',  self.widget.toolbarEdit )

		# addWidgetWithLaytut( toolbar,
		# 	self.widget.containerEditTool )
		self.addTool( 'animator_clips/add',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_clips/remove', label = 'remove', icon = 'remove' )


		self.addTool( 'animator_play/play',    label = 'play',    icon = 'play' )
		self.addTool( 'animator_play/stop',    label = 'stop',    icon = 'stop' )
		
		#SIGNALS

		#
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'AnimatorView.lua' ) )

	def onStart( self ):
		self.delegate.safeCall( 'setupTestData' )

	def onTool( self, tool ):
		name = tool.name
		if name == 'add':
			layer = self.delegate.safeCall( 'addLayer' )
			
		elif name == 'remove':
			for l in self.tree.getSelection():
				self.delegate.safeCall( 'removeLayer', l )
	
