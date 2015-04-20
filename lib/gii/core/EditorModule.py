from abc import ABCMeta, abstractmethod
import logging
import inspect
import sys
import os.path

from res     import *

import signals
from project import Project
from Command import EditorCommandRegistry


##----------------------------------------------------------------##
class EditorModuleMeta( ABCMeta ):
	def __init__( cls, name, bases, dict ):
		super( EditorModuleMeta, cls ).__init__( name, bases, dict )
		name       = dict.get( 'name', None )
		dependency = dict.get( 'dependency', [] )
		if name:
			m = cls()
			m._dependency = dependency
			m._name       = name
			EditorModuleManager.get().registerModule(	m )



##----------------------------------------------------------------##
## EDITORMODULE
##----------------------------------------------------------------##
class EditorModule( ResHolder ):
	__metaclass__ = EditorModuleMeta
	def __repr__(self):
		return '<module: %s>'%self.getName()

	def getDependency(self):
		return self._dependency or []

	def getName(self):		
		return self._name or '???'

	def getModulePath( self, path = None ):
		modName = self.__class__.__module__		
		m = sys.modules.get( modName, None )
		if m:			
			dirname = os.path.dirname( m.__file__ )
			if path:
				return dirname + '/' + path
			else:
				return dirname

	def register( self ):
		EditorModuleManager.get().registerModule( self )

	def getApp( self ):
		return self._app

	def findDataFile( self, fileName ):
		return self.getApp().findDataFile( filename )

	def doCommand( self, fullname, *args, **kwargs ):
		self._app.doCommand( fullname, *args, **kwargs )

	def getProject( self ):
		return Project.get()

	def getAssetLibrary( self ):
		return self.getProject().getAssetLibrary()
	
	def getManager(self):
		return self._manager

	def getModule(self, name):
		return self._manager.getModule(name)

	def affirmModule(self, name):
		return self._manager.affirmModule(name)

	def setConfig( self, name, value ):
		assert(isinstance(name, (str,unicode)))
		fullname = self.getName()+'/'+name
		self.getProject().setConfig( fullname, value )

	def getConfig( self, name, defaultValue=None ):
		assert( isinstance(name, (str,unicode)) )
		fullname = self.getName()+'/'+name
		return self.getProject().getConfig( fullname, defaultValue )

	def setAppConfig( self, name, value ):
		assert(isinstance(name, (str,unicode)))
		fullname = self.getName()+'/'+name
		self.getApp().setConfig( fullname, value )

	def getAppConfig( self, name, defaultValue=None ):
		assert( isinstance(name, (str,unicode)) )
		fullname = self.getName()+'/'+name
		return self.getApp().getConfig( fullname, defaultValue )
	
	def isDependencyReady(self):
		dep=self.getDependency()
		if not dep: return True

		manager=self.getManager()
		for name in dep:
			m = manager.affirmModule(name)
			if not getattr(m,'alive'): return False
		return True
	
	def isDependentUnloaded(self): #FIXME: use a clear name		
		dependent = self.dependent #added by manager
		for m in dependent:
			if m.alive: return False
		return True

	def load(self):
		logging.info('loading module:%s' % self.getName())
		self.onLoad()
		self.alive  = True
		
	def unload(self):
		logging.info('unloading module:%s' % self.getName())
		if self.active:
			self.stop()
		self.alive  = False
		self.releaseAll()
		self.onUnload()

	def start( self ):
		if self.active: return
		logging.info( 'starting module:' + self.getName() )
		self.active = True
		for dep in self.getDependency():
			m = self.getModule( dep )
			if m: m.start()

		self.onStart()

	def stop( self ):
		if not self.active: return
		self.active = False
		for depModule in self.dependent:
			depModule.stop()
		self.onStop()

	def update( self ):
		self.onUpdate()

	#Callbacks
	def onLoad(self):
		pass

	def onSerialize(self):
		pass

	def onDeserialize(self):
		pass

	def onUnload(self):
		pass

	def onUpdate(self):
		pass
	
	def onStart( self ):
		pass

	def onStop( self ):
		pass



