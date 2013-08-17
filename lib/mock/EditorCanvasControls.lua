--------------------------------------------------------------------
CLASS: EditorEntity ( mock.Entity )
function EditorEntity:__init()
	self.__editor_entity = true
end

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
CLASS: CanvasNavigate( EditorEntity )
function CanvasNavigate:onLoad()
	self:attach( mock.InputScript{ device = self:getScene().inputDevice } )
	self.zoom = 1
end

function CanvasNavigate:onMouseDown( btn, x, y )
	if btn == 'middle' then
		self.dragFrom = { x, y }
		self.cameraFrom = { self:getScene().camera:getLoc() }
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
	local scn = self:getScene()
	local x0, y0 = unpack( self.dragFrom )
	local dx, dy = x - x0, y - y0
	local cx0, cy0 = unpack( self.cameraFrom )
	local zoom = scn.cameraCom:getZoom()
	scn.camera:setLoc( cx0 - dx/zoom, cy0 + dy/zoom )
	scn:updateCanvas()
end

function CanvasNavigate:onScroll( x, y )
	if y > 0 then
		self:seekZoom( self.zoom * 2, 0.1 )
	else
		self:seekZoom( self.zoom / 2, 0.1 )
	end
end

function CanvasNavigate:setZoom( zoom )
	zoom = clamp( zoom, 1 / 16, 16 )
	self.zoom = zoom
	self.scene.cameraCom:setZoom( zoom )
	self.scene:updateCanvas()
end
