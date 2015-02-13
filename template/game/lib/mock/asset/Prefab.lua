module 'mock'
--------------------------------------------------------------------
CLASS: Prefab ()

function Prefab:__init( data, id )
	self.data = data
	self.id = id
end

function Prefab:createInstance()
	local instance
	local data = self.data
	if not data.body then
		_stat('loading empty prefab')
		instance = Entity()
	else
		instance = deserializeEntity( data )
	end
	instance.__prefabId = self.id or true
	return instance
end

--------------------------------------------------------------------
function loadPrefab( path )
	local prefab, node = loadAsset( path )
	if prefab and node:getType() == 'prefab' then
		return prefab:createInstance()
	else
		_warn( 'prefab not found:', path )
		return nil
	end
end

--------------------------------------------------------------------
function PrefabLoader( node )
	local path = node:getObjectFile( 'def' )
	local data = loadAssetDataTable( path )

	return Prefab( data, node:getNodePath() )
end

registerAssetLoader( 'prefab',  PrefabLoader )
