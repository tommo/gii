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
			if isinstance( dependency, str ):
				dependency = [ dependency ]
			m._dependency = dependency
			m._name       = name
			m.getDependency = lambda: dependency
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

	def getBaseDependency( self ):
		return [ 'gii' ]

	def getActualDependency( self ):
		return self.getDependency() + self.getBaseDependency()

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
		return self._app.doCommand( fullname, *args, **kwargs )

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
		dep=self.getActualDependency()
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
		for dep in self.getActualDependency():
			m = self.getModule( dep )
			if m: m.start()

		self.onStart()

	def stop( self ):
		if not self.active: return
		self.active = False
		for depModule in self.dependent:
			depModule.stop()
		self.onStop()

	def needUpdate( self ):
		return False
		
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

	def onAppReady( self ):
		pass
		
	def onStop( self ):
		pass


##----------------------------------------------------------------##
def _sortModuleIndex( m1, m2 ):
	diffIndex = m2.moduleIndex - m1.moduleIndex
	if diffIndex > 0 : return -1
	if diffIndex < 0 : return 1
	diffRegIndex = m2.regIndex - m1.regIndex
	if diffRegIndex > 0 : return -1
	if diffRegIndex < 0 : return 1
	return 0


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
		self.updatingModuleQueue = []
		self.sortedModuleQueue = []
		self.moduleChanged = False

	def getAllModules(self):
		return self.modules

	def loadModule( self, m, loadDep=True ):
		if m.alive: return True
		m.loading = True
		for n in m.getActualDependency():
			m1 = self.affirmModule(n)
			if m1 == m: continue
			if not m1.alive:
				if not loadDep:
					m.loading = False
					return False
				if m1.loading: 
					raise Exception('cyclic dependency:%s -> %s'%( m.getName(), m1.getName()) )
				self.loadModule( m1 )
			m1.dependent.append( m )

		m.load()
		m.loading=False
		signals.emit('module.load',m)
		return True

	def unloadModule( self, m ):
		self.moduleChanged = True
		if m.isDependentUnloaded():
			signals.emit('module.unload',m)
			m.unload()
			return True
		else:
			return False

	def loadAllModules(self):	
		queue = self.affirmSortedModuleQueue()
		for m in queue:
			self.loadModule( m )

	def updateAllModules( self ):
		for m in self.getUpdatingModuleQueue():
			if m.alive: 
				m.update()

	def startAllModules( self ):
		logging.info( 'start all modules' )
		for m in self.affirmSortedModuleQueue():
			if m.alive: m.start()
			
	def stopAllModules( self ):
		logging.info( 'stop all modules' )
		for m in self.affirmSortedModuleQueue():
			if m.alive: m.stop()

	def tellAllModulesAppReady( self ):
		logging.info( 'post start all modules' )
		for m in self.affirmSortedModuleQueue():
			if m.alive: 
				logging.info( 'app ready for module:' + m.getName() )
				m.onAppReady()

	def unloadAllModules(self):
		self.moduleChanged = True
		for m in reversed( self.affirmSortedModuleQueue() ):
			self.unloadModule( m )

	def registerModule( self, module, **option ):
		if not isinstance(module, EditorModule):
			raise Exception('Module expected, given:%s' % type(module))

		self.moduleChanged = True

		name = module.getName()
		if self.getModule(name): raise Exception('Module name duplicated:%s' % name)

		self.modules[name] = module
		self.moduleQueue.append(module)

		module._app      = self._app
		module._manager  = self

		module.regIndex    = len( self.moduleQueue ) - 1
		module.moduleIndex = None
		module.alive       = False
		module.active      = False
		module.loading     = False
		module.dependent   = []

		signals.emit( 'module.register', module )

	def unregisterModule(self, m):
		if m.alive:
			if m.isDependentUnloaded():
				self.moduleChanged = True
				m.unload()
				del self.modules[m.getName()]
				self.moduleQueue.remove(m)
				signals.emit( 'module.unregister', m )
			else:
				return False

	def getUpdatingModuleQueue( self ):
		return self.updatingModuleQueue

	def affirmSortedModuleQueue( self ):
		if self.moduleChanged:
			#clear moduleIndex
			for m in self.moduleQueue:
				m.moduleIndex = None
			modulesToSort = self.moduleQueue[ : ]
			while True:
				modulesNotSorted = []
				progressing = False
				for m in modulesToSort:
					newIndex = 0
					for depId in m.getActualDependency():
						depM = self.getModule( depId )
						if not depM:
							raise Exception( 'for %s, depencency module not found: %s' % ( m.getName(), depId ) )
						if depM == m: continue
						if depM.moduleIndex is None:
							newIndex = None
							break #dependency not calculated
						else:
							newIndex = max( newIndex, depM.moduleIndex + 1 )

					if newIndex is None:
						modulesNotSorted.append( m )
					else:
						m.moduleIndex = newIndex	
						progressing = True

				modulesToSort = modulesNotSorted
				if not modulesToSort:
					break

				if not progressing:
					print 'These modules may have cyclic dependency'
					for m in modulesToSort:
						print m.getName(), m.getActualDependency()
					raise Exception('Modules may have cyclic Dependency')

			self.sortedModuleQueue = sorted( self.moduleQueue, cmp = _sortModuleIndex )
			for m in self.sortedModuleQueue:
				if m.needUpdate():
					# if not m.__class__.update == EditorModule.update:
						# print 'update overrided', m.getName()
					# if not m.__class__.onUpdate == EditorModule.onUpdate:
						# print 'onUpdate overrided', m.getName()
					self.updatingModuleQueue.append( m )

			self.moduleChanged = False
			# for m in self.sortedModuleQueue:
			# 	print m.getName(), m.moduleIndex, m.regIndex	
		return self.sortedModuleQueue
	
	def getModule(self, name):
		return self.modules.get(name,None)

	def affirmModule( self, name ):
		m = self.getModule(name)
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