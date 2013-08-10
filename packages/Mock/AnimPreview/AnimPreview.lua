--------------------------------------------------------------------
scn = gii.createMockEditorScene()
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