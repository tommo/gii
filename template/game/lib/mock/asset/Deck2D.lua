module 'mock'

--------------------------------------------------------------------
local loadedDecks = table.weak()

function getLoadedDecks()
	return loadedDecks
end

--------------------------------------------------------------------
CLASS: Deck2D ()
	:MODEL {
		Field 'type'     :string()  :no_edit();
		Field 'name'     :string()  :getset('Name')    :readonly() ;
		Field 'texture'  :asset('texture')  :getset('Texture') :readonly() ;		
	}

function Deck2D:__init()
	loadedDecks[ self ] = true
	self._deck = self:createMoaiDeck()
	self._deck.source = self
	self.name  = 'deck'
	self.w = 0
	self.h = 0
end


function Deck2D:setTexture( path, autoResize )
	local tex, node = mock.loadAsset( path )
	if not tex then return end
	if autoResize ~= false then
		local w, h = tex:getSize()
		self.w = w
		self.h = h
	end
	self.texturePath = path
	self.texture = tex
	self:update()
end

function Deck2D:getTexture()
	return self.texturePath
end


function Deck2D:getTextureData()
	if self.texture then
		return self.texture:getMoaiTextureUV()
	end
end

function Deck2D:getSize()
	return self.w , self.h
end

function Deck2D:setSize( w, h )
	self.w = w
	self.h = h
end

function Deck2D:getRect()
	local ox,oy = self:getOrigin()
	local w,h   = self:getSize()
	return ox - w/2, oy - h/2, ox + w/2, oy + h/2 
end
	
function Deck2D:setName( n )
	self.name = n
end

function Deck2D:getName()
	return self.name
end

function Deck2D:setOrigin( dx, dy )
end

function Deck2D:getOrigin()
	return 0,0
end

function Deck2D:getMoaiDeck()	
	return self._deck
end

function Deck2D:createMoaiDeck()
end

function Deck2D:update()
end


--------------------------------------------------------------------
CLASS: Quad2D ( Deck2D )
	:MODEL{
		Field 'ox' :number() :label('origin X') ;
		Field 'oy' :number() :label('origin Y') ;
		Field 'w'  :number() :label('width')  ;
		Field 'h'  :number() :label('height') ;
		'----';
		Field 'reset' :action('reset');
	}

function Quad2D:__init()
	self.ox = 0
	self.oy = 0
	self.w = 0
	self.h = 0
end

function Quad2D:setOrigin( ox, oy )
	self.ox = ox
	self.oy = oy
end

function Quad2D:getOrigin()
	return self.ox, self.oy
end

function Quad2D:createMoaiDeck()
	return MOAIGfxQuad2D.new()
end

function Quad2D:update()
	local deck = self:getMoaiDeck()
	if not self.texture then return end	
	local tex, uv = self.texture:getMoaiTextureUV()
	deck:setTexture( tex )
	deck:setUVRect( unpack( uv ) )

	local w, h = self.w, self.h
	deck:setRect( self.ox - w/2, self.oy - h/2, self.ox + w/2, self.oy + h/2 )
end

function Quad2D:reset()
	if not self.texture then return end	
	local tex, uv = self.texture:getMoaiTextureUV()
	local w, h = self.texture:getSize()
	self.w = w
	self.h = h
	self:update()
end


--------------------------------------------------------------------
CLASS: Tileset ( Deck2D )
	:MODEL {
		Field 'ox'       :int() :label('offset X') ;
		Field 'oy'       :int() :label('offset Y') ;
		Field 'tw'       :int() :label('tile width')  ;
		Field 'th'       :int() :label('tile height') ;
		Field 'spacing'  :int() :label('spacing')  ;
		Field 'reset'    :action();
	}

function Tileset:__init()
	self.ox      = 0
	self.oy      = 0
	self.tw      = 32
	self.th      = 32
	self.col     = 1
	self.row     = 1
	self.spacing = 0
end

function Tileset:createMoaiDeck()
	local deck = MOAITileDeck2D.new()
	return deck
end

function Tileset:reset()
	if not self.texture then return end	
	local tex, uv = self.texture:getMoaiTextureUV()
	local w, h = self.texture:getSize()
	self.w = w
	self.h = h
	self:update()
end


function Tileset:update()
	local texW, texH = self.w, self.h
	local tw, th  = self.tw, self.th
	local ox, oy  = self.ox, self.oy
	local spacing = self.spacing

	if tw < 0 then tw = 1 end
	if th < 0 then th = 1 end

	self.tw = tw
	self.th = th
	local w1, h1   = tw + spacing, th + spacing
	local col, row = math.floor(texW/w1), math.floor(texH/h1)	
	self.col = col
	self.row = row

	if not self.texture then return end	

	local deck = self:getMoaiDeck()
	local tex, uv = self.texture:getMoaiTextureUV()
	local u0,v1,u1,v0 = unpack( uv )
	deck:setTexture( tex )

	local du, dv = u1 - u0, v1 - v0
	deck:setSize(
		col, row, 
		w1/texW * du,      h1/texH * dv,
		ox/texW * du + u0, oy/texH * dv + v0,
		tw/texW * du,      th/texH * dv
		)
	
