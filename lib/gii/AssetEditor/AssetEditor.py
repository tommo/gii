import sys
import os

from gii.core import *
from gii.core.selection import SelectionManager

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.qt.IconCache       import getIcon
from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from gii.qt.QtEditorModule  import QtEditorModule

import gii.FileWatcher
from gii.SearchView       import requestSearchView, registerSearchEnumerator



##----------------------------------------------------------------##
class AssetEditorModule( QtEditorModule ):
	def getAssetEditor( self ):
		return self.getModule('asset_editor')

	def getMainWindow( self ):
		return self.getModule('asset_editor').getMainWindow()

	def getSelectionManager( self ):
		selectionManager = self.getAssetEditor().selectionManager
		return selectionManager

	def getSelection( self ):
		return self.getSelectionManager().getSelection()

	def changeSelection( self, selection ):
		self.getSelectionManager().changeSelection( selection )

		
##----------------------------------------------------------------##
class AssetEditor( AssetEditorModule ):
	name       = 'asset_editor'
	dependency = ['qt']

	def __init__( self ):
		self.selectionManager = SelectionManager( 'asset' )
		self.projectScanScheduled = False

	def getMainWindow( self ):
		return self.mainWindow

	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow(None)
		self.mainWindow.setBaseSize( 800, 600 )
		self.mainWindow.resize( 800, 600 )
		self.mainWindow.setWindowTitle( 'GII - Asset Editor' )
		self.mainWindow.setMenuWidget( self.getQtSupport().getSharedMenubar() )

		self.mainWindow.module = self

		self.statusBar = QtGui.QStatusBar()
		self.mainWindow.setStatusBar(self.statusBar)

		self.mainToolBar = self.addToolBar( 'asset', self.mainWindow.requestToolBar( 'main' ) )

		####
		self.addMenu('main/asset', {'label':'&Asset'})
		self.addMenuItem(
			'main/asset/reset_all_asset', 
			dict( label='Reset Asset Library' )
		)
		self.addMenuItem(
			'main/asset/clear_free_meta', 
			dict( label='Clear Metadata' )
		)
		
		self.projectScanTimer = self.mainWindow.startTimer( 1, self.checkProjectScan )
		

	def onLoad( self ):
		self.setupMainWindow()
		self.containers  = {}
		signals.connect( 'app.start', self.postStart )
		registerSearchEnumerator( assetSearchEnumerator )
		
	def postStart( self ):
		logging.info('opening up asset editor')
		# self.mainWindow.setUpdatesEnabled( True )
		self.mainWindow.show()
		self.mainWindow.raise_()

	def onStart( self ):
		# self.mainWindow.setUpdatesEnabled( False )
		self.restoreWindowState( self.mainWindow )
	
	def onStop( self ):
		self.saveWindowState( self.mainWindow )

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

	##
	def checkProjectScan( self ):
		lib = self.getAssetLibrary()
		if lib.projectScanScheduled:
			lib.scanProject()

	##
	def onMenu(self, node):
		name = node.name
		if name == 'reset_all_asset':
			self.getAssetLibrary().reset()
		elif name == 'clear_free_meta':
			self.getAssetLibrary().clearFreeMetaData()
		
	def onTool( self, tool ):
		print tool.name

		

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
def getAssetSelectionManager():
	return app.getModule('asset_editor').selectionManager


##----------------------------------------------------------------##
def assetSearchEnumerator( typeId, context ):
		if not context in [ 'all', 'asset' ] : return
		result = []
		lib = AssetLibrary.get()
		for node in AssetLibrary.get().enumerateAsset( typeId ):
			assetType = node.getType()
			iconName = lib.getAssetIcon( assetType ) or 'normal'
			entry = ( node, node.getNodePath(), node.getType(), iconName )
			result.append( entry )
		return result
