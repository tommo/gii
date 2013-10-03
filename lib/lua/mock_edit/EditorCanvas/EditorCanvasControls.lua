module 'mock_edit'
--------------------------------------------------------------------
--CanvasGrid
--------------------------------------------------------------------
CLASS: CanvasGrid( EditorEntity )
function CanvasGrid:onLoad()
	self:attach( mock.DrawScript{	priority = -1	} )
end

function CanvasGrid:onDraw()
	axisSize = 10000
	-- MOAIGfxDevice.setPenColor( .1, .1, .1 )
	-- MOAIDraw.fillRect( -axisSize, -axisSize, axisSize, axisSize )
	MOAIGfxDevice.setPenColor( .3, .3, .3 )
	MOAIDraw.drawLine( -axisSize, 0, axisSize, 0 )
	MOAIDraw.drawLine( 0, -axisSize, 0, axisSize )
end

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
	self.zoom = 1

end

function CanvasNavigate:onMouseDown( btn, x, y )
	if btn == 'middle' then
		self.dragFrom = { x, y }
		self.cameraFrom = { self.targetCamera:getLoc() }
		self.dragging = true
	end
end

function CanvasNavigate:onMouseUp( btn, x, y )
	if btn == 'middle' then
		self.dragging = false
	end
end

function CanvasNavigate:onMouseMove( x, y )
	if not self.dragging then return end	
	local x0, y0 = unpack( self.dragFrom )
	local dx, dy = x - x0, y - y0
	local cx0, cy0 = unpack( self.cameraFrom )
	local cameraCom = self.targetCamera:getComponent( EditorCanvasCamera )
	local zoom = cameraCom:getZoom()
	self.targetCamera:setLoc( cx0 - dx/zoom, cy0 + dy/zoom )
	cameraCom:updateCanvas()	
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
	cameraCom:updateCanvas()
end

--------------------------------------------------------------------
CLASS: CanvasHandleLayer ( EditorEntity )
function CanvasHandleLayer:__init( option )
	self.option = option
	self.activeHandle = false
	self.handles = {}
end

function CanvasHandleLayer:onLoad()
	local option = self.option or {}
	local inputDevice = option.inputDevice or self:getScene().inputDevice
	self.targetCamera = assert( option.camera or self:getScene().camera )
	self.targetCameraCom = self.targetCamera:com('EditorCanvasCamera')
	self:attach( mock.InputScript{ 
			device = inputDevice
		} )
	self.targetCameraCom.onZoomChanged = function( zoom ) return self:onZoomChanged( zoom ) end
end

function CanvasHandleLayer:onMouseDown( btn, x, y )
	for i, handle in ipairs( self.handles ) do
		if handle:onMouseDown( btn, x, y ) == true then --grabbed
			return
		end
	end
end

function CanvasHandleLayer:onMouseUp( btn, x, y )
	for i, handle in ipairs( self.handles ) do
		if handle:onMouseUp( btn, x, y ) == true then
			return
		end
	end
end

function CanvasHandleLayer:onMouseMove( x, y )
	for i, handle in ipairs( self.handles ) do
		if handle:onMouseMove( x, y ) == true then
			return
		end
	end
end

function CanvasHandleLayer:onZoomChanged( zoom )
	local scl = 1/zoom
	for i, handle in ipairs( self.handles ) do
		handle:setScl( scl, scl, 1 )
	end
end	

function CanvasHandleLayer:addHandle( handle )
	self:addSibling( handle )
	table.insert(self.handles, 1, handle )
	handle.handleLayer = self
	local scl = 1/self.targetCameraCom:getZoom()
		handle:setScl( scl, scl, 1 )
	return handle
end


--------------------------------------------------------------------
CLASS: CanvasHandle ( EditorEntity )

function CanvasHandle:onMouseDown( btn, x, y )
end

function CanvasHandle:onMouseUp( btn, x, y )
end

function CanvasHandle:onMouseMove( x, y )
end

function CanvasHandle:onDestroy()
	local handleLayer = self.handleLayer
	if not handleLayer then return end
	for i, h in ipairs( handleLayer.handles ) do
		if h == self then return table.remove( self.handleLayer.handles, i )  end
	end
end

