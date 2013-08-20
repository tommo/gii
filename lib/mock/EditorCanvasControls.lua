
--------------------------------------------------------------------
--CanvasGrid
--------------------------------------------------------------------
CLASS: CanvasGrid( EditorEntity )
function CanvasGrid:onLoad()
	self:attach( mock.DrawScript{	priority = -1	} )
end

function CanvasGrid:onDraw()
	axisSize = 10000
	MOAIGfxDevice.setPenColor( .1, .1, .1 )
	MOAIDraw.fillRect( -axisSize, -axisSize, axisSize, axisSize )
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
	if y > 0 then
		self:setZoom( self.zoom * 2 )
	else
		self:setZoom( self.zoom / 2 )
	end
end

function CanvasNavigate:setZoom( zoom )
	zoom = clamp( zoom, 1 / 16, 16 )
	self.zoom = zoom
	local cameraCom = self.targetCamera:getComponent( EditorCanvasCamera )
	cameraCom:setZoom( zoom )
	cameraCom:updateCanvas()	
end
