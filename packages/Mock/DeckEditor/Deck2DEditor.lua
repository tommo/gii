--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

CLASS: Deck2DEditor( mock_edit.EditorEntity )

function Deck2DEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
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

--------------------------------------------------------------------
function Deck2DEditor:onMouseMove()
	if not self.currentDeck then return end

	if scn.inputDevice:isMouseDown('right') then
		local dx , dy = scn.inputDevice:getMouseDelta()
		local zoom = scn:getCameraZoom()
		dx = dx/zoom
		dy = dy/zoom
		local ox,oy = self.currentDeck:getOrigin()
		if ox then
			self.currentDeck:setOrigin( ox + dx, oy - dy )
		end
		self:updateDeck()
	end
	if scn.inputDevice:isMouseDown('left') then
	end
end

--------------------------------------------------------------------
function Deck2DEditor:onMouseDown( btn, x, y )
	if btn == 'right' then
	end
end

--------------------------------------------------------------------
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

function Deck2DEditor:addItem( item )
	if not self.editingPack then return end
	local dtype = item['type']
	local src   = item['src']
	local name  = item['name']
	local deck = self.editingPack:addDeck( name, dtype, src )
	return deck
end

function Deck2DEditor:openPack( path )
	local pack = mock.loadAsset( path )
	if not pack then pack = mock.Deck2DPack() end
	self.editingPack = pack
	return pack
end

function Deck2DEditor:savePack( path )
	if not self.editingPack then return end
	mock.serializeToFile( self.editingPack, path )
end

--------------------------------------------------------------------
editor = scn:addEntity( Deck2DEditor() )

function loadAsset( data )
	local modelName = data['model']
	local deck
	if modelName == 'Quad2D' then
		deck = Quad2D()
	elseif modelName == 'Tileset' then
		deck = Tileset()
	elseif modelName == 'StretchPatch' then
		deck = StretchPatch()
	end
	mock.deserialize( deck, data )
	return deck
end

function addItem( item )
	return editor:addItem( item )
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

function renameDeck( deck, name )
	deck:setName( name )
	editor:updateDeck()
end
