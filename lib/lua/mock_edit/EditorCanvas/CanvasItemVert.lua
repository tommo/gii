module 'mock_edit'

CLASS: CanvasItemVert ( CanvasItem )
	:MODEL{}

function CanvasItemVert:__init()
	self.size = 5
end

function CanvasItemVert:onLoad()
	self:attach( mock.DrawScript() ):setBlend( 'alpha' )
end

function CanvasItemVert:inside( x, y )
	x, y = self:wndToModel( x, y )
	local padding = 4
	return math.abs( x ) <= self.size + padding and math.abs( y ) <= self.size + padding
end

function CanvasItemVert:onDraw()
	local size = self.size
	applyColor 'cp'
	MOAIDraw.fillRect( -size/2, -size/2, size, size )
	-- MOAIDraw.fillCircle( 0, 0, size )
	applyColor 'cp-border'
	MOAIDraw.drawRect( -size/2, -size/2, size, size )
	-- MOAIDraw.drawCircle( 0, 0, size )
end

function CanvasItemVert:onMouseDown( btn, x, y )
	if btn == 'left' then
		x, y = self:wndToWorld( x, y )
		local x0, y0 = self:getLoc()
		self.dragFrom = { x, y, x0, y0 }
	end
end

function CanvasItemVert:onDrag( btn, x, y )
	if btn == 'left' then
		x, y = self:wndToWorld( x, y )
		local dragFrom = self.dragFrom
		local dx, dy = x - dragFrom[ 1 ], y - dragFrom[ 2 ]
		local x1, y1 = dragFrom[3] + dx, dragFrom[ 4 ] + dy
		self:setLoc( x1, y1 )
		self.tool:updateCanvas()	
	end
end

function CanvasItemVert:onMouseUp( btn, x, y )
	print( 'mouse up')
end





