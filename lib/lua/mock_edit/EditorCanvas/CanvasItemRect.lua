module 'mock_edit'

--------------------------------------------------------------------
CLASS: CanvasItemRect ( CanvasItem )

function CanvasItemRect:__init()
	self.size = { 0, 0 }
	self.rot = 0
end

function CanvasItemRect:onLoad()
	self.vertC = self:addSubItem( CanvasItemVert() )
	
	self.vertT = self:addSubItem( CanvasItemVert() )
	self.vertL = self:addSubItem( CanvasItemVert() )
	self.vertR = self:addSubItem( CanvasItemVert() )
	self.vertB = self:addSubItem( CanvasItemVert() )

	self.vertLT = self:addSubItem( CanvasItemVert() )
	self.vertRT = self:addSubItem( CanvasItemVert() )
	self.vertLB = self:addSubItem( CanvasItemVert() )
	self.vertRB = self:addSubItem( CanvasItemVert() )

	self.vertC.onMove = function( vert ) return self:onVertMove( 'C', vert ) end
	self.vertC:setShape( 'circle' )

	self.vertT.onMove = function( vert ) return self:onVertMove( 'T', vert ) end
	self.vertL.onMove = function( vert ) return self:onVertMove( 'L', vert ) end
	self.vertR.onMove = function( vert ) return self:onVertMove( 'R', vert ) end
	self.vertB.onMove = function( vert ) return self:onVertMove( 'B', vert ) end
	self.vertLT.onMove = function( vert ) return self:onVertMove( 'LT', vert ) end
	self.vertRT.onMove = function( vert ) return self:onVertMove( 'RT', vert ) end
	self.vertLB.onMove = function( vert ) return self:onVertMove( 'LB', vert ) end
	self.vertRB.onMove = function( vert ) return self:onVertMove( 'RB', vert ) end

	linkLoc( self:getProp(), self.vertC:getProp() )

	self.drawScript = self:attach( mock.DrawScript() )
	self.drawScript:setBlend( 'alpha' )
end

function CanvasItemRect:isConstantSize()
	return false
end

function CanvasItemRect:onDraw()
	applyColor 'shape-line'
	local w, h = self:getSize()
	MOAIDraw.drawRect( -w/2, -h/2, w/2, h/2 )
end

function CanvasItemRect:getSize()
	return unpack( self.size )
end

function CanvasItemRect:onVertMove( id, vert )
	local vertC = self.vertC

	if id == 'C' then
		local x0, y0 = vertC:getLoc()
		local w, h = self:getSize()
		local rot  = 0
		return self:setShape( x0, y0, w, h ,0, true )
	else
		local x0, x1 = self.vertL:getLocX() , self.vertR:getLocX()
		local y0, y1 = self.vertB:getLocY() , self.vertT:getLocY()
		if id == 'LT' then
			x0 = vert:getLocX()
			y1 = vert:getLocY()
		elseif id == 'RT' then
			x1 = vert:getLocX()
			y1 = vert:getLocY()
		elseif id == 'LB' then
			x0 = vert:getLocX()
			y0 = vert:getLocY()
		elseif id == 'RB' then
			x1 = vert:getLocX()
			y0 = vert:getLocY()
		end
		local xc,yc = (x0+x1)/2, (y0+y1)/2
		local w, h = math.max( x1 - x0, 0 ), math.max( y1 - y0, 0 )
		
		return self:setShape( xc, yc, w, h, 0, true )
	end
end

function CanvasItemRect:updateShape()
	local x, y, w, h, rot = self:onPullAttr()
	if not x then return end
	return self:setShape( x, y, w, h, rot )
end

function CanvasItemRect:setShape( x, y, w, h, rot, notify )
	-- local ent = shape._entity
	self.vertC:setLoc( x +    0, y + 0    )

	self.vertT:setLoc( x +    0, y +  h/2 )
	self.vertB:setLoc( x +    0, y + -h/2 )
	self.vertL:setLoc( x + -w/2, y + 0    )
	self.vertR:setLoc( x +  w/2, y + 0    )

	self.vertLT:setLoc( x + -w/2, y +  h/2 )
	self.vertRT:setLoc( x +  w/2, y +  h/2 )
	self.vertLB:setLoc( x + -w/2, y + -h/2 )
	self.vertRB:setLoc( x +  w/2, y + -h/2 )

	self.drawScript:setBounds( -w/2, -h/2,0, w/2,h/2,0 )
	self.size = { w, h }
	self.rot  = rot
	if notify ~= false then
		self:onPushAttr( x, y, w, h, rot or 0 )
	end
end

function CanvasItemRect:onPullAttr()
	return nil
end

function CanvasItemRect:onPushAttr( x, y, w, h, rot )
end
