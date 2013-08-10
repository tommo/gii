--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

--------------------------------------------------------------------
CLASS: CanvasGrid( mock.Entity )
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
CLASS: CanvasNavigate( mock.Entity )
function CanvasNavigate:onLoad()
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self.zoom = 1
end

function CanvasNavigate:onMouseDown( btn, x, y )
	if btn == 'middle' then
		self.dragFrom = { x, y }
		self.cameraFrom = { scn.camera:getLoc() }
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
	local zoom = scn.cameraCom:getZoom()
	scn.camera:setLoc( cx0 - dx/zoom, cy0 + dy/zoom )
	updateCanvas()
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
	self.scene.cameraCom:setZoom( zoom )
	updateCanvas()
end


--------------------------------------------------------------------
CLASS: Deck2DEditor( mock.Entity )

function Deck2DEditor:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
end

function Deck2DEditor:openDeck( node )
end

--------------------------------------------------------------------
editor = scn:addEntity( Deck2DEditor() )
