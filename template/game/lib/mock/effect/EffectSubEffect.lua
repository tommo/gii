module 'mock'

--------------------------------------------------------------------
--Effect Sub Effect
--------------------------------------------------------------------
CLASS: EffectSubEffect ( EffectTransformNode )
	:MODEL{
		Field 'effect'  :asset('effect');
	}


function EffectSubEffect:onLoad( fxState )
	if not self.effect then
		return fxState:removeActiveNode( self )
	end

	local parentEmitter = fxState._emitter
	local subEmitter = EffectEmitter()	
	subEmitter.autoPlay = false

	parentEmitter:getEntity():attach( subEmitter )
	subEmitter.actionOnStop = 'detach'
	subEmitter:setEffect( self.effect )

	self:applyTransformToProp( subEmitter.prop )
	fxState:linkTransform( subEmitter.prop )

	--TODO: avoid cyclic effect reference
	local subState 
	subState = subEmitter:start( 'waitStart' )
	if subState then
		local timer = subState:getTimer()
		fxState:attachAction( timer )
		fxState[ self ] = subEmitter
		timer:setListener( MOAIAction.EVENT_STOP, 
			function()
				fxState:removeActiveNode( self )
			end
		)
	else
		fxState:removeActiveNode( self )
	end
end

function EffectSubEffect:getDefaultName()
	return 'sub-effect'
end

function EffectSubEffect:getTypeName()
	return 'effect'
end

registerTopEffectNodeType(
	'sub-effect',
	EffectSubEffect,
	EffectCategoryTransform
)

