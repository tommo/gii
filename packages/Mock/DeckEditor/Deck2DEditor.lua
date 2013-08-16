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
	self.w = 0
	self.h = 0
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
CLASS: Tileset ( Deck2D )
	:MODEL {
		Field 'ox'       :type('int') :label('offset X') ;
		Field 'oy'       :type('int') :label('offset Y') ;
		Field 'tw'       :type('int') :label('tile width')  ;
		Field 'th'       :type('int') :label('tile height') ;
		Field 'spacing'  :type('int') :label('spacing')  ;
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

	local tex = self.texture
	local deck = self:getMoaiDeck()

	local u0,v0,u1,v1 
	if tex.type == 'sub_texture' then
		deck:setTexture( tex.atlas )
		u0,v0,u1,v1 = unpack( tex.uv )
	else
		deck:setTexture( tex )
		u0,v0,u1,v1 = 0, 0, 1, 1
	end
	local du, dv = u1 - u0, v1 - v0
	deck:setSize(
		col, row, 
		w1/texW * du,      h1/texH * dv,
		ox/texW * du + u0, oy/texH * dv + v0,
		tw/texW * du,      th/texH * dv
		)
	
	self.col = col
	self.row = row

end

--------------------------------------------------------------------
CLASS: StretchPatch ( Quad2D )
	:MODEL {
		Field 'left'   :type('number') :label('border left')   :meta{ min=0, max=1 };
		Field 'right'  :type('number') :label('border right')  :meta{ min=0, max=1 };
		Field 'top'    :type('number') :label('border top')    :meta{ min=0, max=1 };
		Field 'bottom' :type('number') :label('border bottom') :meta{ min=0, max=1 };
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

function StretchPatch:moveOrigin( dx, dy )
	self:setOrigin( self.ox + dx, self.oy + dy )	
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
	local tex = self.texture
	if tex.type == 'sub_texture' then
		deck:setTexture( tex.atlas )
		deck:setUVRect( 1, unpack( tex.uv ) )
	else
		deck:setTexture( tex )
		deck:setUVRect( 1, 0, 0, 1, 1 )
	end
	local w, h = self.w, self.h
	deck:setRect( self.ox - w/2, self.oy - h/2, self.ox + w/2, self.oy + h/2 )

	deck:setRow( 1, self.top, false )
	deck:setRow( 3, self.bottom, false )
	deck:setRow( 2, 1 - (self.top+self.bottom), true )

	deck:setColumn( 1, self.left, false )
	deck:setColumn( 3, self.right, false )
	deck:setColumn( 2, 1-(self.left+self.right), true )

end

--------------------------------------------------------------------
CLASS: Deck2DEditor( mock.Entity )

function Deck2DEditor:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )

	self.currentDeck = false
	self.preview = self:addProp{}
	self.previewGrid = MOAIGrid.new()
end

function Deck2DEditor:selectDeck( deck )
	self.currentDeck = deck
	if deck.type == 'tileset' then
		self.preview:setGrid( self.previewGrid )
	else
		self:detach( self.preview )
		self.preview = self:addProp{}
	end
	if deck.type == 'stretchpatch' then
		self.preview:setScl( 2, 2, 2 )
	end
	self.preview:setDeck( deck and deck:getMoaiDeck() )	
	self:updateDeck()
end

function Deck2DEditor:updateDeck( )
	local deck = self.currentDeck
	self.currentDeck:update()
	if deck.type == 'tileset' then		
		local grid = self.previewGrid
		local col, row = deck.col, deck.row
		local tw , th  = deck.tw , deck.th
		local sp = deck.spacing
		grid:setSize( col, row, tw + sp, th + sp, 0, 0, tw, th)
		local t = 1
		for j = row, 1, -1 do
			for i = 1, col do
				grid:setTile( i, j, t )
				t=t+1
			end
		end
	end
	self.preview:forceUpdate()
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
	if not self.currentDeck then return end

	if scn.inputDevice:isMouseDown('right') then
		local dx , dy = scn.inputDevice:getMouseDelta()
		local zoom = scn:getCameraZoom()
		dx = dx/zoom
		dy = dy/zoom
		self.currentDeck:moveOrigin( dx, - dy )
		self:updateDeck()
	end
	if scn.inputDevice:isMouseDown('left') then
	end
end

function Deck2DEditor:onMouseDown( btn, x, y )
	if btn == 'right' then

	end
end

function Deck2DEditor:onDraw()
	local deck = self.currentDeck
	if not deck then return end
	if deck.type == 'tileset' then
		local col, row = deck.col, deck.row
		local tw , th  = deck.tw , deck.th
		local sp = deck.spacing
		MOAIGfxDevice.setPenColor(0,1,0,0.3)
		for i = 0, col-1 do
			for j = 0, row-1 do
				local x , y
				x = i * (tw + sp)
				y = j * (th + sp)
				MOAIDraw.drawRect( x, y, x+tw, y+th )
			end
		end
		return
	end

	MOAIGfxDevice.setPenColor(0,1,0,0.4)
	local x0,y0,z0, x1,y1,z1 = self.preview:getWorldBounds()
	MOAIDraw.drawRect(x0,y0,x1,y1)

	if deck.type == 'stretchpatch' then
		MOAIGfxDevice.setPenColor(1,0,0,0.4)
		local extent = 20
		local r1,r3 = deck.top * deck.h,  deck.bottom * deck.h
		local c1,c3 = deck.left * deck.w, deck.right * deck.w

		--rows
		-- local y= y0 ;      MOAIDraw.drawLine( x0-extent, y, x1+extent, y )
		local y= r1 + y0;  MOAIDraw.drawLine( x0-extent, y, x1+extent, y )
		local y= y1 - r3;  MOAIDraw.drawLine( x0-extent, y, x1+extent, y )
		-- local y= y1 ;      MOAIDraw.drawLine( x0-extent, y, x1+extent, y )

		--columns
		-- local x= x0 ;      MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
		local x= c1 + x0;  MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
		local x= x1 - c3;  MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
		-- local x= x1 ;      MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
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
		deck = quad
	elseif dtype == 'tileset' then
		local tileset = Tileset()
		tileset:setTexture( src )
		deck = tileset
	elseif dtype == 'stretchpatch' then
		local patch = StretchPatch()
		patch:setTexture( src )
		deck = patch
	end

	deck:setName( name )
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
