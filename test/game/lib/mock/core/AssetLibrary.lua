module ('mock')

registerSignals{
	'asset_library.loaded',
}

--tool functions
function splitPath( path )
	path = string.gsub( path, '\\', '/' )
	return string.match( path, "(.-)[\\/]-([^\\/]-%.?([^%.\\/]*))$" )
end

function stripExt(p)
	return string.gsub( p, '%..*$', '' )
end


--asset index library
local AssetLibrary = {}

--asset loaders
local AssetLoaders = {}

---env
local AssetBasePath   = false
local ProjectBasePath = false

function absAssetPath( path )
	if AssetBasePath then
		return AssetBasePath .. '/' .. ( path or '' )
	else
		return path
	end
end

function absProjectPath( path )
	if ProjectBasePath then
		return ProjectBasePath .. '/' .. ( path or '' )
	else
		return path
	end
end

function setBasePaths( prjBase, assetBase )
	ProjectBasePath = prjBase
	AssetBasePath   = assetBase
end

function loadAssetLibrary()
	local indexPath = rawget( _G, 'MOCK_ASSET_LIBRARY_INDEX' )
	if not indexPath then
		_stat( 'asset library not specified, skip.' )
		return
	end
	_stat( 'loading library from', indexPath )
	
	--json assetnode
	local fp = io.open( indexPath, 'r' )
	if not fp then 
		_error( 'can not open asset library index file', indexPath )
		return
	end
	local indexString = fp:read( '*a' )
	fp:close()
	local data = MOAIJsonParser.decode( indexString )

	AssetLibrary={}
	for path, value in pairs( data ) do
		--we don't need all the information from python
		registerAssetNode( path, value )		
	end
	emitSignal( 'asset_library.loaded' )
end

CLASS: AssetNode ()

function AssetNode:getSiblingPath( name )
	return self.parent..'/'..name
end

function AssetNode:getChildPath( name )
	return self.path..'/'..name
end

function AssetNode:getObjectFile( name )
	return self.objectFiles[ name ]
end

function AssetNode:getFilePath( )
	return self.filePath
end



function registerAssetNode( path, data )
	ppath=splitPath(path)
	local node = setmetatable(
		{
			path        = path,
			deploy      = data['deploy'] == true,
			filePath    = data['filePath'],
			properties  = data['properties'],
			objectFiles = data['objectFiles'],
			type        = data['type'],
			parent      = ppath,
			asset       = data['type'] == 'folder' and true or false
		}, 
		AssetNode
		)
	
	AssetLibrary[ path ] = node
	return node
end

function unregisterAssetNode( path )
	AssetLibrary[ path ] = nil
end


function getAssetNode( path )
	return AssetLibrary[ path ]
end

--loader: func( assetType, filePath )
function registerAssetLoader( assetType, loader )
	AssetLoaders[ assetType ] = loader
end

--put preloaded asset into AssetNode of according path
function preloadIntoAssetNode( path, asset )
	local node = getAssetNode( path )
	if node then
		node.asset = asset 
		return asset
	end
	return false
end

--load asset of node
function loadAsset( path, loadPolicy )
	if path == '' then return nil end
	if not path   then return nil end

	loadPolicy   = loadPolicy or 'auto'
	local node   = getAssetNode( path )
	if not node then 
		_warn ( 'no asset found', path or '???' )
		return nil
	end

	if loadPolicy ~= 'force' then
		local asset  = node.asset
		if asset then
			return asset, node
		end
	end

	_stat( 'loading asset from', path )
	if loadPolicy ~= 'auto' and loadPolicy ~='force' then return nil end

	if node.parent then
		loadAsset( node.parent )
		if node.asset then return node.asset end --already preloaded		
	end

	--load from file
	local atype  = node.type
	local loader = AssetLoaders[ atype ]
	if not loader then return false end
	local asset  = loader( node )
	if asset then
		node.asset = asset
		return asset, node
	else
		return nil
	end
end

--
function releaseAsset( path )
	-- 
	node = getAssetNode( path )
	if node then
		node.asset = nil
		_stat( 'released node asset', path )
	end

end