end

--------------------------------------------------------------------
CLASS: QuadArray ( Deck2D )
	:MODEL {
		Field 'ox'       :int() :label('origin X') ;
		Field 'oy'       :int() :label('origin Y') ;
		Field 'count'    :int();
		'----';
		Field 'offx'     :int() :label('offset X') ;
		Field 'offy'     :int() :label('offset Y') ;
		Field 'tw'       :int() :label('tile width')  ;
		Field 'th'       :int() :label('tile height') ;
		Field 'spacing'  :int() :label('spacing')  ;
		'----';
		Field 'inverseOrder' :boolean();
	}

function QuadArray:__init()
	self.count      = -1
	self.ox      = 0
	self.oy      = 0
	self.offx    = 0
	self.offy    = 0
	self.tw      = 32
	self.th      = 32
	self.col     = 1
	self.row     = 1
	self.spacing = 0
	self.inverseOrder = false
end

function QuadArray:createMoaiDeck()
	local deck = MOAIGfxQuadDeck2D.new()
	return deck
end

function QuadArray:update()
	if not self.texture then return end
	local deck = self:getMoaiDeck()
	local tex, uv = self.texture:getMoaiTextureUV()
	local u0,v0,u1,v1 = unpack( uv )
	deck:setTexture( tex )

	local texW, texH  = self.w, self.h
	local tw,   th    = self.tw, self.th
	local offx, offy  = self.offx, self.offy
	local spacing     = self.spacing

	if tw < 0 then tw = 1 end
	if th < 0 then th = 1 end

	self.tw = tw
	self.th = th
	local w1, h1   = tw + spacing, th + spacing
	local col, row = math.floor(texW/w1), math.floor(texH/h1)	
	
	self.col = col
	self.row = row

	local du, dv = u1 - u0, v1 - v0
	local uu, vv 
	tileU  = tw/texW * du
	tileV  = th/texH * dv
	tileU1 = w1/texW * du
	tileV1 = h1/texH * dv
	offU = offx/texW * du + u0
	offV = offy/texH * dv + v0
	local count = self.count
	if count<=0 then 
		count = col*row		
	end

	deck:reserve( count )
	local ox, oy  = self.ox, self.oy
	for r = 1, row do
		local done = false
		for c = 1, col do
			local i = c + ( r - 1 ) * col
			if i<=count then
				-- done = true
				-- break
				local tu0 = ( c-1 ) * tileU1 + offU
				local tv0 = ( row - r ) * tileV1 + offV
				local tu1 = tu0 + tileU
				local tv1 = tv0 + tileV

				deck:setRect   ( i, ox - tw/2, oy - th/2, ox + tw/2, oy + th/2 )
				deck:setUVRect ( i, tu0, tv0, tu1, tv1 )
			end
		end
		if done then break end
	end

end

--------------------------------------------------------------------

--------------------------------------------------------------------
CLASS: SubQuad ()
	:MODEL {
		Field 'x';
		Field 'y';
		Field 'w';
		Field 'h';
		Field 'u1';
		Field 'v1';
		Field 'u0';
		Field 'v0';
	}

CLASS: QuadList ( Deck2D )
	:MODEL {
		Field 'ox'       :int() :label('origin X') ;
		Field 'oy'       :int() :label('origin Y') ;
		Field 'count'    :int();
	}

function QuadList:__init()
	self.count   = 0
	self.ox      = 0
	self.oy      = 0
	self.quads = {} 
end

function QuadList:createMoaiDeck()
	local deck = MOAIGfxQuadListDeck2D.new()
	return deck
end

function QuadList:clearQuads()
	self.quads = {}
end

function QuadList:addQuad( x0,y0,x1,y1, u0,v0,u1,v1 )
	local q = { x0,y0,x1,y1, u0,v0,u1,v1 } 
	table.insert( self.quads, q )
end

function QuadList:update()
	if not self.texture then return end
	local deck = self:getMoaiDeck()
	local tex, uv = self.texture:getMoaiTextureUV()
	local u0,v0,u1,v1 = unpack( uv )
	deck:setTexture( tex )
	
	local quads = self.quads
	local count = #quads
	if count == 0 then return end
	deck:reserveLists( count )
	deck:reservePairs( count )
	deck:reserveQuads( count )
	deck:reserveUVQuads( count )
	deck:setList( 1, 1, count )

	for i = 1, count do
		local q = quads[ i ]
		local  x0,y0,x1,y1, u0,v0,u1,v1 = unpack( q )
		deck:setRect( i, x0,y0, x1,y1 )
		deck:setUVRect( i, u0,v0, u1,v1 )
		deck:setPair( i, i, i )
	end
