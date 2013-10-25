import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from DeviceManager        import DeviceManagerModule
from gii.qt.helpers       import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

import Device

class DeviceBrowser( DeviceManagerModule ):
	def getName( self ):
		return 'device_browser'

	def getDependency( self ):
		return [ 'device_manager' ]

	def onLoad( self ):		
		#UI
		self.windowTitle = 'Devices'
		self.window = self.requestDockWindow( 'DeviceBrowser',
			title     = 'Devices',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'left'
			)

		#Components
		self.tree = self.window.addWidget( 
			DeviceTreeWidget(
				self.window,
				multiple_selection = False,
				sorting            = True,
				editable           = False,
				drag_mode          = False
				)
			)

		self.tree.module = self

		self.tool = self.addToolBar( 'device_browser', self.window.addToolBar() )
		self.addTool( 'device_browser/refresh',    label = 'Refresh' )
		signals.connect( 'device.connected', self.onDeviceConnected )
		signals.connect( 'device.disconnected', self.onDeviceDisconnected )
		signals.connect( 'device.activated', self.onDeviceActivated )
		signals.connect( 'device.deactivated', self.onDeviceDeactivated )

		self.activeDevice = None

	def onStart( self ):
		self.tree.rebuild()

	def enumerateDevice( self ):
		return [ dev for dev in self.getDeviceManager().devices.keys() ]

	def onDeviceConnected( self, device ):
		self.tree.addNode( device )

	def onDeviceDisconnected( self, device ):
		self.tree.removeNode( device )		

	def onDeviceDeactivated( self, device ):
		self.tree.refreshNodeContent( device )

	def onDeviceActivated( self, device ):
		self.tree.refreshNodeContent( device )

	def onTool( self, tool ):
		name = tool.name
		if name == 'refresh':
			pass
			#TODO

##----------------------------------------------------------------##
class DeviceTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ( 'Name', 150 ), ( 'Act', 30 ), ( 'OS', 80 ) ]

	def getRootNode( self ):
		return self.module

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if node == self.module:
			return None
		return self.module

	def getNodeChildren( self, node ):
		if node == self.module:
			return self.module.enumerateDevice()
		return []

	def updateItemContent( self, item, node, **option ):
		if node == self.module: return
		item.setText( 0, node.getName() )
		item.setText( 1, node.isActive() and 'Y' or '' )
		item.setText( 2, node.getType() )

	def onDClicked( self, item, col ):
		device = item.node
		app.getModule('device_manager').setActiveDevice( device )
		
##----------------------------------------------------------------##
DeviceBrowser().register()
