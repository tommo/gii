module 'mock_edit'

--------------------------------------------------------------------
CLASS: CanvasItemCircle ( CanvasItem )

function CanvasItemCircle:__init()
	self.radius = 0
end

function CanvasItemCircle:onLoad()
	self.vertC = self:addSubItem( CanvasItemVert() )
	self.vertR = self:addSubItem( CanvasItemVert() )
	linkLoc( self:getProp(), self.vertC:getProp() )

	self.vertC.onMove = function( vert ) return self:onVertMove( 'C' ) end
	self.vertR.onMove = function( vert ) return self:onVertMove( 'R' ) end
	self.vertC:setShape( 'circle' )
	self.drawScript = self:attach( mock.DrawScript() )
	self.drawScript:setBlend( 'alpha' )
end

function CanvasItemCircle:isConstantSize()
	return false
end

function CanvasItemCircle:onDraw()
	applyColor 'shape-line'
	MOAIDraw.drawCircle( 0,0, self.radius )
end

function CanvasItemCircle:onVertMove( id )
	local vertC = self.vertC
	local vertR = self.vertR
	if id == 'C' then
		local x0, y0 = vertC:getLoc()
		return self:setShape( x0, y0, self.radius, true )
	elseif id == 'R' then
		local x0, y0 = vertC:getLoc()
		local xr = vertR:getLocX()
		local radius = xr - x0
		self.radius = radius
		return self:setShape( x0, y0, radius, true )
	end
end

function CanvasItemCircle:updateShape()
	local x,y,radius = self:onPullAttr()
	if not x then return end
	return self:setShape( x, y, radius, false )
end

function CanvasItemCircle:setShape( x, y, radius, notify )
	self.vertC:setLoc( x, y )
	self.vertR:setLoc( x + radius, y )
	self.radius = radius
	self.drawScript:setBounds( -radius, -radius,0,radius,radius,0 )
	if notify ~= false then
		self:onPushAttr( x, y, radius )
	end
end

function CanvasItemCircle:onPullAttr()
	return nil
end

function CanvasItemCircle:onPushAttr( x, y, radius )
end
