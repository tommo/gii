module ('mock')

function loadAssetDataTable(filename) --lua or json?
	-- _stat( 'loading json data table', filename )
	if not filename then return nil end
	local f = io.open( filename, 'r' )
	if not f then
		error( 'data file not found:' .. tostring( filename ),2  )
	end
	local text=f:read('*a')
	f:close()
	local data =  MOAIJsonParser.decode(text)
	if not data then _error( 'json file not parsed: '..filename ) end
	return data
end

function loadTextData( filename )
	local fp = io.open( filename, 'r' )
	local text = fp:read( '*a' )
	return text
end
---------------------basic loaders
local basicLoaders = {}
function basicLoaders.text( node )
	return loadTextData( node.filePath )
end

----------REGISTER the loaders
for assetType, loader in pairs(basicLoaders) do
	registerAssetLoader( assetType, loader )
end
