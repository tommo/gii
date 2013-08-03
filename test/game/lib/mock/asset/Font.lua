module 'mock'
-------font
local charCodes = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,:.?!{}()<>+_="

--workaround rescaled bmfont rendering ( ?? )
local globalTextScale = 1

function setGlobalTextScale( scl )
	globalTextScale = scl or 1
end


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
		--font texture will be loaded by system
		--its path will be modified in deployment
		font:loadFromBMFont( node.objectFiles['font'] )
	elseif atype == 'font_ttf' then
		local filename = node.objectFiles['font']
		font:load( filename )
	elseif atype == 'font_bdf' then
		font:load( node.objectFiles['font'] )
	end

	local dpi           = 72
	local size          = attributes['size'] or 20
	local preloadGlyphs = attributes['preloadGlyphs']

	if preloadGlyphs then	font:preloadGlyphs( preloadGlyphs, size ) end
	font.size = size

	return font
end


function loadTextStyle( styleData )
	local style = MOAITextStyle.new()
	local font, node = loadAsset( styleData.font )
	--TODO: add a default font here
	style:setFont(font)
	if styleData.color then	style:setColor( unpack( styleData.color ) )	end
	local allowScale = styleData.allowScale
	-- node.type == 'font_bmfont'
	if allowScale then
		--fixed font-size * variant font-scale = style size
		local fsize = font.size or 30
		local size  = styleData.size or font.size or 12	
		local scale = size / fsize
		style:setSize( fsize )
		style:setScale( scale )
	else
		--variant font-size = style size
		--TODO: allow a progressive font-size adaption 
		style:setScale( globalTextScale )
		local size= styleData.size or font.size or 12	
		style:setSize( size/globalTextScale )
	end

	style.name = styleData.name
	return style
end

local function loadStyleSheet( node )
	local sheetData = loadAssetDataTable( node:getObjectFile('def') or node:getFilePath() )
	local fonts  = {}   --preloaded fonts
	local sheet  = {}
	--load fonts
	for i, styleData in ipairs( sheetData.styles ) do
		local style = loadTextStyle( styleData )
		sheet[ styleData.name ] = style
	end
	return sheet
end

registerAssetLoader( 'font_ttf',    loadFont )
registerAssetLoader( 'font_bdf',    loadFont )
registerAssetLoader( 'font_bmfont', loadFont )
registerAssetLoader( 'stylesheet',  loadStyleSheet )