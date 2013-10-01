--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

CLASS: AnimPreview ( mock.Entity )

function AnimPreview:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self.dragging = false
	self:attach( mock.InputScript( { device = scn.inputDevice }) )
	self.spriteType = false
	self.sprite = false
end

function AnimPreview:showAnimSprite( path )
	if self.sprite then self:detach( self.sprite ) end

	local anim, node = mock.loadAsset( path )
	if node.type == 'aurora_sprite' then
		self.spriteType = 'aurora'
		self.sprite = self:attach( mock.AuroraSprite{ blend = 'alpha' } )
		self.sprite:setFPS( 10 )
		self.sprite:load( anim )	
		local names = {}
		for k in pairs( anim.animations ) do
			table.insert( names, k )
		end
		return names
	elseif node.type == 'spine' then
		self.spriteType = 'spine'
		self.sprite = self:attach( mock.SpineSprite() )
		self.sprite:setSprite( path )
		local names = { anim:getAnimationNames() }
		return names
	end
end

function AnimPreview:setAnimClip( name )
	self.currentAnimClipLength = self.sprite:getClipLength( name )
	self.sprite:play( name, MOAITimer.LOOP )
end

-- function AnimPreview:onMouseDown( btn )
-- 	if btn=='left' then 
-- 		self.sprite:pause( true ) --unpause
-- 		self.dragging = true
-- 	end
-- end

-- function AnimPreview:onMouseUp( btn )
-- 	if btn=='left' then 
-- 		self.sprite:pause(false)
-- 		self.dragging = false
-- 	end
-- end

-- function AnimPreview:onMouseMove( x, y )
-- 	if not self.dragging then return end
-- 	if self.currentAnimClipLength then
-- 		local size = getCanvasSize()
-- 		local w, h = size[0], size[1]
-- 		local t = x / w * self.currentAnimClipLength 
-- 		self.sprite:apply( t )		
-- 		updateCanvas()
-- 	end
-- end

--------------------------------------------------------------------
preview = scn:addEntity( AnimPreview() )
--------------------------------------------------------------------