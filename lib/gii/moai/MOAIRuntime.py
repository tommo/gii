import logging

from gii.core import signals, EditorModule

# from gii.core import Module, signals, getAppPath, unregisterModule, registerModule, App, Project

from AKU import getAKU, _LuaTable, _LuaThread, _LuaObject, _LuaFunction

from exceptions import *
from MOAIInputDevice import MOAIInputDevice
from LuaTableProxy   import LuaTableProxy

##----------------------------------------------------------------##
_G = LuaTableProxy( None )

signals.register( 'lua.msg' )
signals.register( 'moai.clean' )
signals.register( 'moai.reset' )
signals.register( 'moai.context.init' )

##----------------------------------------------------------------##
import bridge

##----------------------------------------------------------------##
## MOAIRuntime
##----------------------------------------------------------------##
class MOAIRuntime( EditorModule ):
	_singleton=None

	@staticmethod
	def get():
		return MOAIRuntime._singleton

	def __init__(self):
		assert not MOAIRuntime._singleton
		MOAIRuntime._singleton = self
		super(MOAIRuntime, self).__init__()		

		self.paused            = False
		self.GLContextReady    = False
		
		self.luaModules        = []
		self.luaDelegates      = {}

		self.inputDevices      = {}
		self.lastInputDeviceId = 0

	def getName(self):
		return 'moai.runtime'

	def getDependency(self):
		return []	

	#-------Context Control
	def initContext(self):
		global _G
		self.luaModules        = []

		self.inputDevices      = {}
		self.lastInputDeviceId = 0
		
		aku = getAKU()
		self.luaRuntime = None
		self.GLContextReady = False
		aku.resetContext()
		aku.setInputConfigurationName('GII')

		#inject python env
		lua = aku.getLuaRuntime()
		_G._setTarget( lua.globals() )
		_G['GII_PYTHON_BRIDGE']  = bridge
		_G['GII_DATA_PATH']      = self.getApp().getPath('data')
		logging.info( 'loading gii lua runtime' )
		aku.runScript(
			self.getApp().getPath( 'data/lua/runtime.lua' )
			)
		self.luaRuntime = lua.eval('gii')
		assert self.luaRuntime, "Failed loading Moei Lua Runtime!"
		#finish loading lua bridge
		
		self.AKUReady      = True
		self.RunningScript = False
		self.paused        = False
		
		getAKU().setFuncOpenWindow( self.onOpenWindow )

	def initGLContext( self ):
		if self.GLContextReady: return
		signals.emitNow( 'moai.context.init' )
		getAKU().detectGfxContext()
		self.GLContextReady = True

	def start( self ):
		self.initGLContext()

	def reset(self):
		if not self.AKUReady: return
		self.cleanLuaReferences()
		self.initContext()
		self.setWorkingDirectory( Project.get().getPath() )
		signals.emitNow('moai.reset')

	def onOpenWindow( self, title, w, h ):
		raise Exception( 'No GL context provided.' )

	#------Manual Control For MOAI Module
	#TODO: move function below into bridge module
	def syncAssetLibrary(self):
		self.luaRuntime.syncAssetLibrary()
		
	def stepSim(self, step):
		self.luaRuntime.stepSim(step)

	def setBufferSize(self, w,h):
	#for setting edit canvas size (without sending resize event)
		self.luaRuntime.setBufferSize(w,h) 

	def manualRenderAll(self):
		self.luaRuntime.manualRenderAll()

	def changeRenderContext(self, s):
		self.luaRuntime.changeRenderContext(s or False)

	def setCurrentRenderContextSize(self, w, h):
		self.luaRuntime.setCurrentRenderContextSize(w,h)

	def createRenderContext(self, s):
		self.luaRuntime.createRenderContext(s)

	#### Delegate Related
	def loadLuaDelegate( self, scriptPath , owner = None, **option ):
		if not option.get('forceReload', False): #find in cache first
			delegate = self.luaDelegates.get( scriptPath )
			if delegate: return delegate
		delegate = MOAILuaDelegate( owner )
		delegate.load( scriptPath )
		self.luaDelegates[ scriptPath ] = delegate
		return delegate

	def loadLuaWithEnv( self, file ):
		try:
			return self.luaRuntime.loadLuaWithEnv(file)
		except Exception, e:
			logging.error( 'error loading lua:\n' + str(e) )

	####  LuaModule Related
	def registerLuaModule(self, m):
		self.luaModules.append(m)
		registerModule(m)
	
	#clean holded lua object(this is CRITICAL!!!)
	def cleanLuaReferences(self):
		logging.info('clean lua reference')
		#clear lua module
		for m in self.luaModules:
			unregisterModule(m)

		bridge.clearSignalConnections()
		bridge.clearLuaRegisteredSignals()
		#clear lua object inside introspector
		introspector=self.getModule('introspector')
		if introspector:
			instances = introspector.getInstances()
			for ins in instances:
				if isinstance(ins.target,(_LuaTable, _LuaObject, _LuaThread, _LuaFunction)):
					ins.clear()

		signals.emitNow('moai.clean')

	#General Control
	def setWorkingDirectory(self, path):
		getAKU().setWorkingDirectory(path)

	def pause(self, paused=True):
		self.paused=paused
		getAKU().pause(self.paused)

	def resume(self):
		self.pause(False)
	
	def execConsole(self,command):
		self.runString(command)
		
	def updateAKU(self):
		if not self.AKUReady: return False
		if self.paused: return False		
		try:
			getAKU().update()
		except MOAIException as e:
			self.handleException(e)
			return False
		return True

	def renderAKU(self):
		if not self.AKUReady: return False
		try:
			getAKU().render()
		except MOAIException as e:
			self.handleException(e)
			return False
		return True

	def runScript(self,src):
		self.RunningScript=src
		try:
			getAKU().runScript(src)
		except MOAIException as e:
			self.handleException(e)
			return False
		return True

	def runString(self,string):		
		try:
			getAKU().runString(string)
		except MOAIException as e:
			self.handleException(e)
			return False
		return True

	def handleException(self,e):
		code=e.code
		if code=='TERMINATE':
			self.AKUReady=False
			self.RunningScript=False
		else:
			logging.error( 'error loading lua:\n' + str(e) )

	#Input Device Management
	def getInputDevice(self, name):
		return self.inputDevices.get(name,None)

	def addInputDevice(self, name):
		device = MOAIInputDevice(name, self.lastInputDeviceId)
		self.inputDevices[name] = device
		self.lastInputDeviceId += 1
		getAKU().reserveInputDevices(self.lastInputDeviceId)
		for k in self.inputDevices:
			self.inputDevices[k].onRegister()
		return device

	def addDefaultInputDevice(self, name='device'):
		device=self.addInputDevice(name)
		device.addSensor('touch',       'touch')
		device.addSensor('pointer',     'pointer')
		device.addSensor('keyboard',    'keyboard')
		device.addSensor('mouseLeft',   'button')
		device.addSensor('mouseRight',  'button')
		device.addSensor('mouseMiddle', 'button')
		device.addSensor('level',       'level')
		device.addSensor('compass',     'compass')
		return device

	#----------
	def onLoad(self):
		self.AKUReady = False
		signals.connect ( 'project.preload', self.onProjectPreload )
		signals.tryConnect ( 'console.exec', self.execConsole )
		self.initContext()

	def onUnload(self):
		self.cleanLuaReferences()
		self.luaRuntime = None
		self.AKUReady   = False
		pass

	def onProjectPreload(self, prj):
		self.setWorkingDirectory(prj.getPath())



