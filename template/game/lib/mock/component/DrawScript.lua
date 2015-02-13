module 'mock'

CLASS: DrawScript ()
	-- :MODEL{
	-- 	Field 'blend'  :enum( EnumBlendMode ) :getset('Blend');		
	-- }
function DrawScript:__init( option )
	local prop = MOAIProp.new()

	-- if option and option.transform then
	-- 	prop:setupTransform( option.transform )
	-- end
	self.prop = prop
	local deck = MOAIScriptDeck.new()
	self.prop:setDeck( deck )	
	self.deck = deck

	if option then
		setupMoaiProp( prop, option )		
	end

	local rect = option and option['rect']
	self:setRect( rect and unpack( rect ) )
end

function DrawScript:getBlend()
	return self.blend
end

function DrawScript:setBlend( b )
	self.blend = b	
	setPropBlend( self.prop, b )
end

function DrawScript:setScissorRect( rect )
	return self.prop:setScissorRect( rect )
end

function DrawScript:inside( x,y,z,pad )
	return self.prop:inside( x,y,z,pad )
end

function DrawScript:onAttach( entity )	
	local drawOwner, onDraw
	if self.onDraw then 
		onDraw = self.onDraw
		drawOwner = self
	elseif entity.onDraw then
		onDraw = entity.onDraw
		drawOwner = entity
	end
	if onDraw then
		self.deck:setDrawCallback( 
			function(...) return onDraw( drawOwner, ... ) end
		)
	end

	local rectOwner, onGetRect
	if self.onGetRect then 
		onGetRect = self.onGetRect
		rectOwner = self
	elseif entity.onGetRect then
		onGetRect = entity.onGetRect
		rectOwner = entity
	end
	if onGetRect then
		self.deck:setRectCallback( 
			function(...) return onGetRect( rectOwner, ... ) end
		)
	end
		
	return entity:_attachProp( self.prop )
end

function DrawScript:setRect( x0, y0, x1, y1 )
	if not x0 then
		self.deck:setRect( 10000, 10000, -10000, -10000 ) 
	else
		self.deck:setRect(  x0, y0, x1, y1 )
	end
end

function DrawScript:onDetach( entity )
	entity:_detachProp( self.prop )
end
