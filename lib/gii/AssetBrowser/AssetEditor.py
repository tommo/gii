import sys
import os

from gii.core import *

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from gii.qt.QtEditorModule  import QtEditorModule

##----------------------------------------------------------------##
class AssetEditor( QtEditorModule ):
	def __init__( self ):
		pass

	def getName( self ):
		return 'asset_editor'

	def getDependency( self ):
		return ['qt']

	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow(None)
		self.mainWindow.setBaseSize( 800, 600 )
		self.mainWindow.resize( 800, 600 )
		self.mainWindow.setWindowTitle( 'GII - Asset Editor' )

		self.mainWindow.module = self
		
		self.menu = self.addMenuBar( 'asset', self.mainWindow.menuBar() )
		self.menu.addChild('&File').addChild([
			'Open','E&xit'
			]
		)

	def onLoad( self ):
		self.setupMainWindow()
		self.containers  = {}
		return True

	def onStart( self ):
		self.mainWindow.show()
		self.mainWindow.raise_()
	
	#controls
	def setFocus(self):
		self.mainWindow.show()
		self.mainWindow.raise_()
		self.mainWindow.setFocus()

	#resource provider
	def requestDockWindow( self, id, dockOptions ):
		container = self.mainWindow.requestDockWindow(id, dockOptions)		
		self.containers[id] = container
		return container

	def requestSubWindow( self, id, windowOption ):
		container = self.mainWindow.requestSubWindow(id, windowOption)		
		self.containers[id] = container
		return container

	def requestDocumentWindow( self, id, windowOption ):
		container = self.mainWindow.requestDocuemntWindow(id, windowOption)
		self.containers[id] = container
		return container

	def getMainWindow( self ):
		return self.mainWindow

	def onMenu(self, node):
		name = node.name
		if name == 'exit':
			self.getApp().stop()


AssetEditor().register()


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

