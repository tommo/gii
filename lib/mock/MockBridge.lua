require 'mock.env'
--------------------------------------------------------------------
-- mock.setLogLevel( 'status' )

--------------------------------------------------------------------
--Asset Sync
--------------------------------------------------------------------
local function onAssetModified( node ) --node: <py>AssetNode	
	local nodepath = node:getPath()
	mock.releaseAsset( nodepath )
end

local function onAssetRegister( node )
	local nodePath = node:getPath()
	mock.registerAssetNode( nodePath, {
			deploy      = node.deployState == true,
			filePath    = node.filePath,
			type        = node.assetType,
			objectFiles = gii.dictToTable( node.objectFiles ),
		})
end

local function onAssetUnregister( node )
	local nodePath = node:getPath()
	mock.unregisterAssetNode( nodePath )
end

gii.connectPythonSignal( 'asset.modified',   onAssetModified )
gii.connectPythonSignal( 'asset.register',   onAssetRegister )
gii.connectPythonSignal( 'asset.unregister', onAssetUnregister )


----------------------------------------------------------------------
----MODEL
----------------------------------------------------------------------
local modelBridge     = GII_PYTHON_BRIDGE.ModelBridge.get()
local getClass        = getClass

----
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
			assert ( type(f.__enum) == 'table' )
			pmodel:addLuaEnumFieldInfo( id, f.__enum, option )
		else
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
	local tt = type(v)
	if tt == 'table' then
		local mt = getmetatable(v)
		if not mt then return nil end
		return mt
	elseif tt == 'userdata' then --MOAIObject
		local getClass = v.getClass
		if getClass then
			return getClass(v)
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
			model = Model.fromClass( clas )
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
gii.registerModelProvier{
	name               = 'MockModelProvider',
	priority           = 100,
	getTypeId          = typeIdGetter,
	getModel           = modelGetter,
	getModelFromTypeId = modelFromType
}

local function onContextChange( ctx, oldCtx )
	mock.game:setCurrentRenderContext( ctx )
end

gii.addContextChangeListeners( onContextChange )


----------------------------------------------------------------------
----Component/Entity Class
----------------------------------------------------------------------


--------------------------------------------------------------------
--Editor Command
--------------------------------------------------------------------
CLASS: EditorCommand ()
function EditorCommand.register( clas, name )
	_stat( 'register Lua Editor Command', name )
	gii.registerLuaEditorCommand( name, clas )
end

function EditorCommand:init()
end

function EditorCommand:redo()
end

function EditorCommand:undo()
end


