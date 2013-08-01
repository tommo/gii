module ('mock')

function loadAssetDataTable(filename) --lua or json?
	--lua
	-- local f=loadfile(filename)
	-- if f then return f() end
	--json
	local f = io.open( filename,'r')
	if not f then return nil end
	local text=f:read('*a')
	f:close()
	return MOAIJsonParser.decode(text)
end

---------------------basic loaders
local basicLoaders = {}
function basicLoaders.text( node )
	local fp = io.open( node.filePath, 'r' )
	local text = fp:read( '*a' )
	return text
end

----------REGISTER the loaders
for assetType, loader in pairs(basicLoaders) do
	registerAssetLoader( assetType, loader )
end