end


--------------------------------------------------------------------
CLASS: StretchPatch ( Quad2D )
	:MODEL {
		Field 'left'   :number() :label('border left')   :meta{ min=0, max=1 };
		Field 'right'  :number() :label('border right')  :meta{ min=0, max=1 };
		Field 'top'    :number() :label('border top')    :meta{ min=0, max=1 };
		Field 'bottom' :number() :label('border bottom') :meta{ min=0, max=1 };
	}

function StretchPatch:__init()
	self.ox = 0
	self.oy = 0
	self.w = 0
	self.h = 0

	self.left   = 0.3
	self.right  = 0.3
	self.top    = 0.3
	self.bottom = 0.3

end

function StretchPatch:setOrigin( ox, oy )
	self.ox = ox
	self.oy = oy
end

function StretchPatch:createMoaiDeck()
	local deck = MOAIStretchPatch2D.new()
	deck:reserveRows( 3 )
	deck:reserveColumns( 3 )
	deck:reserveUVRects( 1 )
	deck:setUVRect( 1, 0, 1, 1, 0 )
	return deck
end

function StretchPatch:update()
	local deck = self:getMoaiDeck()

	local tex, uv = self.texture:getMoaiTextureUV()
	deck:setTexture( tex )
	deck:setUVRect( 1, unpack( uv ) )	

	local w, h = self.w, self.h
	deck:setRect( self.ox - w/2, self.oy - h/2, self.ox + w/2, self.oy + h/2 )

	deck:setRow( 1, self.top, false )
	deck:setRow( 3, self.bottom, false )
	deck:setRow( 2, 1 - (self.top+self.bottom), true )

	deck:setColumn( 1, self.left, false )
	deck:setColumn( 3, self.right, false )
	deck:setColumn( 2, 1-(self.left+self.right), true )

	deck.patchWidth = w
	deck.patchHeight = h
end

--------------------------------------------------------------------
--MESH Decks
--------------------------------------------------------------------

local vertexFormat = MOAIVertexFormat.new ()
vertexFormat:declareCoord ( 1, MOAIVertexFormat.GL_FLOAT, 2 )
vertexFormat:declareUV ( 2, MOAIVertexFormat.GL_FLOAT, 2 )
vertexFormat:declareColor ( 3, MOAIVertexFormat.GL_UNSIGNED_BYTE )


CLASS: PolygonDeck ( Deck2D )
	:MODEL{
		Field 'polyline'   :array() :no_edit();		
		Field 'vertexList' :array() :no_edit();		
		Field 'indexList'  :array() :no_edit();		
	}


function PolygonDeck:__init()
	self.polyline   = false
	self.vertexList = {}
	self.indexList  = {}
end

function PolygonDeck:createMoaiDeck()
	local mesh = MOAIMesh.new ()	
	mesh:setPrimType ( MOAIMesh.GL_TRIANGLES )
	return mesh
end

function PolygonDeck:update()
	-- local w, h = self.w, self.h
	-- mesh:setRect( self.ox - w/2, self.oy - h/2, self.ox + w/2, self.oy + h/2 )
	local mesh = self:getMoaiDeck()

	local tex, uv = self.texture:getMoaiTextureUV()
	local u0,v0,u1,v1 = unpack( uv )
	mesh:setTexture( tex )
	
	local us = u1-u0
	local vs = v1-v0

	local vertexList  = self.vertexList
	local vertexCount = #vertexList
	local indexList   = self.indexList
	local indexCount  = #indexList

	local vbo = MOAIVertexBuffer.new ()
	vbo:setFormat ( vertexFormat )
	vbo:reserveVerts ( vertexCount )
	for i = 1, vertexCount, 4 do
		local x, y = vertexList[ i ], vertexList[ i + 1 ]
		local u, v = vertexList[ i + 2 ], vertexList[ i + 3 ]
		vbo:writeFloat ( x, y )
		vbo:writeFloat ( u*us + u0,  v*vs +v0 )
		vbo:writeColor32 ( 1, 1, 1 )
	end
	vbo:bless ()

	-- local ibo = MOAIIndexBuffer.new ()
	-- ibo:reserve ( indexCount )
	-- for i = 1, indexCount, 2 do
	-- 	local a, b = indexList[ i ], indexList[ i + 1 ]
	-- 	ibo:setIndex( i, a, b )
	-- end

	mesh:setVertexBuffer ( vbo )
	-- mesh:setIndexBuffer ( ibo )

