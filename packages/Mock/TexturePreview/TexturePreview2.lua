--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

CLASS: Preview ( mock.Entity )
function Preview:onLoad()
	self:addSibling( CanvasGrid() )
	self.prop = self:addProp{
		blend = 'alpha'
	}
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self.zoom = 1
		self.dragging = false

end

function Preview:show( path )
	local tex = mock.loadAsset(path)
	if not tex then return false end 

	local deck = MOAIGfxQuad2D.new()
	local w, h = tex:getSize()
	deck:setRect( -w/2, -h/2, w/2, h/2 )

	if tex.type == 'sub_texture'  then
		deck:setTexture( tex.atlas )
		deck:setUVRect( unpack( tex.uv ) )
	else
		deck:setTexture( tex )
	end

	self.prop:setDeck( deck )
	self.prop:forceUpdate()
	updateCanvas()
end

function Preview:fitViewport()
	
end

function Preview:onMouseDown( btn, x, y )
	if btn == 'left' then
		self.dragging = true
		self.dragFrom = { x, y }
	end
end

function Preview:onMouseUp( btn )
	if btn == 'left' then
		self.dragging = false
		scn.camera:setLoc( 0, 0 )
		updateCanvas()
	end
end

function Preview:onMouseMove( x, y )
	if self.dragging then
		local x0, y0 = unpack( self.dragFrom )
		local dx, dy = x - x0, y - y0
		scn.camera:setLoc( dx, -dy )
		updateCanvas()
	end
end

function Preview:onScroll( x, y )
	if y > 0 then
		self:setZoom( self.zoom * 2 )
	else
		self:setZoom( self.zoom / 2 )
	end
end

function Preview:setZoom( zoom )
	zoom = clamp( zoom, 1 / 16, 16 )
	self.zoom = zoom
	scn.cameraCom:setZoom( zoom )
	updateCanvas()
end

preview = scn:addEntity( Preview() )


function show( path )
	preview:show( path )
end
