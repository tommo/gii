import os
import logging

from gii.core        import app, signals, EditorCommandStack, RemoteCommand
from gii.core.selection import SelectionManager

from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from gii.qt  import TopEditorModule, SubEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt, QObject
from PyQt4.QtGui    import QKeyEvent
##----------------------------------------------------------------##

from gii.moai.MOAIRuntime import MOAILuaDelegate


##----------------------------------------------------------------##
class SceneEditorModule( SubEditorModule ):
	def getParentModuleId( self ):
		return 'scene_editor'

	def getSceneEditor( self ):
		return self.getParentModule()

##----------------------------------------------------------------##
class SceneEditor( TopEditorModule ):
	name       = 'scene_editor'
	dependency = ['qt']

	def getSelectionGroup( self ):
		return 'scene'

	def getWindowTitle( self ):
		return 'Scene Editor'
	
	def onSetupMainWindow( self, window ):
		self.mainToolBar = self.addToolBar( 'scene', self.mainWindow.requestToolBar( 'main' ) )		
		window.setMenuWidget( self.getQtSupport().getSharedMenubar() )
		#MainTool 
		self.addTool( 'scene/run',    label = 'Run' )
		self.addTool( 'scene/deploy', label = 'Deploy' )
		#menu
		self.addMenu( 'main/scene', dict( label = 'Scene' ) )

	def onLoad( self ):
		signals.connect( 'app.start', self.postStart )
		return True

	def postStart( self ):
		logging.info('opening up scene editor')
		self.mainWindow.show()
		# self.mainWindow.setUpdatesEnabled( True )

	def onMenu(self, node):
		name = node.name
		if name == 'open_scene':
			#TODO
			pass

	def onTool( self, tool ):
		name = tool.name
		if name == 'run':
			from gii.core.tools import RunHost
			RunHost.run( 'main' )
			
		elif name == 'deploy':
			deployManager = self.getModule('deploy_manager')
			if deployManager:
				deployManager.setFocus()

##----------------------------------------------------------------##
def getSceneSelectionManager():
	return app.getModule('scene_editor').selectionManager


##----------------------------------------------------------------##
class RemoteCommandRunGame( RemoteCommand ):
	name = 'run_game'
	def run( self, target = None, *args ):
		from gii.core.tools import RunHost
		RunHost.run( 'main' )
