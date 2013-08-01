module 'mock'

CLASS: DrawScript ()
function DrawScript:__init( option )
	local prop = MOAIProp.new()

	-- if option and option.transform then
	-- 	prop:setupTransform( option.transform )
	-- end
	if option then
		setupMoaiProp( prop, option )
	end
	self.prop = prop
end

function DrawScript:setScissorRect( rect )
	return self.prop:setScissorRect( rect )
end

function DrawScript:onAttach( entity )	
	local deck = MOAIScriptDeck.new()
	
	if entity.onDraw then
		local onDraw = entity.onDraw
		deck:setDrawCallback( 
			function(...) return onDraw(entity, ... ) end
		)
	end

	if entity.onGetRect then
		local onGetRect = entity.onGetRect
		deck:setDrawCallback( 
			function(...) return onGetRect(entity, ... ) end
		)
	end
	
	deck:setRect(1,1,-1,-1)	
	self.prop:setDeck( deck )	

	return entity:_attachProp( self.prop )
end

function DrawScript:onDetach( entity )
	entity:_detachProp( self.prop )
end
