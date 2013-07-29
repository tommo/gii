import sys
import os


from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.core import *

from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from QtEditorModule         import QtEditorModule


_QT_SETTING_FILE = 'qt.ini'

##----------------------------------------------------------------##
class QtSupportEventFilter(QObject):
	def eventFilter(self, obj, event):
		e=event.type()
		if   e == QEvent.ApplicationActivate:			
			signals.emitNow('app.activate')
		elif e == QEvent.ApplicationDeactivate:
			signals.emitNow('app.deactivate')		
		return QObject.eventFilter(self, obj,event)

##----------------------------------------------------------------##
class QtSupport( QtEditorModule ):
	def __init__( self ):
		self.qtSetting = QtCore.QSettings(
					self.getProject().getConfigPath( _QT_SETTING_FILE ),
					QtCore.QSettings.IniFormat
				)

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
					open( self.getApp().getPath( 'data/' + styleSheetName ) ).read() 
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

<<<<<<< HEAD
	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow(None)
		self.mainWindow.setBaseSize( 800, 600 )
		self.mainWindow.resize( 800, 600 )
		self.mainWindow.setWindowTitle( 'GII - Asset Editor' )

		self.mainWindow.setFixedSize(0,0)
		self.mainWindow.show()
		self.mainWindow.raise_() #bring app to front
		self.mainWindow.hide()
		self.mainWindow.module = self

		self.sharedMenuBar = QtGui.QMenuBar( None )
		self.mainWindow.setMenuWidget( self.sharedMenuBar )
		
		self.menu = self.addMenuBar( 'main', self.sharedMenuBar )
		self.menu.addChild('&File').addChild([
			'Open',
			'E&xit'
			]
		)	

	def getSharedMenubar( self ):
		return self.sharedMenuBar
=======
>>>>>>> be2a9cf9d9cedce852a9937c9a908f21f3cd7cb7

	def onLoad( self ):
		self.qtApp   = QtGui.QApplication(sys.argv)

		eventFilter = QtSupportEventFilter( self.qtApp )
		eventFilter.app = self
		self.qtApp.installEventFilter(eventFilter)
		self.setupStyle()
		
		# self.setupMainWindow()
		
		self.rootWindow = QtGui.QMainWindow()
		self.rootWindow.setFixedSize(0,0)
		self.rootWindow.show()
		self.rootWindow.raise_() #bring app to front
		self.rootWindow.hide()
		self.rootWindow.app = self

		self.containers  = {}

		self.initialized = True
		self.running     = False
		return True

	def update( self ):
		self.qtApp.processEvents( QEventLoop.AllEvents )

	# #resource provider
	# def requestDockWindow( self, id, **dockOptions ):
	# 	pass

	# def requestSubWindow( self, id, **windowOption ):
	# 	pass

	# def requestDocumentWindow( self, id, **windowOption ):
	# 	pass

	def getMainWindow( self ):
		return self.rootWindow

	def getQtSettingObject( self ):
		return self.qtSetting

	def onMenu(self, node):
		name = node.name
		if name == 'exit':
			self.getApp().stop()

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
