module 'mock_edit'

--------------------------------------------------------------------
local handleSize = 100
local handleArrowSize = 20

--------------------------------------------------------------------
---Translation Tool
--------------------------------------------------------------------
CLASS: TranslationHandle( CanvasHandle )
function TranslationHandle:__init( option )
	self.option = option
	self.activeAxis = false
end

function TranslationHandle:onLoad()
	local option = self.option
	self:attach( mock.DrawScript() )	
end

function TranslationHandle:onDraw()	
	applyColor 'handle-all'
	MOAIDraw.fillRect( 0,0, handleArrowSize, handleArrowSize )
	--x axis
	applyColor 'handle-x'
	MOAIDraw.drawLine( 0,0, handleSize, 0 )
	MOAIDraw.fillFan(
		handleSize,  handleArrowSize/3, 
		handleSize + handleArrowSize, 0,
		handleSize, -handleArrowSize/3
		-- handleSize,  handleArrowSize/3
		)
	-- MOAIDraw.fillFan( 0,0, handleSize / 5, handleSize / 5 )
	--y axis
	applyColor 'handle-y'
	MOAIDraw.drawLine( 0,0, 0, handleSize )
	MOAIDraw.fillFan(
		handleArrowSize/3, handleSize, 
		0, handleSize + handleArrowSize,
		-handleArrowSize/3, handleSize 
		-- handleArrowSize/3, handleSize, 
		)
end

function TranslationHandle:wndToTarget( x, y )
	local x, y = self:wndToWorld( x, y )
	if self.target then 
		local parent = self.target.parent
		if parent then
			return parent:worldToModel( x, y )
		end
	end
	return x, y
end

function TranslationHandle:setTarget( target )
	self.target = target
	inheritLoc( self:getProp(), target:getProp() )
end

function TranslationHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	self.x0, self.y0 = self:wndToTarget( x, y )	
	x, y = self:wndToModel( x, y )
	if x >= 0 and y >= 0 and x <= handleArrowSize + 5 and y <= handleArrowSize + 5 then
		self.activeAxis = 'all'
		return true
	end
	if math.abs( y ) < 5 and x <= handleSize + handleArrowSize then
		self.activeAxis = 'x'
		return true
	end
	if math.abs( x ) < 5 and y <= handleSize + handleArrowSize then
		self.activeAxis = 'y'
		return true
	end
end

function TranslationHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.activeAxis then return end
	self.activeAxis = false
	return true
end

function TranslationHandle:onMouseMove( x, y )
	if not self.activeAxis then return end
	local target = self.target
	target:forceUpdate()
	self:forceUpdate()
	x, y = self:wndToTarget( x, y )
	local dx = x - self.x0
	local dy = y - self.y0
	self.x0, self.y0 = x, y 
	local tx, ty = self.target:getLoc()
	
	local mode = 'global'
	local parent = target.parent
	if parent and mode == 'global' then
		local wx, wy   = target:getWorldLoc( 0,0,0 )
		local wx1, wy1 = parent:modelToWorld( tx + dx, ty + dy )
		if self.activeAxis == 'all' then
			--pass			
		elseif self.activeAxis == 'x' then
			wy1 = wy
		elseif self.activeAxis == 'y' then
			wx1 = wx
		end
		tx, ty = parent:worldToModel( wx1, wy1 )
	else
		if self.activeAxis == 'all' then
			tx = tx + dx
			ty = ty + dy
		elseif self.activeAxis == 'x' then
			tx = tx + dx
		elseif self.activeAxis == 'y' then
			ty = ty + dy
		end
	end
	target:setLoc( tx, ty )
	self:updateCanvas()
	return true
end


--------------------------------------------------------------------
---ROTATION
--------------------------------------------------------------------

CLASS: RotationHandle( mock_edit.CanvasHandle )
function RotationHandle:__init( option )
	self.option = option
	self.align  = false
	self.active = false
end

function RotationHandle:onLoad()
	self:attach( mock.DrawScript() )
end

function RotationHandle:setTarget( target )
	self.target = target
	inheritLoc( self:getProp(), target:getProp() )
	self.r0 = target:getRotZ()
end