##----------------------------------------------------------------##
## Delegate
##----------------------------------------------------------------##
class MOAILuaDelegate(object):
	def __init__(self, owner=None, **option):
		self.scriptPath   = None
		self.owner        = owner
		self.extraSymbols = {}
		self.clearLua()
		signals.connect('moai.clean', self.clearLua)
		if option.get('autoReload',True):
			signals.connect('moai.reset', self.reload)

	def load(self, scriptPath):
		self.scriptPath = scriptPath
		runtime = MOAIRuntime.get()
		try:
			self.luaEnv = runtime.loadLuaWithEnv(scriptPath)
			if self.luaEnv:
				self.luaEnv['_owner']    = self.owner
				self.luaEnv['_delegate'] = self
		except Exception, e:
			print(e)


	def reload(self):
		if self.scriptPath: 
			self.load(self.scriptPath)
			for k,v in self.extraSymbols.items():
				self.setEnv(k,v)

	def setEnv(self, name ,value, autoReload=True):
		if autoReload : self.extraSymbols[name] = value
		self.luaEnv[name] = value

	def getEnv(self, name, defaultValue=None):
		v = self.luaEnv[name]
		if v is None : return defaultValue
		return v

	def safeCall(self, method, *args):
		if not self.luaEnv: return
		m = self.luaEnv[method]
		if m: return m(*args)

	def call(self, method, *args):
		m = self.luaEnv[method]
		return m(*args)

	def clearLua(self):
		self.luaEnv=None

MOAIRuntime().register()