end


--------------------------------------------------------------------
--Cylinder
--------------------------------------------------------------------
CLASS: CylinderDeck ( Deck2D )
	:MODEL{
		Field 'radius' ;
		Field 'height' ;
		Field 'span'   :int() :range( 3 );
	}

function CylinderDeck:__init()
	self.radius = 100
	self.height = 100
	self.span = 16
end


function CylinderDeck:createMoaiDeck()
	local mesh = MOAIMesh.new ()	
	mesh:setPrimType ( MOAIMesh.GL_TRIANGLES )
	return mesh
end

function CylinderDeck:update()
	-- local w, h = self.w, self.h
	-- mesh:setRect( self.ox - w/2, self.oy - h/2, self.ox + w/2, self.oy + h/2 )
	local mesh = self:getMoaiDeck()

	local tex, uv = self.texture:getMoaiTextureUV()
	local u0,v0,u1,v1 = unpack( uv )
	mesh:setTexture( tex )
	
	local us = u1-u0
	local vs = v1-v0

	local vertexList  = self.vertexList
	local vertexCount = #vertexList
	local indexList   = self.indexList
	local indexCount  = #indexList

	local vbo = MOAIVertexBuffer.new ()
	vbo:setFormat ( vertexFormat )
	vbo:reserveVerts ( vertexCount )
	for i = 1, vertexCount, 4 do
		local x, y = vertexList[ i ], vertexList[ i + 1 ]
		local u, v = vertexList[ i + 2 ], vertexList[ i + 3 ]
		vbo:writeFloat ( x, y )
		vbo:writeFloat ( u*us + u0,  v*vs +v0 )
		vbo:writeColor32 ( 1, 1, 1 )
	end
	vbo:bless ()

	-- local ibo = MOAIIndexBuffer.new ()
	-- ibo:reserve ( indexCount )
	-- for i = 1, indexCount, 2 do
	-- 	local a, b = indexList[ i ], indexList[ i + 1 ]
	-- 	ibo:setIndex( i, a, b )
	-- end

	mesh:setVertexBuffer ( vbo )
	-- mesh:setIndexBuffer ( ibo )

end

--------------------------------------------------------------------
--PACK
--------------------------------------------------------------------
CLASS: Deck2DPack()
:MODEL{
	Field 'name'  :string();
	Field 'decks' :array( Deck2D ) :no_edit() :sub()
}

function Deck2DPack:__init()
	self.decks = {}
end

function Deck2DPack:getDeck( name )
	for i, deck in ipairs( self.decks ) do
		if deck.name == name then return deck end
	end
	return nil
end

function Deck2DPack:addDeck( name, dtype, src )
	local deck
	if dtype == 'quad' then
		local quad = mock.Quad2D()
		quad:setTexture( src )
		deck = quad
	elseif dtype == 'tileset' then
		local tileset = mock.Tileset()
		tileset:setTexture( src )
		deck = tileset
	elseif dtype == 'stretchpatch' then
		local patch = mock.StretchPatch()
		patch:setTexture( src )
		deck = patch
	elseif dtype == 'quad_array' then
		local qa = mock.QuadArray()
		qa:setTexture( src )
		deck = qa
	elseif dtype == 'polygon' then
		local poly = mock.PolygonDeck()
		poly:setTexture( src )
		deck = poly
	end
	deck.type = dtype
	deck:setName( name )
	table.insert( self.decks, deck )
	return deck
end

function Deck2DPack:removeDeck( deck )
	local idx  = table.index( self.decks, deck )
	if idx then table.remove( self.decks, idx ) end
end

--------------------------------------------------------------------
function Deck2DPackLoader( node )
	local packData   = loadAssetDataTable( node:getObjectFile('def') )
	local pack = deserialize( nil, packData )
	return pack
end

local function Deck2DItemLoader( node )
	local pack = loadAsset( node.parent )
	local name = node:getName()	
	local item = pack:getDeck( name )
	if item then
		item:update()
		node.cached.deckItem = item
		local deck = item:getMoaiDeck()
		return deck
	end
	return nil
end

--------------------------------------------------------------------
registerAssetLoader ( 'deck2d', Deck2DPackLoader )

registerAssetLoader ( 'deck2d.quad',         Deck2DItemLoader )
registerAssetLoader ( 'deck2d.tileset',      Deck2DItemLoader )
registerAssetLoader ( 'deck2d.stretchpatch', Deck2DItemLoader )
registerAssetLoader ( 'deck2d.polygon',      Deck2DItemLoader )
registerAssetLoader ( 'deck2d.quad_array',   Deck2DItemLoader )