##----------------------------------------------------------------##
## MODULE MANAGER
##----------------------------------------------------------------##
class EditorModuleManager(object):
	"""docstring for EditorModuleManager"""
	_singleton=None
	@staticmethod
	def get():
		return EditorModuleManager._singleton

	def __init__(self):
		assert not EditorModuleManager._singleton
		EditorModuleManager._singleton = self
		self.modules     = {}
		self.moduleQueue = []

	def getAllModules(self):
		return self.modules

	def loadModule( self, m, loadDep=True ):
		if m.alive: return True
		m.loading = True
		for n in m.getDependency():
			m1 = self.affirmModule(n)
			if not m1.alive:
				if not loadDep:
					m.loading = False
					return False
				if m1.loading: 
					raise Exception('cyclic dependency:%s -> %s'%(n.getName(), m1.getName()) )
				self.loadModule( m1 )
			m.dependent.append( m1 )
		m.load()
		m.loading=False
		signals.emit('module.load',m)
		return True

	def loadAllModules(self):	
		loaded=False
		while True:
			loaded=False
			for m in self.moduleQueue:
				if not m.alive:
					loaded=True
					if not self.loadModule(m): 
						raise Exception('Module not load:'+m.getName())
			if not loaded: return True

	def updateAllModules( self ):
		for m in self.moduleQueue:
			if m.alive: m.update()

	def startAllModules( self ):
		logging.info( 'start all modules' )
		for m in self.moduleQueue:
			if m.alive: m.start()
			
	def stopAllModules( self ):
		logging.info( 'stop all modules' )
		for m in self.moduleQueue:
			if m.alive: m.stop()

	def _loadModules(self):
		while True:
			loaded   = False
			needload = False
			for m in self.moduleQueue:
				if not m.alive:
					needload = True
					if m.isDependencyReady():
						m.load()
						signals.emit('module.load',m)
						loaded = True
			if not needload:
				return True
			if not loaded:
				for m in self.moduleQueue:
					m=self.modules[name]
					if not m.alive:
						print(m.getName())
				raise Exception('Cyclic Dependency')

	def unloadAllModules(self):
		while True:
			unloaded   = False
			needUnload = False
			for m in self.moduleQueue:
				if m.alive:
					needUnload=True
					if m.isDependentUnloaded():
						signals.emit('module.unload',m)
						m.unload()
						unloaded=True
			if not needUnload:
				break
			if not unloaded:
				for m in self.moduleQueue:
					if m.alive:
						print(m.getName())
				raise Exception('Cyclic Dependency')
		logging.info('modules unloaded' )

	def registerModule( self, module, **option ):
		if not isinstance(module, EditorModule):
			raise Exception('Module expected, given:%s' % type(module))

		name = module.getName()
		if self.getModule(name): raise Exception('Module name duplicated:%s' % name)

		self.modules[name] = module
		self.moduleQueue.append(module)

		module._app      = self._app
		module._manager  = self
		
		module.alive     = False
		module.active    = False
		module.loading   = False
		module.dependent = []

		signals.emit( 'module.register', module )

	def unregisterModule(self, m):
		if m.alive:
			if m.isDependentUnloaded():
				m.unload()
				del self.modules[m.getName()]
				self.moduleQueue.remove(m)
				signals.emit( 'module.unregister', m )
			else:
				return False
		
	def getModule(self, name):
		return self.modules.get(name,None)

	def affirmModule(self,name):
		m=self.getModule(name)
		if not m: raise Exception('Module not found: %s' %name)
		return m

EditorModuleManager()

##----------------------------------------------------------------##	
def registerEditorModule(m):
	EditorModuleManager.get().registerModule(m)

def unregisterEditorModule(m):
	EditorModuleManager.get().unregisterModule(m)

def getEditorModule(name):
	return EditorModuleManager.get().getModule(name)

def affirmEditorModule(name):
	return EditorModuleManager.get().affirmModule(name)