import sys
import os

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.core import *

from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from QtEditorModule         import QtEditorModule

##----------------------------------------------------------------##
class QtSupportEventFilter(QObject):
	def eventFilter(self, obj, event):
		e=event.type()
		if e==QEvent.ApplicationActivate:			
			signals.emit('app.activate')
		elif e==QEvent.ApplicationDeactivate:
			signals.emit('app.deactivate')
		return QObject.eventFilter(self, obj,event)

##----------------------------------------------------------------##
class QtSupport( QtEditorModule ):
	def __init__( self ):
		pass

	def getName( self ):
		return 'qt'

	def getDependency( self ):
		return []

	def setupStyle( self ):
		# setup styles
		# QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
		try:
			styleSheetName = 'dark1.qss'
			self.qtApp.setStyleSheet(
					open( getAppPath( 'data/' + styleSheetName ) ).read() 
				)
		except Exception, e:
			# logging.info('style sheet not load',e)
			self.qtApp.setStyleSheet('''
				QWidget{
					font: 10pt;				
				}

				QMainWindow::Separator{
					width:4px;
					height:4px;
					border:1px solid #c9c9c9;
				}
				''')

	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow(None)
		self.mainWindow.setBaseSize( 800, 600 )
		self.mainWindow.resize( 800, 600 )
		self.mainWindow.setWindowTitle( 'GII' )
		self.mainWindow.app = self

		self.mainWindow.module = self
		self.menu = MenuManager.get().addMenuBar( 'main', self.mainWindow.menuBar(), self )

		# self.menu.addChild('&File').addChild([
		# 	'Open','E&xit'
		# 	]
		# )

	def onLoad( self ):
		self.qtApp   = QtGui.QApplication(sys.argv)

		eventFilter = QtSupportEventFilter( self.qtApp )
		eventFilter.app = self
		self.qtApp.installEventFilter(eventFilter)

		self.setupStyle()
		
		self.setupMainWindow()
		
		# self.rootWindow = QtGui.QMainWindow()
		# self.rootWindow.setFixedSize(0,0)
		# self.rootWindow.show()
		# self.rootWindow.raise_() #bring app to front
		# self.rootWindow.hide()
		# self.rootWindow.app = self

		self.containers  = {}
		self.initialized = True
		self.running     = False
		return True

	def start( self ):
		self.mainWindow.show()
		self.mainWindow.raise_()

	def update( self ):
		self.qtApp.processEvents( QEventLoop.AllEvents )

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


QtSupport().register()


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

