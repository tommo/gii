import os
import os.path
import logging
import time
import platform


import signals

import globalSignals
from EditorModule   import EditorModule, EditorModuleManager
from project        import Project
from package        import PackageManager
from MainModulePath import getMainModulePath
from selection      import SelectionManager
from Command        import EditorCommandRegistry

from InstanceHelper import checkSingleInstance, setRemoteArgumentCallback


_GII_BUILTIN_PACKAGES_PATH = 'packages'

class EditorApp(object):
	_singleton = None

	@staticmethod
	def get():
		return _singleton

	def __init__(self):
		assert(not EditorApp._singleton)
		EditorApp._singleton = self
		EditorModuleManager.get()._app = self

		self.initialized   = False
		self.projectLoaded = False
		self.flagModified  = False
		self.debugging     = False
		self.running       = False
		self.basePath      = getMainModulePath()

		self.config        = {}
		self.selectionManager = SelectionManager()
		self.packageManager   = PackageManager()
		self.commandRegistry  = EditorCommandRegistry()

		signals.connect( 'module.register', self.onModuleRegister )

	def onModuleRegister(self, m):		
		if self.running:
			logging.info('registered in runtime:'+m.getName())
			EditorModuleManager.get().loadModule(m)

	def init( self ):
		if not checkSingleInstance():
			raise Exception('running instance detected')

		if self.initialized: return
		self.openProject()
		
		setRemoteArgumentCallback( self.onRemoteArgument )
		#packages
		excludePackages = self.getProject().getConfig( 'excluded_packages' )
		self.packageManager.addExcludedPackage( excludePackages )
		self.packageManager.addPackagePath( self.getPath( _GII_BUILTIN_PACKAGES_PATH ) )
		if self.getProject().isLoaded():
			self.packageManager.addPackagePath( self.getProject().envPackagePath )
		self.packageManager.scanPackages()

		#modules
		EditorModuleManager.get().loadAllModules()
		signals.emitNow( 'module.loaded' ) #some pre app-ready activities
		signals.dispatchAll()

		self.initialized = True
		self.running     = True

	def run( self, **kwargs ):
		if not self.initialized: self.init()
		sleepTime = kwargs.get( 'sleep', 0.005 )
		EditorModuleManager.get().startAllModules()
		
		signals.emitNow('app.start')
		signals.dispatchAll()
		signals.emit('app.post_start')

		while self.running:
			self.doMainLoop( sleepTime )

		signals.emitNow('app.close')
		signals.dispatchAll()
		
		EditorModuleManager.get().stopAllModules()
		self.getProject().save()
		EditorModuleManager.get().unloadAllModules()

	def doMainLoop( self, sleepTime = 0.01 ):
		signals.dispatchAll()
		EditorModuleManager.get().updateAllModules()
		time.sleep( sleepTime )

	def stop( self ):
		self.running = False

	def setConfig( self, name, value ):
		self.config[name] = value

	def getConfig( self, name, default = None ):
		return self.config.get( name, default )

	def getModule(self, name):
		return EditorModuleManager.get().getModule( name )

	def affirmModule(self, name):
		return EditorModuleManager.get().affirmModule( name )

	def createCommandStack( self, stackName ):
		return self.commandRegistry.createCommandStack( stackName )

	def getCommandStack( self, stackName ):
		return self.commandRegistry.getCommandStack( stackName )

	def doCommand( self, fullname, *args, **kwargs ):
		self.commandRegistry.doCommand( fullname, *args, **kwargs )

	def getPath( self, path = None ):
		if path:
			return self.basePath + '/' + path
		else:
			return self.basePath

	def getProject( self ):
		return Project.get()

	def openProject( self ):
		if self.projectLoaded: return
		info = Project.findProject()
		if not info:
			raise Exception( 'no valid gii project found' )
		Project.get().load( info['path'] )
		self.projectLoaded = True

	def getAssetLibrary( self ):
		return self.getProject().getAssetLibrary()

	def getSelectionManager( self ):
		return self.selectionManager

	def isDebugging( self ):
		return False

	def getPlatformName( self ):
		name = platform.system()
		if name == 'Linux':
			return 'linux'
		elif name == 'Darwin':
			return 'osx'
		elif name == 'Windows':
			return 'win'
		else:
			raise Exception( 'what platform?' + name )

	def onRemoteArgument( self, data, output ):
		signals.emitNow( 'app.remote', data, output )
			
app = EditorApp()
