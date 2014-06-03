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
from Command        import EditorCommandRegistry
from RemoteCommand  import RemoteCommandRegistry

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
		self.dataPaths     = []
		self.config        = {}
		self.packageManager   = PackageManager()

		self.commandRegistry       = EditorCommandRegistry.get()
		self.remoteCommandRegistry = RemoteCommandRegistry.get()
		
		self.registerDataPath( self.getPath('data') )

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
		
		#scan packages
		excludePackages = self.getProject().getConfig( 'excluded_packages' )
		self.packageManager.addExcludedPackage( excludePackages )

		self.packageManager.scanPackages( self.getPath( _GII_BUILTIN_PACKAGES_PATH ) )

		if self.getProject().isLoaded():
			self.packageManager.scanPackages( self.getProject().envPackagePath )

		#modules
		EditorModuleManager.get().loadAllModules()
		signals.emitNow( 'module.loaded' ) #some pre app-ready activities
		signals.dispatchAll()

		self.getProject().loadAssetLibrary()

		self.initialized = True
		self.running     = True

		signals.connect( 'app.remote', self.onRemote )

	def run( self, **kwargs ):
		if not self.initialized: self.init()
		sleepTime = kwargs.get( 'sleep', 0.005 )
		hasError = False
		try:
			EditorModuleManager.get().startAllModules()
			
			signals.emitNow('app.start')
			signals.dispatchAll()
			signals.emit('app.post_start')

			while self.running:
					self.doMainLoop( sleepTime )

		except Exception, e:
			#TODO: popup a alert window?
			logging.exception( e )
			hasError = True

		signals.emitNow('app.close')

		signals.dispatchAll()
		EditorModuleManager.get().stopAllModules()
		
		if not hasError:
			self.getProject().save()

		signals.dispatchAll()
		EditorModuleManager.get().unloadAllModules()

	def doMainLoop( self, sleepTime = 0.01 ):		
		EditorModuleManager.get().updateAllModules()
		if not signals.dispatchAll():
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

	def clearCommandStack( self, stackName ):
		stack = self.commandRegistry.getCommandStack( stackName )
		if stack:
			stack.clear()

	def doCommand( self, fullname, *args, **kwargs ):
		self.commandRegistry.doCommand( fullname, *args, **kwargs )

	def getPath( self, path = None ):
		if path:
			return self.basePath + '/' + path
		else:
			return self.basePath

	def findDataFile( self, fileName ):
		for path in self.dataPaths:
			f = path + '/' + fileName
			if os.path.exists( f ):
				return f
		return None

	def registerDataPath( self, dataPath ):
		self.dataPaths.append( dataPath )

	def getProject( self ):
		return Project.get()

	def openProject( self, basePath = None ):
		if self.projectLoaded: return Project.get()
		info = Project.findProject( basePath )
		if not info:
			raise Exception( 'no valid gii project found' )
		proj = Project.get()
		proj.load( info['path'] )
		self.projectLoaded = True
		self.registerDataPath( proj.getEnvPath('data') )
		return proj

	def getAssetLibrary( self ):
		return self.getProject().getAssetLibrary()
	
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

	def onRemote( self, data, output ):
		self.remoteCommandRegistry.doCommand( data, output )

app = EditorApp()
##----------------------------------------------------------------##

def _onRemoteArgument( data, output ):
		#warning: comes from another thread
		signals.emit( 'app.remote', data, output )

setRemoteArgumentCallback( _onRemoteArgument )