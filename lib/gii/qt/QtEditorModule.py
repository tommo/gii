from abc        import ABCMeta, abstractmethod

from gii.core   import EditorModule

from gii.qt.controls.Menu      import MenuManager
from gii.qt.controls.ToolBar   import ToolBarManager, ToolBarNode

##----------------------------------------------------------------##
_QT_SETTING_FILE = 'qt.ini'

##----------------------------------------------------------------##
class QtEditorModule( EditorModule ):
	__metaclass__ = ABCMeta

	@abstractmethod
	def getMainWindow( self ):
		return None

	def getDependency( self ):
		return [ 'qt' ]

	def getQtSupport( self ):
		return self.getModule( 'qt' )

	def requestDockWindow( self, id = None, **windowOption ):
		if not id: id = self.getName()
		mainWindow = self.getMainWindow()
		container = mainWindow.requestDockWindow( id, **windowOption )
		# self.containers[id] = container
		return container

	def requestSubWindow( self, id = None, **windowOption ):
		if not id: id = self.getName()
		mainWindow = self.getMainWindow()
		container = mainWindow.requestSubWindow( id, **windowOption )
		# self.containers[id] = container
		return container

	def requestDocumentWindow( self, id = None, **windowOption ):
		if not id: id = self.getName()
		mainWindow = self.getMainWindow()
		container = mainWindow.requestDocumentWindow( id, **windowOption )
		# self.containers[id] = container
		return container

	def setFocus(self):
		self.onSetFocus()

	def setActiveWindow( self, window ):
		qt = self.getQtSupport()
		qt.qtApp.setActiveWindow(window)

	#CONFIG
	def getQtSettingObject( self ):
		return self.getQtSupport().getQtSettingObject()		

	def setQtSetting( self, name, value ):
		name = 'modules/%s/%s' % (self.getName(), name)
		self.setGlobalQtSetting( name, value )

	def getQtSetting( self, name, default = None ):
		name = 'modules/%s/%s' % (self.getName(), name)
		return self.getGlobalQtSetting( name, default )
		
	def setGlobalQtSetting( self, name, value, **kwarg ):		
		setting = self.getQtSettingObject()
		setting.setValue(name, value)
		setting.sync()

	def getGlobalQtSetting( self, name, default = None, **kwarg ):
		setting = self.getQtSettingObject()		
		v = setting.value(name)
		if v is None: return default
		return v

	#MENU CONTROL
	def addMenuBar( self, name, menubar ):
		node = MenuManager.get().addMenuBar(name, menubar, self)		
		return node

	def addMenu(self, path, opiton = None):
		node = MenuManager.get().addMenu(path, opiton, self)		
		return node

	def addMenuItem(self, path, option = None):
		node = MenuManager.get().addMenuItem( path, option, self )
		return node

	def findMenu(self, path):
		node=MenuManager.get().find(path)
		return node

	def disableMenu(self,path):
		self.enableMenu(path, False)

	def enableMenu(self,path, enabled=True):
		node=self.findMenu(path)
		if not node:
			raise Exception('Menuitem not found:'+path)
		node.setEnabled(enabled)

	def checkMenu(self,path,checked=True):
		node=self.findMenu(path)
		if not node:
			raise Exception('Menuitem not found:'+path)
		node.setValue(checked)

	#TOOLBar control
	def addToolBar( self, name, toolbar ):
		node = ToolBarManager.get().addToolBar(name, toolbar, self)		
		return node

	def addTool(self, path, **opiton ):
		node = ToolBarManager.get().addTool( path, opiton, self )
		return node

	def findTool(self, path):
		node = ToolBarManager.get().find(path)
		return node

	def disableTool(self,path):
		self.enableTool(path, False)

	def enableTool(self,path, enabled=True):
		node = self.findTool(path)
		if not node:
			raise Exception('tool/toolbar not found:'+path)
		node.setEnabled(enabled)

	def checkTool(self,path,checked=True):
		node=self.findTool(path)
		if not node:
			raise Exception('tool/toolbar not found:'+path)
		node.setValue(checked)


	#WINDOW STATE
	def restoreWindowState(self, window, name=None):
		if not name:
			name  = window.objectName() or 'window'
		geodata = self.getQtSetting('geom_'+name)
		if geodata:
			window.restoreGeometry( geodata )
		if hasattr( window, 'restoreState' ):
			statedata = self.getQtSetting('state_'+name)
			if statedata:
				window.restoreState(statedata)

	def saveWindowState(self, window, name=None):
		if not name:
			name = window.objectName() or 'window'
		self.setQtSetting( 'geom_' + name, window.saveGeometry())
		if hasattr(window,'saveState'):
			self.setQtSetting( 'state_' + name, window.saveState())
			
	def onMenu(self, menuItem):
		pass

	def onTool(self, toolItem):
		pass

	def onSetFocus(self):
		pass

