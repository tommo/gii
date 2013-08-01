require 'mock.env'

module ('mock.edit', package.seeall)

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

-- --------------------------------------------------------------------
-- --MODEL
----------------------------------------------------------------------
local modelBridge     = GII_PYTHON_BRIDGE.ModelBridge.get()
local modelFromObject = Model.fromObject
local getClass        = getClass

----
local function buildGiiModel( model )
	local pmodel = GII_PYTHON_BRIDGE.LuaObjectModel( model.__name )
	
	for i, f in ipairs( model:getFieldList( true ) ) do
		--todo: array/ list field type
		local option = {
			get = f.__getter,
			set = f.__setter,
			--extra
			--widget?
			--range?
		}
		pmodel:addLuaFieldInfo( f.__id, f.__type, option )
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
	return getClass( obj )
end

----
local function modelGetter( obj )
	local model = modelFromObject( obj )
	if not model then return nil end	
	--if not converted, convert first
	local giiModel = model.__gii_model
	if not giiModel then
		giiModel = buildGiiModel( model )
	end
	return giiModel
end

----
gii.registerModelProvier{
	name      = 'MockModelProvider',
	priority  = 100,
	getTypeId = typeIdGetter,
	getModel  = modelGetter,
}

--------------------------------------------------------------------
mock.setLogLevel( 'status' )