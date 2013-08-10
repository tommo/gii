--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------


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
CLASS: AnimPreview ( mock.Entity )

function AnimPreview:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self.dragging = false
	self:attach( mock.InputScript( { device = scn.inputDevice }) )
	self.sprite = self:attach( mock.AuroraSprite{ blend = 'alpha' } )
	self.sprite:setFPS( 10 )
end

function AnimPreview:showAuroraSprite( path )
	local anim, node = mock.loadAsset( path )
	self.sprite:load( anim )	
	local names = {}
	for k in pairs( anim.animations ) do
		table.insert( names, k )
	end
	return names
end

function AnimPreview:setAnimClip( name )
	self.currentAnimClipLength = self.sprite:getClipLength( name )
	self.sprite:play( name, MOAITimer.LOOP )
end

function AnimPreview:onMouseDown( btn )
	if btn=='left' then 
		self.sprite:pause( true ) --unpause
		self.dragging = true
	end
end

function AnimPreview:onMouseUp( btn )
	if btn=='left' then 
		self.sprite:pause(false)
		self.dragging = false
	end
end

function AnimPreview:onMouseMove( x, y )
	if not self.dragging then return end
	if self.currentAnimClipLength then
		local size = getCanvasSize()
		local w, h = size[0], size[1]
		local t = x / w * self.currentAnimClipLength 
		self.sprite:apply( t )		
		updateCanvas()
	end
end

--------------------------------------------------------------------
preview = scn:addEntity( AnimPreview() )
--------------------------------------------------------------------

function showAuroraSprite( path )
	return preview:showAuroraSprite( path )
end

function setAnimClip( name )
	return preview:setAnimClip( name )
end