module 'mock'
--------------------------------------------------------------------
local charCodes = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,:.?!{}()<>+_="
--------------------------------------------------------------------
-------font
local function loadFont( node )
	local font  = MOAIFont.new()
	local atype = node.type
	--TODO: support serialized font
	local attributes = node.attributes or {}
	if attributes[ 'serialized' ] then
		local sdataPath   = node.objectFiles['data']
		local texturePath = node.objectFiles['texture']
		font = dofile( sdataPath )
		-- load the font image back in
		local image = MOAIImage.new ()
		image:load ( texturePath, 0 )
		-- set the font image
		font:setCache()
		font:setReader()
		font:setImage( image )
	end

	if atype == 'font_bmfont' then
		local texPaths = {}
		for k, v in pairs( node.dependency ) do
			if k:sub(1,3) == 'tex' then
				local id = tonumber( k:sub(5,-1) )
				texPaths[ id ] = v
			end
		end
		local textures = {}
		for i, path in ipairs( texPaths ) do
			local tex, node = loadAsset( path )
			table.insert( textures, tex:getMoaiTexture() )
		end
		if #textures > 0 then
			font:loadFromBMFont( node.objectFiles['font'], textures )
		else
			_warn('bmfont texture not load', node:getNodePath() )
		end

	elseif atype == 'font_ttf' then
		local filename = node.objectFiles['font']
		font:getReader():enableAntiAliasing( true )
		font:getCache():setColorFormat( MOAIImage.COLOR_FMT_RGBA_8888 )
		font:load( filename, 0 )

	elseif atype == 'font_bdf' then
		font:load( node.objectFiles['font'] )

	else
		_error( 'failed to load font:', node.path )
		return getFontPlaceHolder()
	end

	local dpi           = 72
	local size          = attributes['size'] or 20
	local preloadGlyphs = attributes['preloadGlyphs']

	if preloadGlyphs then	font:preloadGlyphs( preloadGlyphs, size ) end
	font.size = size

	return font
end

--------------------------------------------------------------------
registerAssetLoader( 'font_ttf',    loadFont )
registerAssetLoader( 'font_bdf',    loadFont )
registerAssetLoader( 'font_bmfont', loadFont )

--preload font placeholder
getFontPlaceHolder()