function RotationHandle:onDraw()
	if self.active then
		applyColor 'handle-active'
	else
		applyColor 'handle-z'
	end
	MOAIDraw.fillCircle( 0, 0, 5 )
	MOAIDraw.drawCircle( 0, 0, 80 )
	local r = self.target:getRotZ()	
	MOAIDraw.drawLine( 0,0, vecAngle( r, 80 ) )
	if self.active then
		applyColor 'handle-previous'
		MOAIDraw.drawLine( 0,0, vecAngle( self.r0, 80 ) )
	end
end

function RotationHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	local x1, y1 = self:wndToModel( x, y )
	local r = distance( 0,0, x1,y1 )
	if r > 80 then return end
	local rx,ry,rz = self.target:getRot()
	self.rot0 = rz
	self.dir0 = direction( 0,0, x1,y1 )
	self.active = true
	self.r0 = self.target:getRotZ()
	self:updateCanvas()
	return true
end

function RotationHandle:onMouseMove( x, y )
	if not self.active then return end
	local x1, y1 = self:wndToModel( x, y )
	local r = distance( 0,0, x1,y1 )
	if r>5 then
		local dir = direction( 0,0, x1,y1)
		local ddir = dir - self.dir0
		local rx,ry,rz = self.target:getRot()
		rz = self.rot0 + ddir * 180/math.pi
		self.target:setRot( rx, ry, rz )
		gii.emitPythonSignal( 'entity.modified', self.target, 'view' )
		self:updateCanvas()
	end
	return true
end

function RotationHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.active then return end
	self.active = false
	self:updateCanvas()
	return true
end

--------------------------------------------------------------------
---SCALE Handle
--------------------------------------------------------------------
CLASS: ScaleHandle( CanvasHandle )
function ScaleHandle:__init( option )
	self.option = option
	self.activeAxis = false
end

function ScaleHandle:onLoad()
	local option = self.option
	self:attach( mock.DrawScript() )	
end

function ScaleHandle:onDraw()
	applyColor 'handle-all'
	MOAIDraw.fillRect( 0, 0, handleArrowSize, handleArrowSize )
	--x axis
	applyColor 'handle-x'
	MOAIDraw.drawLine( 0, 0, handleSize, 0 )
	MOAIDraw.fillRect( handleSize,0, handleSize + handleArrowSize, handleArrowSize )
	--y axis
	applyColor 'handle-y'
	MOAIDraw.drawLine( 0, 0, 0, handleSize )
	MOAIDraw.fillRect( 0, handleSize, handleArrowSize, handleSize + handleArrowSize )
end

function ScaleHandle:setTarget( target )
	self.target = target
	inheritLoc( self:getProp(), target:getProp() )
end

function ScaleHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end	
	self.x0 = x
	self.y0 = y
	x,y = self:wndToModel( x, y )
	self.sx, self.sy, self.sz = self.target:getScl()

	if x >= -5 and y >= -5 and x <= handleArrowSize + 5 and y <= handleArrowSize + 5 then
		self.activeAxis = 'all'
		return true
	end
	if math.abs( y ) < 5 and x <= handleSize + handleArrowSize then
		self.activeAxis = 'x'
		return true
	end
	if math.abs( x ) < 5 and y <= handleSize + handleArrowSize then
		self.activeAxis = 'y'
		return true
	end
end

function ScaleHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.activeAxis then return end
	self.activeAxis = false
	return true
end

function ScaleHandle:onMouseMove( x, y )
	if not self.activeAxis then return end
	local target = self.target
	target:forceUpdate()
	self:forceUpdate()
	
	local dx = x - self.x0
	local dy = y - self.y0

	local mode = 'global'
	local parent = target.parent
	if parent and mode == 'global' then
		if self.activeAxis == 'all' then
			--pass
			local k = 1 + math.magnitude( dx, dy ) / 100 * math.sign(dx) 
			self.target:setScl( 
				self.sx * k,
				self.sy * k,
				self.sz * 1 )
		elseif self.activeAxis == 'x' then
			-- pass
		elseif self.activeAxis == 'y' then
			-- pass
		end
		
	else
		local k = 1 + math.magnitude( dx, dy ) / 100 * math.sign(dx) 
		self.target:setScl( 
			self.sx * k,
			self.sy * k,
			self.sz * 1 )
	end
	
	self:updateCanvas()	
	return true
end

