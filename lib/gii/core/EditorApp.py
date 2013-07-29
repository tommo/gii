import os
import os.path
import logging
import time

import signals

import globalSignals
from EditorModule   import EditorModule, EditorModuleManager
from project        import Project
from package        import PackageManager
from MainModulePath import getMainModulePath
from selection      import SelectionManager

from InstanceHelper import checkSingleInstance

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
		self.flagModified  = False
		self.debugging     = False
		self.running       = False
		self.basePath      = getMainModulePath()

		self.config        = {}
		self.selectionManager = SelectionManager()
		self.packageManager   = PackageManager()

		signals.connect( 'module.register', self.onModuleRegister )

	def onModuleRegister(self, m):		
		if self.running:
			logging.info('registered in runtime:'+m.getName())
			EditorModuleManager.get().loadModule(m)

	def init( self ):
		if not checkSingleInstance():
			raise Exception('running instance detected')

		if self.initialized: return
		
		#packages
		self.packageManager.addPackagePath( self.getPath( _GII_BUILTIN_PACKAGES_PATH ) )
		if self.getProject().isLoaded():
			self.packageManager.addPackagePath( self.getProject().envPackagePath )
		self.packageManager.scanPackages()

		#modules
		EditorModuleManager.get().loadAllModules()
		signals.emitNow('module.loaded') #some pre app-ready activities
		signals.dispatchAll()

		self.initialized = True
		self.running     = True

	def run( self, **kwargs ):
		if not self.initialized: self.init()
		sleepTime = kwargs.get( 'sleep', 0.002 )
		EditorModuleManager.get().startAllModules()
		signals.emitNow('app.start')

		while self.running:
			self.doMainLoop( sleepTime )

		signals.emitNow('app.close')
		signals.dispatchAll()
		EditorModuleManager.get().stopAllModules()
		self.getProject().save()
		EditorModuleManager.get().unloadAllModules()

	def doMainLoop( self, sleepTime = 0.002 ):
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

	def getPath( self, path = None ):
		if path:
			return self.basePath + '/' + path
		else:
			return self.basePath

	def getProject( self ):
		return Project.get()

	def openProject( self ):
		path = Project.findProject()
		if not path:
			raise Exception( 'no valid gii project found' )
		Project.get().load( path )

	def getAssetLibrary( self ):
		return self.getProject().getAssetLibrary()

	def getSelectionManager( self ):
		return self.selectionManager

app = EditorApp()
