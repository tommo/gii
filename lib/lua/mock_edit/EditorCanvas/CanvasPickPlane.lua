module 'mock_edit'

CLASS: CanvasPickPlane ( CanvasItem )
	:MODEL{}

function CanvasPickPlane:__init()
	self.picking = false
	self.pickingFrom = false
	self.x0 = 0
	self.y0 = 0
	self.x1 = 0
	self.y1 = 0
end

function CanvasPickPlane:onLoad()
	self:attach( mock.DrawScript() ):setBlend( 'alpha' )
end

function CanvasPickPlane:inside()
	return true
end

function CanvasPickPlane:onDraw()
	local x0 = self.x0
	local y0 = self.y0
	local x1 = self.x1
	local y1 = self.y1
	MOAIGfxDevice.setPenColor( 0.4,.5,1,0.2 )
	MOAIDraw.fillRect( x0,y0,x1,y1 )
	MOAIGfxDevice.setPenColor( 0.4,.5,1,1 )
	MOAIDraw.drawRect( x0,y0,x1,y1 )
end

function CanvasPickPlane:onMouseDown( btn, x, y )
	if btn ~= 'left' then return end
	local view = self:getView()
	x, y = view:wndToWorld( x, y )
	self.x0 = x
	self.y0 = y
	self.x1 = x 
	self.y1 = y
	self.picking = true
	self:setVisible( true )	
	self:getView():updateCanvas()
end

function CanvasPickPlane:onDrag( btn, x, y )
	if not self.picking then return end
	local view = self:getView()
	x, y = view:wndToWorld( x, y )
	self.x1 = x
	self.y1 = y
	self:getView():updateCanvas()
end

function CanvasPickPlane:onMouseUp( btn )
	if btn == 'left' and self.picking then
		self.picking = false
		self:setVisible( false )
		self:getView():updateCanvas()

		local x, y = self.x0, self.y0
		local picked = self:getView():pick( x, y )
		if self.onPicked then
			return self.onPicked( picked )
		end		
		
	end
end

function CanvasPickPlane:setPickCallback( cb )
	self.onPicked = cb
end

function CanvasPickPlane:isConstantSize()
	return false
end
