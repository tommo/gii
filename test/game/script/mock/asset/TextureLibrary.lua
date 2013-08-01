module 'mock'

local textureTable = {}
local groupTable   = {}
local atlasTable   = {}

local texturePlaceHolder = false
local function getTexturePlaceHolder()
	if not texturePlaceHolder then
		texturePlaceHolder = MOAIImageTexture.new()
		local w, h = 64, 64
		texturePlaceHolder.init( w, h )
		texturePlaceHolder.fillRect( 0,0, w, h, 1, 0, 1, 1 )
		texturePlaceHolder.invalidate()
	end
	return texturePlaceHolder
end


local defaultGroup = {
	filter             = 'nearest',
	wrapmode           = 'clamp',
	mipmap             = false,
	premultiply_alpha  = true,
}

-----
local function loadSingleTexture( path, groupId )
	if type( path ) ~= 'string' then 
		_error( " unknown texture path:", path )
		return getTexturePlaceHolder()
	end

	local absPath = absAssetPath( path ) --FIXME: test only
	_stat( 'loading single texture:' , absPath )

	local group     = groupTable [ groupId ] or defaultGroup
	local tex       = MOAITexture.new()

	local transform = MOAIImage.TRUECOLOR
	if group.premultiply_alpha then
		transform = transform + MOAIImage.PREMULTIPLY_ALPHA
	end

	tex:load( absPath, transform )
	if tex:getSize() <= 0 then
		_warn( 'failed load texture file:', path )
		return getTexturePlaceHolder()
	end

	tex.group = group
	
	local filter
	if group.filter == 'linear' then
		if group.mipmap then
			filter = MOAITexture.GL_LINEAR_MIPMAP_LINEAR
		else
			filter = MOAITexture.GL_LINEAR
		end
	else  --if group.filter == 'nearest' then
		if group.mipmap then
			filter = MOAITexture.GL_NEAREST_MIPMAP_NEAREST
		else
			filter = MOAITexture.GL_NEAREST
		end
	end	

	tex:setFilter( filter )
	tex:setWrap( group.wrapmode == 'wrap' )
	return tex
end

--------texpack
--[[
	atlases = [
		{ path = '...' }
	],
	textures = [
		{ path = '...', atlasId = n }
	]
]]
local function loadAtlas( groupId )
	local group = groupTable[ groupId ]
	if group.atlas then return group.atlas end

	local atlas = atlasTable[ atlasId ]
	if not atlas then
		_error( 'no atlas found:', atlasId )
		return nil
	end

	local f = io.open( atlas.path, 'r' )
	if not f then 
		error( 'file not found', atlas.path ) --TODO: proper exception handle
		return nil
	end
	local text = f:read( '*a' )
	f:close()
	local data = MOAIJsonParser.decode( text )
	if not data then 
		error('file not parsed') --TODO: proper exception handle
		return nil
	end

	local atlases  = {}
	local textures = {}
	for i, texpath in pairs( data['atlases'] ) do
		local tex = loadSingleTexture( texpath, atlas.group )
		if not tex then
			error( 'error loading texture:'..texpath )
		end
		atlases[i] = tex
	end

	for i,item in pairs( data['items'] ) do
		local x, y, w, h = unpack( item.rect )
		local tex  = atlases[ item.atlas+1 ]
		local name = item.name
		tw,th = tex:getSize()
		local u0, v0, u1, v1 = x/tw, y/th, (x+w)/tw, (y+h)/th
		textures[ name ] = {
			name  = name,
			atlas = tex,
			rect  = item.rect,
			uv    = { u0, v1, u1, v0 },
			w     = w,
			h     = h,
			source= item.source
		}
	end
	
	local pack ={
		atlases  = atlases,
		textures = textures
	}

	return pack
end

--------texpack
local function loadSubTexture( t )
	local atlas = loadAtlas( t.group )
	return atlas.textures[ t.path ]
end

--------------------------------------------------------------------
function loadTextureLibrary( )
	local indexPath = rawget( _G, 'MOCK_TEXTURE_LIBRARY_INDEX')	
	if not indexPath then
		_stat 'no texture library specified, skip'
		return false
	end

	_stat( 'loading texture library', indexPath )

	--json assetnode
	local fp = io.open( indexPath, 'r' )
	if not fp then 
		_error( 'can not open texture library index file', indexPath )
		return false
	end
	local indexString = fp:read( '*a' )
	fp:close()

	local data = MOAIJsonParser.decode( indexString )
	if not data then return false end

	textureTable = {}
	groupTable   = {}
	atlasTable   = {}
	
	for _, value in pairs( data['groups'] ) do
		groupTable[ value['name'] ] = value
	end

	for path, value in pairs( data['textures'] ) do
		textureTable[ value['path'] ] = value
	end

	return true
end

--------------------------------------------------------------------
function loadTexture( path )
	local t = textureTable[ path ]
	
	if not t then 
		_warn( 'no texture found:', path )
		return nil
	end

	local tex = t.loadedTexture
	if not tex then
		if t.atlas then --atlas
			tex = loadSubTexture( t )
		else
			tex = loadSingleTexture( t.path, t.group )		
		end
		t.loadedTexture = tex
	end

	return tex

end


connectSignal( 'asset_library.loaded', loadTextureLibrary )

