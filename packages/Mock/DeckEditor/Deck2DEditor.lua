--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

CLASS: Deck2D ()
	:MODEL {
		Field 'name'     :type('string')    :getset('Name') ;
		Field 'texture'  :asset('texture')  :getset('Texture');		
	}

function Deck2D:__init()
	self._deck = self:createMoaiDeck()
end

function Deck2D:setTexture( path )
	local tex = mock.loadAsset( path )
	local w, h = tex:getSize()
	self.w = w
	self.h = h
	self.texturePath = path
	self.texture = tex
	self:update()
end

function Deck2D:getTexture()
	return self.texturePath
end

function Deck2D:setName( n )
	self.name = n
end

function Deck2D:getName()
	return self.name
end

function Deck2D:setOrigin( dx, dy )

end

function Deck2D:moveOrigin( dx, dy )

end

function Deck2D:getMoaiDeck()	
	return self._deck
end

function Deck2D:createMoaiDeck()
end

function Deck2D:update()
end

--------------------------------------------------------------------
CLASS: Tileset ( Deck2D )
	:MODEL {
		Field 'ox' :type('number') :label('offset X') ;
		Field 'oy' :type('number') :label('offset Y') ;
		Field 'tw'  :type('number') :label('tile width')  ;
		Field 'th'  :type('number') :label('tile height') ;
	}

function Tileset:createMoaiDeck()
	local deck = MOAITileDeck2D.new()
	return deck
end
--------------------------------------------------------------------
CLASS: Quad2D ( Deck2D )
	:MODEL{
		Field 'ox' :type('number') :label('offset X') ;
		Field 'oy' :type('number') :label('offset Y') ;
		Field 'w'  :type('number') :label('width')  ;
		Field 'h'  :type('number') :label('height') ;
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

function Quad2D:moveOrigin( dx, dy )
	self:setOrigin( self.ox + dx, self.oy + dy )	
end

function Quad2D:createMoaiDeck()
	return MOAIGfxQuad2D.new()
end

function Quad2D:update()
	local deck = self:getMoaiDeck()
	local tex = self.texture
	if tex.type == 'sub_texture' then
		deck:setTexture( tex.atlas )
		deck:setUVRect( unpack( tex.uv ) )
	else
		deck:setTexture( tex )
		deck:setUVRect( 0, 0, 1, 1 )
	end
	local w, h = self.w, self.h
	deck:setRect( self.ox - w/2, self.oy - h/2, self.ox + w/2, self.oy + h/2 )
end

--------------------------------------------------------------------
CLASS: Deck2DEditor( mock.Entity )

function Deck2DEditor:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self.currentDeck = false
	self.preview = self:addProp{}
end

function Deck2DEditor:selectDeck( deck )
	self.preview:setDeck( deck and deck:getMoaiDeck() )	
	self.preview:forceUpdate()
	self.currentDeck = deck
end

function Deck2DEditor:updateDeck( )
	self.currentDeck:update()
	updateCanvas()
	updateEditor()
end

function Deck2DEditor:setOrigin( direction )
	if not self.currentDeck then return end
	local x0,y0,z0, x1,y1,z1 = self.preview:getBounds()
	local w, h =x1-x0, y1-y0
	x0,x1 = -w/2, w/2
	y0,y1 = h/2, -h/2
	local ox, oy
	if     direction == 'E'  then
		ox, oy = x1,  0
	elseif direction == 'W'  then
		ox, oy = x0,  0
	elseif direction == 'N'  then
		ox, oy = 0,  y0
	elseif direction == 'S'  then
		ox, oy = 0,  y1
	elseif direction == 'SE' then
		ox, oy = x1,  y1
	elseif direction == 'SW' then
		ox, oy = x0,  y1
	elseif direction == 'NE' then
		ox, oy = x1,  y0
	elseif direction == 'NW' then
		ox, oy = x0,  y0
	elseif direction == 'C' then
		ox, oy = 0, 0
	else
		ox, oy = 0, 0
	end
	self.currentDeck:setOrigin( ox, oy )
	self:updateDeck()
end

function Deck2DEditor:onMouseMove()
	if scn.inputDevice:isMouseDown('right') then
		local dx , dy = scn.inputDevice:getMouseDelta()
		if self.currentDeck then
			local zoom = scn:getCameraZoom()
			dx = dx/zoom
			dy = dy/zoom
			self.currentDeck:moveOrigin( dx, - dy )
			self:updateDeck()
		end
	end
end

function Deck2DEditor:onMouseDown( btn, x, y )
	if btn == 'right' then

	end
end

--------------------------------------------------------------------
editor = scn:addEntity( Deck2DEditor() )

function openAsset( path )

end

function addItem( item )
	local dtype = item['type']
	local src   = item['src']
	local name  = item['name']
	local deck
	if dtype == 'quad' then
		local quad = Quad2D()
		quad:setTexture( src )
		quad:setName( name )
		deck = quad
	end

	if dtype == 'tileset' then
		local tileset = Tileset()
		tileset:setTexture( src )
		tileset:setName( name )
		deck = tileset
	end
	deck.type = dtype
	return deck
end

function setOrigin( direction )
	editor:setOrigin( direction )	
end

function selectDeck( deck )
	editor:selectDeck( deck )
end

function updateDeck( )
	editor:updateDeck()
end
