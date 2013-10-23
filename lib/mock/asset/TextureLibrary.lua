library = false

function saveLibrary( path )
	-- print( 'saving library', path )
	if library then
		return mock.serializeToFile( library, path )
	end
end

function loadLibrary( path )
	local getAssetNode = mock.getAssetNode
	-- print( 'loading library', path )
	library = mock.deserializeFromFile( nil, path ) or newLibrary()
	for i, group in ipairs( library.groups ) do
		if group.default then library.defaultGroup = group end
		local textures1 = {}
		for i, tex in ipairs( group.textures ) do
			if getAssetNode( tex.path ) then
				table.insert( textures1, tex )
			end
		end
		group.textures = textures1
	end
	return library 
end

function newLibrary()
	library = mock.TextureLibrary()	
	local defaultGroup = library:addGroup()
	defaultGroup.name = 'DEFAULT'
	defaultGroup.default = true
	library.defaultGroup = defaultGroup
	return library
end


function releaseTexPack( path )
	mock.releaseTexPack( path )
end