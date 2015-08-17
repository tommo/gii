module 'mock_edit'

--------------------------------------------------------------------
--CanvasNavigate
--------------------------------------------------------------------
CLASS: CanvasNavigate( EditorEntity )

function CanvasNavigate:__init( option )
	self.option = option
end

function CanvasNavigate:onLoad()
	local option = self.option or {}
	local inputDevice = option.inputDevice or self:getScene().inputDevice
	self.targetCamera = assert( option.camera or self:getScene().camera )
	self:attach( mock.InputScript{ 
			device = inputDevice
		} )
	self.inputDevice = inputDevice
	self.zoom = 1
	self.dragging = false
end

function CanvasNavigate:reset()
	self.targetCamera:setLoc( 0,0,0 )
	self.targetCamera:setRot( 0,0,0 )
	self.targetCamera:setScl( 1,1,1 )
	self.targetCamera:com():setZoom( 1 )
end

-- function CanvasNavigate:onKeyEvent( key, down )
-- 	if key == 'space' then
-- 	end
-- end

function CanvasNavigate:startDrag( btn, x, y )
	self.dragFrom = { x, y }
	self.cameraFrom = { self.targetCamera:getLoc() }
	self.dragging = btn
	self.targetCamera:com():setCursor( 'closed-hand' )
end

function CanvasNavigate:stopDrag()
	self.dragging = false
	self.targetCamera:com():setCursor( 'arrow' )
end

function CanvasNavigate:onMouseDown( btn, x, y )
	if btn == 'middle' then
		if self.dragging then return end
		self:startDrag( btn, x, y )

	elseif btn == 'left' then
		if self.dragging then return end
		if self.inputDevice:isKeyDown( 'space' ) then
			self:startDrag( btn, x, y )
		end
		
	end
end

function CanvasNavigate:onMouseUp( btn, x, y )
	if btn == self.dragging then self:stopDrag() end
end

function CanvasNavigate:onMouseMove( x, y )
	if not self.dragging then return end	
	local x0, y0 = unpack( self.dragFrom )
	local dx, dy = x - x0, y - y0
	local cx0, cy0 = unpack( self.cameraFrom )
	local cameraCom = self.targetCamera:getComponent( EditorCanvasCamera )
	local zoom = cameraCom:getZoom()
	local z0 = self.targetCamera:getLocZ()
	self.targetCamera:setLoc( cx0 - dx/zoom, cy0 + dy/zoom, z0 )
	self:updateCanvas()
end

function CanvasNavigate:onScroll( x, y )
	if self.dragging then return end
	if y > 0 then
		self:setZoom( self.zoom + 0.1 )
	else
		self:setZoom( self.zoom - 0.1 )
	end
end

function CanvasNavigate:setZoom( zoom )
	zoom = clamp( zoom, 1 / 16, 16 )
	self.zoom = zoom
	local cameraCom = self.targetCamera:getComponent( EditorCanvasCamera )
	cameraCom:setZoom( zoom )
	self:updateCanvas()
end

function CanvasNavigate:updateCanvas()
	local cameraCom = self.targetCamera:getComponent( EditorCanvasCamera )
	cameraCom:updateCanvas()
end