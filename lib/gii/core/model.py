def getSuperType( t ):
	if isinstance( t, DataType ):
		return t.getSuperType()		
	return None
	
##----------------------------------------------------------------##
class DataType(object):
	
	def getName(self):
		return None

	def getSuperType( self ):
		return None

	def getDefaultValue(self):
		return None
	
	def repr(self, value):
		return repr(value)

	def check(self, value):
		return value

	def serialize(self, value):
		raise 'not implemented'

	def deserialize(self, data):
		raise 'not implemented'

	def register( self ):
		raise 'not implemented'


##----------------------------------------------------------------##
class PythonValueType(DataType):
	def __init__(self ,t, defaultValue):
		self._type = t
		name = repr(t)
		self._defaultValue=defaultValue

	def getName(self):
		return repr(self._type)

	def check(self, value):
		if value is self._type:
			return value
		return None

	def register( self, typeId ):
		ModelManager.get().registerPythonModel( typeId, self )
		return self


##----------------------------------------------------------------##
class EnumType( DataType ):
	def __init__( self, name, enum, defaultValue = None ):
		#validation
		self.name = name
		itemDict = {}

		self.itemDict = itemDict
		for item in enum:
			( name, value ) = item
			itemDict[ name ] = value
		self._defaultValue = defaultValue
		self.itemList = enum[:]

	def getName( self ):
		return self.name

	def getSuperType( self ):
		return EnumType

	def repr( self, value ):
		return '<%s> %s' %( self.name, repr( value ) )

	def fromIndex( self, idx ):
		if idx < 0 or idx >= len( self.itemList ):
			return None
		( name, value ) = self.itemList[ idx ]
		return value

	def toIndex( self, value ):
		for i, item in enumerate( self.itemList ):
			( k, v ) = item
			if value == v: return i
		return None

	def register( self, typeId ):
		ModelManager.get().registerPythonModel( typeId, self )
		return self


# class StringEnumValueType(object):	
# 	def __init__(self, arg):
# 		super(IntEnumValueType, self).__init__()
# 		self.arg = arg
		

##----------------------------------------------------------------##
class FlagsValueType( DataType ):
	def __init__( self, flags, defaultValue ):
		super(FlagsValueType, self).__init__()
		self.arg = arg


##----------------------------------------------------------------##
class ObjectModel(DataType):
	@staticmethod
	def fromList( name, fieldList, **option ):
		model = ObjectModel( name, **option )
		for dataTuple in fieldList:
			if len(dataTuple) == 3:
				(key, typeId, fieldOption ) = dataTuple
			else:
				(key, typeId) = dataTuple
				fieldOption = {}
			model.addFieldInfo( key, typeId, **fieldOption )
		return model

	def getName(self):
		return self.name

	def getSuperType(self):
		return self.superType

	def setSuperType( self , typeInfo ):
		self.superType = typeInfo
		#TODO: check circular reference

	def isSubTypeOf(self, superType):
		s = self.getSuperType()
		while s:
			if superType == s : return True
			s = s.getSuperType()
		return False
		
	def isSuperTypeOf(self, subType):
		return subType.isSubTypeOf( self )

	def __init__(self, name, superType = None, **option):
		self.name      = name
		self.fieldMap  = {}
		self.fieldList = []
		self.superType = None
		if superType: self.setSuperType( superType )
		if not option: return
		self.defaultRefWidget = option.get('defaultRefWidget',None)
		self.defaultSubWidget = option.get('defaultSubWidget',None)
		self.reference = option.get('reference',None)
		self.subobject = option.get('subobject',None)

	def addFieldInfo(self, id, t, **option):
		f = Field(self, id, t, **option)
		self.fieldMap[id] = f
		self.fieldList.append(f)
		return f

	def getFieldInfo(self, id):
		return self.fieldMap.get(id, None)

	def getFieldValue(self, obj, id):
		f=self.getFieldInfo(id)
		return f.getValue(obj)

	def setFieldValue(self, obj, id, value):
		f=self.getFieldInfo(id)
		f.setValue(obj, value)

