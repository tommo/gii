import os
import stat

from gii.core import *

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QEventLoop, QEvent, QObject

from gii.qt.IconCache       import getIcon
from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager
from gii.qt.QtEditorModule  import QtEditorModule

from gii.SearchView       import requestSearchView, registerSearchEnumerator

import MobileDevice
from   MonitorThread import DeviceMonitorThread

##----------------------------------------------------------------##
# def getIOSDeviceName( dev ):
# 	name = u''
# 	try:
# 		name = dev.get_value(name=u'DeviceName')
# 	except:
# 		pass
# 	print( u'%s - "%s"' % ( dev.get_deviceid(), name.decode(u'utf-8') ) )


signals.register( 'device.connected' )
signals.register( 'device.disconnected' )

##----------------------------------------------------------------##
class DeviceManagerModule( QtEditorModule ):
	def getDeviceManager( self ):
		return self.getModule('device_manager')

	def getMainWindow( self ):
		return self.getModule('device_manager').getMainWindow()

	def getSelectionManager( self ):
		selectionManager = self.getDeviceManager().selectionManager
		return selectionManager

	def getSelection( self ):
		return self.getSelectionManager().getSelection()

	def changeSelection( self, selection ):
		self.getSelectionManager().changeSelection( selection )


##----------------------------------------------------------------##		
class DeviceManager( DeviceManagerModule ):
	def __init__( self ):
		pass
		
	def getName( self ):
		return 'device_manager'

	def getDependency( self ):
		return ['qt']

	def getMainWindow( self ):
		return self.mainWindow

	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow(None)
		self.mainWindow.setBaseSize( 600, 400 )
		self.mainWindow.resize( 600, 400 )
		self.mainWindow.setWindowTitle( 'GII - Device Manager' )
		self.mainWindow.setMenuWidget( self.getQtSupport().getSharedMenubar() )

		self.mainWindow.module = self

		self.statusBar = QtGui.QStatusBar()
		self.mainWindow.setStatusBar(self.statusBar)

		self.mainToolBar = self.addToolBar( 'device', self.mainWindow.requestToolBar( 'main' ) )

		####
		self.addMenu('main/device', {'label':'&Device'})

	def onLoad( self ):
		self.setupMainWindow()
		self.containers  = {}
		self.devices     = {}
		signals.connect( 'app.start', self.postStart )
		registerSearchEnumerator( deviceSearchEnumerator )
		
	def postStart( self ):
		self.mainWindow.show()
		self.mainWindow.raise_()

	def onStart( self ):
		self.restoreWindowState( self.mainWindow )
		self.monitorThread = DeviceMonitorThread( self.onIOSDeviceEvent )
		# self.monitorThread.start()
	
	def onStop( self ):
		# self.monitorThread.stop()
		self.saveWindowState( self.mainWindow )

	def onIOSDeviceEvent( self, ev, device ):
		if ev == 'connected':
			name = ''
			try:
				name = device.get_value( name = u'DeviceName' )
			except:
				pass
			device.name = name
			signals.emit( 'device.connected', device )
			self.devices[ device ] = True
		elif ev == 'disconnected':
			signals.emit( 'device.disconnected', device )
			self.devices[ device ] = False

	def setFocus(self):
		self.mainWindow.show()
		self.mainWindow.raise_()
		self.mainWindow.setFocus()

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
		# name = node.name
		pass

	def onTool( self, tool ):
		pass
		
DeviceManager().register()


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
def deviceSearchEnumerator( typeId, context ):
		if not context in [ 'device' ]: return
		result = []
		dm = app.getModule( 'device_manager' )
		for device in dm.enumerateDevice():
			entry = ( device, device.getName(), device.getType(), None )
			result.append( entry )
		return result

##----------------------------------------------------------------##
