module 'mock_edit'

----------------------------------------------------------------------
----MODEL
----------------------------------------------------------------------
local modelBridge     = GII_PYTHON_BRIDGE.ModelBridge.get()
local getClass        = getClass

----

local isTupleValue  = mock.isTupleValue
local isAtomicValue = mock.isAtomicValue

local unpackPythonList = gii.unpackPythonList
local function buildGiiModel( model )
	local pmodel = GII_PYTHON_BRIDGE.LuaObjectModel( model.__name )
	
	for i, f in ipairs( model:getFieldList( true ) ) do
		--todo: array/ list field type
		local option = {
			get = f.__getter,
			set = f.__setter,
			label = f.__label,
			meta  = f.__meta
		}
		local id     = f.__id
		local typeid = f.__type

		if typeid == '@enum' then
			if type(f.__enum) == 'table' then
				pmodel:addLuaEnumFieldInfo( id, f.__enum, option )
			else
				_error('invalid enum type')
			end
		elseif typeid == '@asset' then
			pmodel:addLuaAssetFieldInfo( id, f.__assettype, option )
		else
			if isTupleValue( typeid ) then
				local _set = f.__setter
				option.set = function( obj, tuple )
					_set( obj, unpackPythonList( tuple ) )
				end
			elseif not isAtomicValue( typeid ) then
				option['objtype'] = f.__objtype or 'ref'
			end
			pmodel:addLuaFieldInfo( id, typeid, option )
		end
	end

	local superModel = model:getSuperModel()
	if superModel then
		local superPModel = buildGiiModel( superModel )
		pmodel:setSuperType( superModel.__class )
	end

	model.__gii_model = pmodel

	return pmodel
end

----
local function typeIdGetter( obj )
	local tt = type(obj)
	if tt == 'table' then
		local mt = getmetatable(obj)
		if not mt then return nil end
		return mt
	elseif tt == 'userdata' then --MOAIObject
		local getClass = obj.getClass
		if getClass then
			return getClass(obj)
		end
	end
	return nil
end

----
local function modelGetter( obj )
	local model

	local tt = type(obj)
	if tt == 'table' then
		local clas = getmetatable(obj)
		if not isClass( clas ) then return nil end
		model = Model.fromClass( clas )
		
	elseif tt == 'userdata' then --MOAIObject
		local getClass = obj.getClass
		if getClass then
			local clas = getClass( obj )
			model = MoaiModel.fromClass( clas )
		end
	else
		return nil
	end

	if not model then return nil end	 
	local giiModel = model.__gii_model
	if not giiModel then --if not converted, convert first
		giiModel = buildGiiModel( model )
	end
	return giiModel

end

----
local function modelFromType( t )
	local model = Model.fromClass( t )
	if not model then return nil end	

	local giiModel = model.__gii_model
	if not giiModel then --if not converted, convert first
		giiModel = buildGiiModel( model )
	end
	return giiModel
end

----
gii.registerModelProvider{
	name               = 'MockModelProvider',
	priority           = 100,
	getTypeId          = typeIdGetter,
	getModel           = modelGetter,
	getModelFromTypeId = modelFromType
}


