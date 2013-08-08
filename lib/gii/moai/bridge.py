import logging
import json
import weakref

from gii.core   import *
from exceptions import *
from AKU        import _LuaTable, _LuaThread, _LuaObject, _LuaFunction
from time       import time as getTime


def wrapLuaCaller(func):
	def caller(*args):
			try:
				return func(*args)
			except Exception, e:
				logging.error( str(e) )
			return None
	return caller

####################################
#COMMON COMMUNICATION FUNCTIONS
####################################
_luaSignalConnections=[]
_luaSignalRegistration=[]

def emitPythonSignal(name, *args):	
	signals.emit(name, *args)

def emitPythonSignalNow(name, *args):	
	signals.emitNow(name, *args)

def connectPythonSignal(name, func):
	caller=wrapLuaCaller(func)
	signals.connect(name, caller)
	sig=signals.affirm(name)
	_luaSignalConnections.append((sig, caller))

def clearSignalConnections():
	global _luaSignalConnections
	for m in _luaSignalConnections:
		(sig , handler) = m
		sig.disconnect(handler)
	_luaSignalConnections=[]

def registerPythonSignal(name):
	signals.register(name)
	_luaSignalRegistration.append(name)

def clearLuaRegisteredSignals():
	global _luaSignalRegistration
	for name in _luaSignalRegistration:
		signals.unregister(name)

def throwPythonException(name, data=None):
	raise MOAIException(name)



####################################
#COMMAND BRIDGE
####################################
#todo
def changeSelection(targets=None):
	SelectionManager.get().changeSelection(targets)



####################################
#GUI BRIDGE
####################################
#todo
def GUIYield():
	app.doMainLoop()


####################################
#COMMON DATA BRIDGE
####################################
def fromUnicode(s, codec='utf-8'):
	if isinstance(s,unicode):
		return s.encode(codec)
	return s

def toUnicode(s, codec='utf-8'):
	if isinstance(s,str):
		return s.decode(codec)
	return s

def getDict( d, key, default=None ):
	return d.get( key, default )

def setDict( d, key, value ):
	d[key] = value

def decodeDict(data):
	return json.loads(data)

def encodeDict(dict):
	return json.dumps(dict).encode('utf-8')

def luaTableToDict(luat): #no deep conversion
	assert isinstance(luat , _LuaTable)
	res={}
	for k in luat:
		res[k]=luat[k]
	return res

def newPythonList(*arg):
	return list(arg)

def newPythonDict():
	return {}

def appendPythonList(list, data):
	list.append(data)

def deletePythonList(list, i):
	del list[i]

def sizeOfPythonObject(list):
	return len(list)


####################################
#MODEL BRIDGE
####################################
class LuaObjectModelProvider(ModelProvider):
	def __init__( self,  name, priority, getTypeId, getModel ):
		self.name = name
		self.priority = priority
		self._getTypeId = getTypeId
		self._getModel  = getModel

	def getPriority( self ):
		return self.priority

	def getTypeId( self, obj ):
		if isinstance( obj, _LuaObject ):
			return self._getTypeId( obj )
		else:
			return None

	def getModel( self, obj ):
		if isinstance( obj, _LuaObject ):
			return self._getModel( obj )
		else:
			return None

	def clear( self ):
		pass

class LuaObjectModel(ObjectModel):
	_EnumCache = weakref.WeakValueDictionary()
	def addLuaFieldInfo(self, name, typeId, data = None): #called by lua
		#convert lua-typeId -> pythontype
		typeId  = luaTypeToPyType( typeId )
		setting = data and luaTableToDict(data) or {}
		self.addFieldInfo( name, typeId, **setting )

	def addLuaEnumFieldInfo(self, name, enumItems, data = None): #called by lua
		enumType = LuaObjectModel._EnumCache.get( enumItems, None )
		if not enumType:
			tuples = []
			for item in enumItems.values():
				itemName  = item[1]
				itemValue = item[2]
				tuples.append ( ( itemName, itemValue ) )
			enumType = EnumType( '_LUAENUM_', tuples )
			LuaObjectModel._EnumCache[ enumItems ] = enumType
		return self.addLuaFieldInfo( name, enumType, data )


def luaTypeToPyType( tname ):
		if tname   == 'int':
			return int
		elif tname == 'string':
			return str
		elif tname == 'number':
			return float
		elif tname == 'boolean':
			return bool
		elif tname == 'nil':
			return None
		return tname #no conversion


class ModelBridge(object):
	_singleton=None

	@staticmethod
	def get():
		return ModelBridge._singleton

	def __init__(self):
		assert(not ModelBridge._singleton)
		ModelBridge._singleton=self
		self.modelProviders  = []
		self.registeredTypes = {}
		signals.connect( 'moai.clean', self.cleanLuaBridgeReference )

	def newLuaObjectMoel(self, name):
		return LuaObjectModel(name)

	def buildLuaObjectModelProvider( self, name, priority, getTypeId, getModel ):
		provider = LuaObjectModelProvider( name, priority, getTypeId, getModel )
		ModelManager.get().registerModelProvier( provider )
		self.modelProviders.append( provider )
		return provider

	def getTypeId(self, obj):
		return ModelManager.get().getTypeId(obj)

	def cleanLuaBridgeReference(self):
		#clean type getter
		for provider in self.modelProviders:
			logging.info( 'unregister provider:%s'% repr(provider) )
			provider.clear()
			ModelManager.get().unregisterModelProvider( provider )
		self.modelProviders = []


ModelBridge()
