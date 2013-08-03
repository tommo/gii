
-----------
context        = false
camScl         = 1
----------
targetType     = false
currentSprite  = false
currentDeck    = false
currentTex     = false

-------COMMON
prop           = false
originX        = 0
originY        = 0
deckWidth      = 0
deckHeight     = 0

-------STRETCH PATCH
row1           = .25
row2           = .50
row3           = .25
col1           = .25
col2           = .50
col3           = .25
----------
patchSclX      = 1
patchSclY      = 2

----TILESET
tileWidth      = 32
tileHeight     = 32
gutter         = 0
offsetX        = 0
offsetY        = 0
tileCol        = 0
tileRow        = 0
local getDict = gii.getDict

function onLoad()
	context = gii.createEditCanvasContext()
	context:addDrawScript(drawGrid, {priority=-100})
	context:addDrawScript(drawGizmo, {priority=100})

	-- context.layer:showDebugLines( true )
	-- MOAIDebugLines.setStyle ( MOAIDebugLines.PROP_WORLD_BOUNDS, 1, 0, 1, .2, .2 )
end

function onResize(w,h)
	context:resize(w,h)	
end

function selectItem( item )
	local deckType  = item.type
	local texPath   = item.tex
	local tex, node = mock.loadAsset( texPath )
	if not tex then tex = mock.getTexturePlaceHolder() end

	targetType = deckType

	if prop then 
		context:removeProp(prop)
		prop = false
	end

	prop = MOAIProp.new()
	prop:setBlendMode( 
		MOAIProp.GL_SRC_ALPHA, 
		MOAIProp.GL_ONE_MINUS_SRC_ALPHA
		) 
	context:insertProp(prop)
	local sub = tex.type == 'sub_texture'
	local uv = false
	if sub then
		uv = tex.uv
		tex = tex.atlas
	end
	if deckType == 'quad' then
		local deck = MOAIGfxQuad2D.new()
		deck:setTexture( tex )
		prop:setDeck( deck )
		prop:setGrid( nil )
		local w, h = tex:getSize()
		deckWidth  = w
		deckHeight = h
		currentDeck = deck
		currentTex  = tex
		if sub then
			deck:setUVRect( unpack( uv ) )
		end

	elseif deckType == 'stretchpatch' then
		local deck = MOAIStretchPatch2D.new()
		deck:setTexture( tex )
		deck:reserveRows( 3 )
		deck:reserveColumns( 3 )
		deck:reserveUVRects ( 1 )
		if sub then
			deck:setUVRect( unpack( uv ) )
		else
			deck:setUVRect ( 1, 0, 1, 1, 0 )
		end
		prop:setDeck(deck)
		prop:setGrid(nil)
		local w, h = tex:getSize()
		deckWidth  = w
		deckHeight = h
		currentDeck = deck
		currentTex  = tex

	elseif deckType == 'tileset' then
		local w, h = tex:getSize()
		currentDeck = MOAITileDeck2D.new()
		deckWidth  = w
		deckHeight = h
		currentTex = tex
		if sub then
			deck:setUVRect( unpack( uv ) )
		end
	end

	updateItemFromEditor( item )
	prop:forceUpdate()
	updateEditor()
end

function drawGrid()
	-- local w,h = context:getSize()
	w=1000
	h=1000
	--draw origin axis
	MOAIGfxDevice.setPenColor(.5,.5,.5,0.5)
	MOAIDraw.drawLine(-w/2, 0, w/2, 0)
	MOAIDraw.drawLine(0, -h/2, 0, h/2)
end

function drawGizmo()
	if not prop then return end
	local vw,vh = context:getSize()
	--tileset only
	if targetType == 'tileset' then
		MOAIGfxDevice.setPenColor(0,1,0,0.3)
		for i = 0, tileCol-1 do
			for j = 0, tileRow-1 do
				local x,y
				x = i * (tileWidth + 3)  
				y = j * (tileHeight + 3)
				MOAIDraw.drawRect( x, y, x+tileWidth, y+tileHeight )
			end
		end
		return
	end

	--draw bounds
	MOAIGfxDevice.setPenColor(0,1,0,0.5)
	local x0,y0,z0, x1,y1,z1 = prop:getWorldBounds()
	MOAIDraw.drawRect(x0,y0,x1,y1)

	if targetType == 'stretchpatch' then
		local dw, dh = deckWidth, deckHeight
		local vw, vh = x1-x0, y1-y0
		MOAIGfxDevice.setPenColor(1,0,0,0.5)
		--draw slice lines
		local extent = 20
		local r1,r3 = row1 * dh, row3 * dh
		local c1,c3 = col1 * dw, col3 * dw

		--rows
		local y= y0 ;      MOAIDraw.drawLine( x0-extent, y, x1+extent, y )
		local y= r1 + y0;  MOAIDraw.drawLine( x0-extent, y, x1+extent, y )
		local y= y1 - r3;  MOAIDraw.drawLine( x0-extent, y, x1+extent, y )
		local y= y1 ;      MOAIDraw.drawLine( x0-extent, y, x1+extent, y )

		--columns
		local x= x0 ;      MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
		local x= c1 + x0;  MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
		local x= x1 - c3;  MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
		local x= x1 ;      MOAIDraw.drawLine( x, y0-extent, x, y1+extent )
	end

	
end

