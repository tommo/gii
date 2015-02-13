module 'mock'

registerSignals{
	'scene.serialize',
	'scene.deserialize',
}

--------------------------------------------------------------------
local function entitySortFunc( a, b )
	return  a._priority < b._priority
end

--------------------------------------------------------------------
local function collectEntity( entity, objMap )
	if entity.FLAG_INTERNAL or entity.FLAG_EDITOR_OBJECT then return end
	local coms = {}
	local children = {}

	for com in pairs( entity.components ) do
		if not com.FLAG_INTERNAL then
			table.insert( coms, objMap:map( com ) )
		end
	end

	local childrenList = {}
	local i = 1
	for e in pairs( entity.children ) do
		childrenList[i] = e
		i = i + 1
	end
	table.sort( childrenList, entitySortFunc )

	for i, child in ipairs( childrenList ) do
		local childData = collectEntity( child, objMap )
		if childData then
			table.insert( children, childData )
		end
	end
	return {
		id = objMap:map( entity ),
		components = coms,
		children   = children
	}
end

--------------------------------------------------------------------
local function insertEntity( scn, parent, edata, objMap )
	local id = edata['id']
	local components = edata['components']
	local children   = edata['children']

	local entity = objMap[ id ][ 1 ]
	
	if scn then
		scn:addEntity( entity )
	elseif parent then
		parent:addChild( entity )
	end

	--components
	for _, comId in ipairs( components ) do
		local com = objMap[ comId ][ 1 ]
		entity:attach( com )
	end
	
	--chilcren
	for i, childData in ipairs( children ) do
		insertEntity( nil, entity, childData, objMap )
	end

	return entity
end


--------------------------------------------------------------------
function serializeScene( scene, option )
	option = option or {}
	emitSignal( 'scene.serialize', scene )
	local objMap = SerializeObjectMap()
	local entityList = {}
	for e in pairs( scene.entities ) do
		if not e.parent then --1st level entity
			table.insert( entityList, e )
		end
	end
	table.sort( entityList, entitySortFunc )

	local entities = {}
	for i, e in ipairs( entityList ) do
		local data = collectEntity( e, objMap )
		if data then table.insert( entities, data ) end
	end

	local map = {}
	while true do
		local newObjects = objMap:flush()
		if next( newObjects ) then
			for obj, id in pairs( newObjects )  do
				map[ id ] = _serializeObject( obj, objMap )
			end
		else
			break
		end
	end

	--guid
	local guidMap = {}
	for obj, id in pairs( objMap.objects ) do
		local guid = obj.__guid
		if guid then
			guidMap[ id ] = guid
		end
	end

	--prefab
	local prefabIdMap = {}
	for obj, id in pairs( objMap.objects ) do
		local prefabId = obj.__prefabId
		if prefabId then
			prefabIdMap[ id ] = prefabId
		end
	end

	local result = {
		_assetType  = 'scene',
		meta        = scene.metaData or {},
		map         = map,
		entities    = entities,
		guid        = guidMap,
		prefabId    = prefabIdMap
	}

	if option.save_dependency_list then
		result.asset_dependency = collectSceneAssetDependency( scene )
	end
	return result
end

--------------------------------------------------------------------
function deserializeScene( data, scn )
	local objMap = {}
	_deserializeObjectMap( data.map, objMap )
	
	if not scn then
		scn = Scene()
		scn:init()
	end

	for i, edata in ipairs( data.entities ) do
		insertEntity( scn, nil, edata, objMap )
	end
	scn.metaData = data['meta'] or {}
	if data['guid'] then
		for id, guid in pairs( data['guid'] ) do
			local obj = objMap[ id ][ 1 ]
			obj.__guid = guid
		end
	end

	if data['prefabId'] then
		for id, prefabId in pairs( data['prefabId'] ) do
			local obj = objMap[ id ][ 1 ]
			obj.__prefabId = prefabId
		end
	end

	emitSignal( 'scene.deserialize', scn )
	return scn
end

function serializeSceneToFile( scn, path, option )
	local data = serializeScene( scn, option )
	local str  = encodeJSON( data )
	local file = io.open( path, 'wb' )
	if file then
		file:write( str )
		file:close()
	else
		_error( 'can not write to scene file', path )
		return false
	end
	return true
end

--------------------------------------------------------------------
--PREFAB
--------------------------------------------------------------------
function serializeEntity( obj )
	local objMap = SerializeObjectMap()
	for i, layer in ipairs( game:getLayers() ) do
		objMap:map( layer.name )
	end
	local data = collectEntity( obj, objMap )	
	local map = {}
	while true do
		local newObjects = objMap:flush()
		if next( newObjects ) then
			for obj, id in pairs( newObjects )  do
				map[ id ] = _serializeObject( obj, objMap, 'noNewRef' )
			end
		else
			break
		end
	end
	return {				
		map    = map,
		body   = data
	}
end

function deserializeEntity( data )
	local objMap = {}
	_deserializeObjectMap( data.map, objMap )
	return insertEntity( nil, nil, data.body, objMap )
end

function loadSceneData( path )
	local node = getAssetNode( path )
	local data = node.cached.data
	if not data then
		local path = node:getObjectFile( 'def' )
		data = loadAssetDataTable( path )
		node.cached.data = data
	end
	return data
end

function _scanEntity( e, assetSet )
	scanObjectAsset( e, assetSet )
	if e.children then
		for child in pairs( e.children ) do
			_scanEntity( child, assetSet )
		end
	end
	if e.components then
		for com in pairs( e.components ) do
			scanObjectAsset( com, assetSet )
		end
	end
end

function scanEntityAsset( e )
	local assetSet = {}
	_scanEntity( e, assetSet )
	return assetSet
end

function scanSceneAsset( scn )
	local assetSet = {}
	for e in pairs( scn.entities ) do
		if not e.parent then
			_scanEntity( e, assetSet )
		end
	end
	return assetSet
end

-------------------------------------------------------------------
local function sceneLoader( node, option )
	local data = loadSceneData( node:getNodePath() )
	local scn  = option.scene or Scene()
	--configuration
	scn:init()
	scn.path = node:getNodePath()
	--entities
	deserializeScene( data, scn )
	local dep = data['asset_dependency']
	if dep then
		for assetPath in pairs( dep ) do
			mock.loadAsset( assetPath )
		end
	end

	return scn, false --no cache
end


registerAssetLoader( 'scene', sceneLoader )
