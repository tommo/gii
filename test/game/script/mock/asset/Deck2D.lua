module 'mock'

--[[
	SpritePack supports:
		1. single quad         --  MOAIGfxQuad2D
		2. quad array          --  MOAIGfxQuadDeck2D
		3. quad list array     --  MOAIGfxQuadListDeck
		4. stretch patch deck  --  MOAIStretchPatch2D
		5. tile deck           --  Patch
]]
local loaders = {}

local function getTextureInfo( item )
	local tex, node = loadAsset( item.texture )
	if tex.type == 'sub_texture' then
		local u0, v0, u1, v1 = unpack( tex.uv )
		return tex.atlas, u0, v0, u1, v1, tex.rotated or false
	else
		return tex, 0,0,1,1, false --texture, u0,v0,u1,v1,  rotated
	end
end

function loaders.quad( item, pack )
	local texture, u0,v0,u1,v1, rotated = getTextureInfo( item )
	--TODO:rotated texture?
	local deck = MOAIGfxQuad2D.new()
	deck:setTexture( texture )
	deck:setRect( unpack( item.rect ) )
	deck:setUVRect( u0, v0, u1, v1 )
	return deck
end

function loaders.quad_array( item, pack )
	local texture, u0,v0,u1,v1, rotated = getTextureInfo( item )
	--TODO:rotated texture?
	local deck  = MOAIGfxQuadDeck2D.new()
	local quads = item.quads
	deck:setTexture( texture )
	deck:reserve( #quads )
	for i, quad in ipairs( quads ) do
		deck:setRect   ( i, unpack( quad.rect   ) )
		deck:setUVRect ( i, unpack( quad.uvrect ) )
	end
end

function loaders.quadlist_array( item, pack )
	local texture, u0,v0,u1,v1, rotated = getTextureInfo( item )
	local deck = MOAIGfxQuadListDeck2D.new()
	--TODO:not useful unless with a good editor
	--TODO:rotated texture?
	-- deck:setTexture( texture )
	-- deck:setRect( unpack( item.rect ) )
	-- deck:setUVRect( u0, v0, u1, v1 )
	return deck
end

function loaders.stretchpatch( item, pack )
	local texture, u0,v0,u1,v1, rotated = getTextureInfo( item )
	--TODO:rotated texture?
	local patch  = MOAIStretchPatch2D.new ()
	local layout = item.layout
	local cols   = layout.columns
	local rows   = layout.rows
	
	patch:setTexture( texture )
	patch:reserveRows( #rows )
	for i = 1, #rows do
		local row = rows[i]
		patch:setRow( i, row[1], row[2] )
	end

	patch:reserveColumns( #cols )
	for i = 1, #cols do
		local col = cols[i]
		patch:setColumn( i, col[1], col[2] )
	end

	patch:reserveUVRects ( 1 )
	patch:setUVRect ( 1, u0, v0, u1, v1 )
	return patch
end

function loaders.tileset( item, pack )
	local texture, u0,v0,u1,v1, rotated = getTextureInfo( item )
	local texSizeU, texSizeV = u1-u0, v1-v0
	--TODO:rotated texture?
	local col, row = item.col, item.row
	local cellSizeU = item.cellSizeU --tilesize + guttersize
	local cellSizeV = item.cellSizeV --tilesize + guttersize
	local tileSizeU = item.tileSizeU
	local tileSizeV = item.tileSizeV
	local offsetU   = item.offsetU
	local offsetV   = item.offsetV

	local deck = MOAITileDeck2D.new()
	deck:setTexture( texture )
	deck:setSize( 
		col, row, 
		cellSizeU * texSizeU, cellSizeV * texSizeV, 
		cellOffU  * texSizeU, cellOffV  * texSizeV,
		tileSizeU * texSizeU, tileSizeV * texSizeV
	)
	deck.tileSize = { item.tileWidth, item.tileHeight }
end


function spritePackLoader( node )
	local pack   = loadAssetDataTable( node:getObjectFile('def') )
	local name   = pack.name
	local result = {}
	--load each deck settings
	for i, item in ipairs( pack.items ) do
		local itype  = item.type
		local loader = loaders[ itype ]
		assert( loader, 'unknown deck type:'..itype )
		local deck = loader( item, pack )
		result[ item.name ] = deck
	end

	return result
end

registerAssetLoader ( 'deck2d' )