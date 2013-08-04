module ('mock')

CLASS: SubTexture ()
function SubTexture:getSize()
	return self.w, self.h
end

function SubTexture:getPixmapRect()
	return self.x, self.y, self.w, self.h
end

--------------------------------------------------------------------
local defaultTextureConfig = {
	filter             = 'nearest',
	wrapmode           = 'clamp',
	mipmap             = false,
	premultiply_alpha  = true,
}

--------------------------------------------------------------------
local texturePlaceHolder = false
function getTexturePlaceHolder()
	if not texturePlaceHolder then
		texturePlaceHolder = MOAIImageTexture.new()
		local w, h = 64, 64
		texturePlaceHolder:init( w, h )
		texturePlaceHolder:fillRect( 0,0, w, h, 0, 1, 0, 1 )
		texturePlaceHolder:invalidate()
	end
	return texturePlaceHolder
end


--------------------------------------------------------------------
local function loadSingleTexture( pixmapPath, group )
	_stat( 'loading texture from pixmap:' , pixmapPath )

	local tex = MOAITexture.new()
	tex.pixmapPath = pixmapPath

	local transform = MOAIImage.TRUECOLOR
	if group['premultiply_alpha'] then
		transform = transform + MOAIImage.PREMULTIPLY_ALPHA
	end

	tex:load( absProjectPath( pixmapPath ), transform )
	if tex:getSize() <= 0 then
		_warn( 'failed load texture file:', path )
		return getTexturePlaceHolder()
	end

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
	tex.type = 'texture'
	return tex

end


--------texpack
local function loadTexPack( config )	
	local base = config[ 'cache' ]
	local configPath = base .. '/atlas.json'
	local f = io.open( configPath, 'r' )
	if not f then 
		error( 'file not found', configPath )   --TODO: proper exception handle
		return nil
	end
	local text = f:read( '*a' )
	f:close()
	local data = MOAIJsonParser.decode( text )

	if not data then 
		error('atlas config file not parsable') --TODO: proper exception handle
		return nil
	end

	local atlases  = {}
	local textures = {}
	for i, texpath in pairs( data[ 'atlases' ] ) do
		local tex = loadSingleTexture( base .. '/' .. texpath, config )
		if not tex then
			error( 'error loading texture:' .. texpath )
		end
		atlases[i] = tex
	end

	for i,item in pairs( data[ 'items' ] ) do
		local x, y, w, h = unpack( item.rect )
		local tex  = atlases[ item.atlas + 1 ]
		local name = item.name
		tw,th = tex:getSize()
		local u0, v0, u1, v1 = x/tw, y/th, (x+w)/tw, (y+h)/th
		textures[ name ] = SubTexture:rawInstance{
			type   = 'sub_texture',
			name   = name,
			atlas  = tex,
			rect   = item.rect,
			uv     = { u0, v1, u1, v0 },
			w      = w,
			h      = h,
			x      = x,
			y      = y,
			source = item.source
		}
	end
	
	local pack ={
		atlases  = atlases,
		textures = textures
	}

	return pack
end

-----
local loadedTexPack = {}

local function getTexPack( config )
	local pack = loadedTexPack[ config.name ]
	if pack then return pack end
	pack = loadTexPack( config )
	loadedTexPack[ config.name ] = pack
	return pack
end

--------texpack
local function loadSubTexture( path, config )
	local cacheDir = config[ 'cache' ]
	local pack = getTexPack( config )	
	assert( pack, 'texpack not loaded correctly.')
	local sub = pack.textures[ path ]
	return sub
end

-------main
local function loadTexture( node )
	local configPath = node:getAbsObjectFile( 'config' )
	
	local config = loadAssetDataTable( configPath ) or defaultTextureConfig
	if not config[ 'atlas_allowed' ] then
		local pixmapPath = node.objectFiles[ 'pixmap' ]
		return loadSingleTexture( pixmapPath, config )
	else
		return loadSubTexture( node.path, config )
	end

	return tex
end


registerAssetLoader( 'texture',     loadTexture )
registerAssetLoader( 'texpack',     loadTexPack )
registerAssetLoader( 'sub_texture', loadTexture )
