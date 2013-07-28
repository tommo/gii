from gii.core   import EditorModule

from gii.qt.controls.Window import MainWindow
from gii.qt.controls.Menu   import MenuManager

##----------------------------------------------------------------##
class QtEditorModule( EditorModule ):
	def getDependency( self ):
		return [ 'qt' ]

	def getQtSupport( self ):
		return self.getModule( 'qt' )
	
	def requestDockWindow( self, id, **windowOption ):
		qt = self.getModule( 'qt' )
		container = qt.requestDockWindow( id, windowOption )
		# self.containers[id] = container
		return container

	def requestSubWindow( self, id, **windowOption ):
		qt = self.getModule( 'qt' )
		container = qt.requestSubWindow( id, windowOption )
		# self.containers[id] = container
		return container

	def requestDocumentWindow( self, id, **windowOption ):
		qt = self.getModule( 'qt' )
		container = qt.requestDocumentWindow( id, windowOption )
		# self.containers[id] = container
		return container

	def setFocus(self):
		pass


	def setActiveWindow(self, window):
		qt = self.getQtSupport()
		qt.qtApp.setActiveWindow(window)

	#CONFIG
	def getQtSetting( self, name, default = None ):
		#TODO: fix this
		pass

	def setQtSetting( self, name, value ):
		#TODO: fix this
		pass

	#MENU CONTROL
	def addMenuBar( self, name, menubar ):
		node = MenuManager.get().addMenuBar(name, menubar, self)		
		return node

	def addMenu(self, path, opiton = None):
		node = MenuManager.get().addMenu(path, opiton, self)		
		return node

	def addMenuItem(self, path, option = None):
		node = MenuManager.get().addMenuItem(path, option, self)		
		if type(node) is list:
			for n in node:
				self.markRes(n)
		else:
			self.markRes(node)
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

	#WINDOW STATE
	def restoreWindowState(self, window, name=None):
		if not name:
			name=window.objectName() or 'window'
		geodata=self.getQtSetting('geom_'+name)
		if geodata:
			window.restoreGeometry(geodata)
		if hasattr(window,'restoreState'):
			statedata=self.getQtSetting('state_'+name)
			if statedata:
				window.restoreState(statedata)

	def saveWindowState(self, window, name=None):
		if not name:
			name=window.objectName() or 'window'
		self.setQtSetting('geom_'+name, window.saveGeometry())
		if hasattr(window,'saveState'):
			self.setQtSetting('state_'+name, window.saveState())
			
	def onMenu(self, menuItem):
		pass
