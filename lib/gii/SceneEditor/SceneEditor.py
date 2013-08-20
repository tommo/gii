import os
import logging

from gii.core        import app, signals, EditorCommandStack
from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from gii.qt.QtEditorModule  import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt
##----------------------------------------------------------------##

from gii.moai.MOAIRuntime import MOAILuaDelegate
##----------------------------------------------------------------##

signals.register( 'entity.modified' )

##----------------------------------------------------------------##
class SceneEditor( QtEditorModule ):
	def __init__( self ):
		pass

	def getName( self ):
		return 'scene_editor'

	def getDependency( self ):
		return [ 'qt' ]

	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow(None)
		self.mainWindow.setBaseSize( 800, 600 )
		self.mainWindow.resize( 800, 600 )
		self.mainWindow.setWindowTitle( 'GII - Scene Editor' )
		self.mainWindow.setMenuWidget( self.getQtSupport().getSharedMenubar() )
		self.mainWindow.module = self
		
		self.mainToolBar = self.addToolBar( 'scene', self.mainWindow.requestToolBar( 'main' ) )		
		self.statusBar = QtGui.QStatusBar()
		self.mainWindow.setStatusBar(self.statusBar)

	def onLoad( self ):
		self.commands = self.createCommandStack( 'scene_editor' )

		self.setupMainWindow()
		self.containers  = {}

		#MainTool 
		self.addTool( 'scene/run',    label = 'Run' )
		self.addTool( 'scene/deploy', label = 'Deploy' )

		signals.connect( 'app.start', self.postStart )

		return True

	def postStart( self ):
		logging.info('opening up scene editor')
		self.mainWindow.show()
		self.mainWindow.setUpdatesEnabled( True )

	def onStart( self ):
		self.mainWindow.setUpdatesEnabled( False )
		self.restoreWindowState( self.mainWindow )
		
	def onStop( self ):
		self.saveWindowState( self.mainWindow )

	#controls
	def onSetFocus(self):
		self.mainWindow.show()
		self.mainWindow.raise_()
		self.mainWindow.setFocus()

	def startEdit( self, node ):
		logging.info( 'start edit scene' + repr( node ) )

	#resource provider
	def requestDockWindow( self, id, **dockOptions ):
		container = self.mainWindow.requestDockWindow(id, **dockOptions)		
		self.containers[id] = container
		return container

	def requestSubWindow( self, id, **windowOption ):
		container = self.mainWindow.requestSubWindow(id, **windowOption)		
		self.containers[id] = container
		return container

	def requestDocumentWindow( self, id, **windowOption ):
		container = self.mainWindow.requestDocuemntWindow(id, **windowOption)
		self.containers[id] = container
		return container

	def getMainWindow( self ):
		return self.mainWindow

	def onMenu(self, node):
		name = node.name

	def onTool( self, tool ):
		name = tool.name
		if name == 'run':
			from gii.core.tools import RunHost
			RunHost.run( 'main' )



##----------------------------------------------------------------##
class QtMainWindow( MainWindow ):
	"""docstring for QtMainWindow"""
	def __init__(self, parent,*args):
		super(QtMainWindow, self).__init__(parent, *args)
	
	def closeEvent(self,event):
		if self.module.alive:
			self.hide()
			event.ignore()
		else:
			pass

##----------------------------------------------------------------##
class SceneEditorModule( QtEditorModule ):
	def getMainWindow( self ):
		return self.getModule('scene_editor').getMainWindow()

##----------------------------------------------------------------##
SceneEditor().register()