function setOrigin( direction )
	local x0,y0,z0, x1,y1,z1 = prop:getBounds()
	local w, h =x1-x0, y1-y0
	x0,x1 = -w/2, w/2
	y0,y1 = h/2, -h/2

	if     direction == 'E'  then
		originX, originY = x1,  0
	elseif direction == 'W'  then
		originX, originY = x0,  0
	elseif direction == 'N'  then
		originX, originY = 0,  y0
	elseif direction == 'S'  then
		originX, originY = 0,  y1
	elseif direction == 'SE' then
		originX, originY = x1,  y1
	elseif direction == 'SW' then
		originX, originY = x0,  y1
	elseif direction == 'NE' then
		originX, originY = x1,  y0
	elseif direction == 'NW' then
		originX, originY = x0,  y0
	elseif direction == 'C' then
		originX, originY = 0, 0
	end

	updateItem()
	updateEditor()
end

function updateItemFromEditor( item, key, value )
	originX = getDict( item, 'ox', 0 )
	originY = getDict( item, 'oy', 0 )

	if targetType == 'quad' then
		width = getDict( item, 'width',  -1 )
		height = getDict( item, 'height', -1 )

	elseif targetType =='tileset' then
		tileWidth  = getDict( item, 'width',  32 )
		tileHeight = getDict( item, 'height', 32 )
		gutter     = getDict( item, 'gutter',  0 )
		offsetX    = getDict( item, 'offsetX', 0 )
		offsetY    = getDict( item, 'offsetY', 0 )

	elseif targetType == 'stretchpatch' then
		row1 = getDict(item, 'row1', 0.25)
		row2 = getDict(item, 'row2', 0.5)
		row3 = getDict(item, 'row3', 0.25)
		col1 = getDict(item, 'col1', 0.25)
		col2 = getDict(item, 'col2', 0.5)
		col3 = getDict(item, 'col3', 0.25)
	end

	updateItem()
end

function updateItem( )
	if not currentDeck then return end
	local tex  = currentTex
	local deck = currentDeck
	local ox, oy = originX, originY
	if targetType =='tileset' then
		local tw, th   = deckWidth, deckHeight
		local w, h     = tileWidth, tileHeight
		
		if w<0 then w=1 end
		if h<0 then h=1 end

		tileWidth, tileHeight = w, h
		local w1, h1   = w + gutter, h + gutter
		local col, row = math.floor(tw/w1), math.floor(th/h1)
		tileCol, tileRow = col, row
		currentGrid = MOAIGrid.new()
		currentDeck = MOAITileDeck2D.new()
		currentDeck:setTexture( currentTex )
		currentDeck:setSize( col, row, 
			w1/tw, h1/th, 
			offsetX/tw, offsetY/th,
			w/tw, h/th
			)
		currentGrid:setSize( col, row, w + 3, h + 3, 0, 0, w, h)
		prop:setGrid( currentGrid )
		prop:setDeck( currentDeck )
		local t = 1
		for j = row, 1, -1 do
			for i = 1, col do
				currentGrid:setTile( i, j, t )
				t=t+1
			end
		end

	elseif targetType == 'quad' then
		local w,  h  = deckWidth, deckHeight
		deck:setRect( -w/2+ox, -h/2+oy, w/2+ox, w/2+oy )
	elseif targetType == 'stretchpatch' then
		local w,  h  = deckWidth, deckHeight
		deck:setRect( -w/2+ox, -h/2+oy, w/2+ox, w/2+oy )
		deck:setRow( 1, row1, false )
		deck:setRow( 2, row2, true )
		deck:setRow( 3, row3, false )
		deck:setColumn( 1, col1, false )
		deck:setColumn( 2, col2, true )
		deck:setColumn( 3, col3, false )
	end
	prop:forceUpdate()
	_owner:updateCanvas()	
end

stretching     = false
draggingOrigin = false
padding        = false

px0, py0 =0,0
function onMouseDown( btn, x, y )
	if btn == 'right' then
		draggingOrigin = true 
		pressX, pressY = context:wndToWorld( x, y )
		originX0, originY0 = originX, originY
	end
	if btn == 'left' then
		stretching = true
	end
	if btn == 'middle' then
		padding = true
		px0, py0 = x, y
	end
end

function onMouseUp( btn )
	if btn == 'right' then
		draggingOrigin = false
	end
	if btn == 'left' then
		stretching = false
		prop:setScl(1 ,1)
		prop:forceUpdate()
		_owner:updateCanvas()
	end
	if btn == 'middle' then
		padding = false
	end
end

function onMouseMove( x, y )
	if draggingOrigin then
		x, y = context:wndToWorld( x, y )
		local dx, dy = x - pressX, y - pressY
		originX = originX0 + dx
		originY = originY0 + dy
		updateItem()
		updateEditor()
		
	end
	if stretching and targetType == 'stretchpatch' then
		x, y = context:wndToWorld( x, y )
		patchSclX = math.abs(x) /20
		patchSclY = math.abs(y) /20
		prop:setScl(patchSclX, patchSclY)
		prop:forceUpdate()
		_owner:updateCanvas()
		-- updateItem()
	end
	if padding then
		local dx,dy=x-px0,y-py0
		px0=x
		py0=y
		
		dx = dx*camScl
		dy = dy*camScl

		context.camera:addLoc( -dx, dy )
		_owner:updateCanvas()
	end
end

function onKeyDown( key )
	if not draggingOrigin then
		if     key=='up'    then originY = originY + 1
		elseif key=='down'  then originY = originY - 1
		elseif key=='left'  then originX = originX - 1
		elseif key=='right' then originX = originX + 1
		else
			return
		end
		updateItem()
		updateEditor()
	end
end


function onScroll(dx,dy,x,y)
	camScl = camScl - dy *0.1
	if camScl<0.1 then camScl = 0.1 end
	if camScl>4 then camScl = 4 end
	context:setCameraScl( camScl )
	_owner:updateCanvas()
end