##----------------------------------------------------------------##
class Field(object):
	"""docstring for Field"""
	def __init__(self, model, id, _type, **option):
		self._type = _type
		self.model = model
		self.id    = id

		option = option or {}

		self.label	   = option.get( 'label',    id )
		self.default   = option.get( 'default',  None )
		self.widget	   = option.get( 'widget',   None )
		self.readonly  = option.get( 'readonly', False )
		self.choice	   = option.get( 'choice',   None )
		self.reference = option.get( 'reference', None )
		self.subobject = option.get( 'subobject', None )		

		self.getter	   = option.get( 'get',   True )
		self.setter	   = option.get( 'set',   True )
		self.option    = option
		if self.setter == False: self.readonly = True

	def getType( self ):
		return self._type

	def getValue( self, obj, defaultValue = None ):
		getter = self.getter
		if getter == False: return None
		#indexer
		if getter == True:
			if isinstance( obj, dict ):
				return obj.get( self.id, defaultValue )
			else:
				return getattr( obj, self.id, defaultValue )
		#caller
		v = self.getter( obj, self.id )
		if v is None: return defaultValue
		return v

	def setValue( self, obj, value ):
		if self.readonly: return 
		if self.setter == True:
			if isinstance( obj, dict ):
				obj[ self.id ] = value
			else:
				setattr(obj, self.id, value)
		else:
			self.setter(obj, value)

##----------------------------------------------------------------##
class TypeIdGetter(object):
	"""docstring for TypeInfoGetter"""
	def getTypeId(self, obj):
		return None

##----------------------------------------------------------------##
## ModelManager
##----------------------------------------------------------------##
class ModelProvider(object):
	def getModel( self, obj ):
		return None

	def getTypeId( self, obj ):
		return None

	#the bigger the first
	def getPriority( self ):
		return 0
	
class PythonModelProvider(ModelProvider):
	def __init__(self):
		self.typeMapV           = {}
		self.typeMapN           = {}

		self.registerModel( int,   PythonValueType( int,    0 ) )
		self.registerModel( float, PythonValueType( float,  0 ) )
		self.registerModel( str,   PythonValueType( str,    '' ) )
		self.registerModel( bool,  PythonValueType( bool,   False ) )

	def registerModel(self, t, model):
		self.typeMapV[t]=model
		self.typeMapN[model.getName()]=model
		return model

	def unregisterModel(self, t, Model):
		del self.typeMapV[t]
		del self.typeMapN[Model.getName()]

	def getModel( self, obj ):
		typeId = type(obj)
		if typeId:
			return self.typeMapV.get( typeId, None )
		return None

	def getTypeId( self, obj ):
		typeId = type(obj)
		return typeId

	def getPriority( self ):
		return 0
		

class ModelManager(object):
	_singleton=None

	@staticmethod
	def get():
		return ModelManager._singleton

	def __init__(self):
		assert(not ModelManager._singleton)
		ModelManager._singleton=self

		self.modelProviders     = []
		self.objectEnumerators  = []
	
		self.pythonModelProvider = self.registerModelProvier( PythonModelProvider() )
		#build python types
	
	def registerModelProvier( self, provider ):
		self.modelProviders.append( provider )
		return provider

	def unregisterModelProvider( self, provider ):
		idx = self.modelProviders.index( provider )
		self.modelProviders.pop( idx )

	def registerEnumerator(self, typeId, enumerator):
		# assert not self.objectEnumerators.has_key(typeId), 'duplicated Enumerator for type:%s'%repr(typeId)
		# self.objectEnumerators[typeId]=enumerator
		self.objectEnumerators.append((typeId, enumerator))
		return enumerator

	def unregisterEnumerator(self, enumerator):
		newList = []
		for enumEntry in self.objectEnumerators:
			typeId, enum = enumEntry
			if enum != enumerator: newList.append( enumEntry )
		self.objectEnumerators = newList
	
	def getTypeId(self, obj):
		for provider in self.modelProviders:
			typeId = provider.getTypeId( obj )
			if typeId: return typeId			
		return None

	def getModel(self, obj):
		for provider in self.modelProviders:
			typeId = provider.getModel( obj )
			if typeId: return typeId			
		return None

	def enumerateObject(self, targetTypeId, context = None):
		res=[]
		for m in self.objectEnumerators:
			(typeId, enumerator) = m
			if issubclass(typeId, targetTypeId):
				objs = enumerator( targetTypeId, context )
				if objs:
					res += objs
		return res

	def registerPythonModel(self, typeId, model):
		self.pythonModelProvider.registerModel( typeId, model)


##----------------------------------------------------------------##
ModelManager()
