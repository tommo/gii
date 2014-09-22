import os
import logging

from gii.core        import app, signals, EditorCommandStack, RemoteCommand
from gii.core.selection import SelectionManager

from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from gii.qt.QtEditorModule  import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt, QObject
from PyQt4.QtGui    import QKeyEvent
##----------------------------------------------------------------##

##----------------------------------------------------------------##
class TopEditorModule( QtEditorModule ):
	def getWindowTitle( self ):
		return 'Top Level Editor'

	def getSelectionGroup( self ):
		return 'top'

	def setupMainWindow( self ):
		self.mainWindow = window = QtMainWindow(None)
		window.module = self
		window.setBaseSize( 800, 600 )
		window.resize( 800, 600 )
		window.setWindowTitle( 'GII - ' + self.getWindowTitle() )
		self.statusBar = QtGui.QStatusBar()
		window.setStatusBar( self.statusBar )
		self.onSetupMainWindow( window )

	def onSetupMainWindow( self, window ):
		pass
		# window.setMenuWidget( self.getQtSupport().getSharedMenubar() )
		# self.mainToolBar = self.addToolBar( 'scene', window.requestToolBar( 'main' ) )		

	def load( self ):
		self.commands = self._app.createCommandStack( self.getName() )
		self.selectionManager = SelectionManager( self.getSelectionGroup() )
		self.setupMainWindow()
		self.subWindowContainers  = {}
		return QtEditorModule.load( self )

	def onStart( self ):
		self.restoreWindowState( self.mainWindow )
		
	def onStop( self ):
		self.saveWindowState( self.mainWindow )

	#controls
	def onSetFocus(self):
		self.mainWindow.show()
		self.mainWindow.raise_()
		self.mainWindow.setFocus()

	#resource provider
	def requestDockWindow( self, id, **dockOptions ):
		container = self.mainWindow.requestDockWindow(id, **dockOptions)		
		self.subWindowContainers[id] = container
		return container

	def requestSubWindow( self, id, **windowOption ):
		container = self.mainWindow.requestSubWindow(id, **windowOption)		
		self.subWindowContainers[id] = container
		return container

	def requestDocumentWindow( self, id, **windowOption ):
		container = self.mainWindow.requestDocuemntWindow(id, **windowOption)
		self.subWindowContainers[id] = container
		return container

	def getMainWindow( self ):
		return self.mainWindow

	def onMenu(self, node):
		pass		

	def onTool( self, tool ):
		pass
		
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
class SubEditorModule( QtEditorModule ):
	def getParentModuleId( self ):
		return 'top_editor'

	def getParentModule( self ):
		return self.getModule( self.getParentModuleId() )

	def getMainWindow( self ):
		return self.getParentModule().getMainWindow()

	def getSelectionManager( self ):
		return self.getParentModule().selectionManager

	def getSelection( self ):
		return self.getSelectionManager().getSelection()

	def changeSelection( self, selection ):
		self.getSelectionManager().changeSelection( selection )

	def setFocus( self ):
		self.getMainWindow().raise_()
		self.getMainWindow().setFocus()
		self.onSetFocus()
