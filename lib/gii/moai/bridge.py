import logging
import json
import weakref

from gii.core   import *

from gii.core.selection   import getSelectionManager

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
#GUI BRIDGE
####################################
#todo
def GUIYield():
	app.doMainLoop()

def getSelection( key ):
	selectionManager = getSelectionManager( key )
	s = selectionManager.getSelection()
	return s

def changeSelection( key, targets = None ):
	selectionManager = getSelectionManager( key )
	selectionManager.changeSelection( targets )

####################################
#COMMON DATA BRIDGE
####################################
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
		v = luat[k]
		if isinstance( v, _LuaTable ):
			v = luaTableToDict( v )
		res[k] = v
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

def tupleToList( t ):
	return list( t )

####################################
#MODEL BRIDGE
####################################
class LuaObjectModelProvider(ModelProvider):
	def __init__( self,  name, priority, getTypeId, getModel, getModelFromTypeId ):
		self.name        = name
		self.priority    = priority

		self._getTypeId          = getTypeId
		self._getModel           = getModel
		self._getModelFromTypeId = getModelFromTypeId

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

	def getModelFromTypeId( self, typeId ):
		return self._getModelFromTypeId( typeId )

	def getPriority( self ):
		return 1

	def clear( self ):
		pass

##----------------------------------------------------------------##
class LuaObjectEnumerator( ObjectEnumerator ):
	def __init__( self, name, enumerateObject, getObjectRepr, getObjectTypeRepr ):
		self.name     = name
		self._enumerateObject    = enumerateObject
		self._getObjectTypeRepr  = getObjectTypeRepr
		self._getObjectRepr      = getObjectRepr

	def getName( self ):
		return self.name

	def enumerateObjects( self, typeId, context ):
		result = self._enumerateObject( self, typeId, context )
		if not result: return None
		return [ obj for obj in result.values() ]			

	def getObjectRepr( self, obj ):
		return self._getObjectRepr( self, obj )

	def getObjectTypeRepr( self, obj ):
		return self._getObjectTypeRepr( self, obj )

##----------------------------------------------------------------##
class LuaObjectModel(ObjectModel):
	_EnumCache = weakref.WeakValueDictionary()
	_AssetTypeCache = {}

	def addLuaFieldInfo(self, name, typeId, data = None): #called by lua
		#convert lua-typeId -> pythontype
		typeId  = luaTypeToPyType( typeId )
		setting = data and luaTableToDict(data) or {}
		meta = setting.get('meta',None)
		if meta:
			del setting['meta']
			for k, v in meta.items():
				if not setting.has_key( k ):
					setting[k] = v
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

	def addLuaAssetFieldInfo(self, name, assetType, data = None): #called by lua
		typeId = LuaObjectModel._AssetTypeCache.get( assetType )
		if not typeId:
			typeId = AssetRefType( assetType )
			LuaObjectModel._AssetTypeCache[ assetType ] = typeId
		return self.addLuaFieldInfo( name, typeId, data )

	def serialize( self, obj, objMap = None ):
		raise Exception('Serializing Lua object in python is not supported, yet')

	def deserialize( self, obj, data, objMap = None ):
		raise Exception('Deserializing Lua object in python is not supported, yet')


##----------------------------------------------------------------##
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

##----------------------------------------------------------------##
class ModelBridge(object):
	_singleton=None

	@staticmethod
	def get():
		return ModelBridge._singleton

	def __init__(self):
		assert(not ModelBridge._singleton)
		ModelBridge._singleton=self
		self.modelProviders   = []
		self.enumerators      = []		
		self.registeredTypes  = {}
		signals.connect( 'moai.clean', self.cleanLuaBridgeReference )

	def newLuaObjectMoel(self, name):
		return LuaObjectModel(name)

	def buildLuaObjectModelProvider( self, name, priority, getTypeId, getModel, getModelFromTypeId ):
		provider = LuaObjectModelProvider( name, priority, getTypeId, getModel, getModelFromTypeId )
		ModelManager.get().RegisterModelProvider( provider )
		self.modelProviders.append( provider )
		return provider

	def buildLuaObjectEnumerator( self, name, enumerateObjects, getObjectRepr, getObjectTypeRepr ):
		enumerator = LuaObjectEnumerator( name, enumerateObjects, getObjectRepr, getObjectTypeRepr )
		ModelManager.get().registerObjectEnumerator( enumerator )
		self.enumerators.append( enumerator )
		return enumerator

	def getTypeId(self, obj):
		return ModelManager.get().getTypeId(obj)

	def cleanLuaBridgeReference(self):
		#clean type getter
		for provider in self.modelProviders:
			logging.info( 'unregister provider:%s'% repr(provider) )
			provider.clear()
			ModelManager.get().unregisterModelProvider( provider )

		for enumerator in self.enumerators:
			logging.info( 'unregister enumerator:%s'% repr(enumerator) )
			ModelManager.get().unregisterObjectEnumerator( enumerator )

		self.modelProviders = []
		self.enumerators    = []



ModelBridge()

##----------------------------------------------------------------##
class SafeDict(object):
	def __init__( self, dict ):
		self.__dict = dict

	def __setitem__( self, key, value ):
		self.__dict[key] = value

	def __getitem__( self, key ):
		return self.__dict.get( key, None )

	def __iter__( self ):
		return self.__dict

	def values( self ):
		return self.__dict.values()

def registerLuaEditorCommand( fullname, cmdCreator ):
	class LuaEditorCommand( EditorCommand ):	
		name = fullname
		def __init__( self ):
			self.luaCmd = cmdCreator()

		def init( self, **kwargs ):
			cmd = self.luaCmd
			return cmd.init( cmd, SafeDict( kwargs ) )

		def redo( self ):
			cmd = self.luaCmd
			return cmd.redo( cmd )

		def undo( self ):
			cmd = self.luaCmd
			return cmd.undo( cmd )
			
	return LuaEditorCommand
