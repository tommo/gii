module 'mock'

--------------------------------------------------------------------
--Common Routine
--------------------------------------------------------------------
-- CLASS: EffectPropNode ( EffectNode )
-- 	:MODEL{}

-- function EffectPropNode:createProp( fxState )

-- end

-- function EffectPropNode:onLoad( fxState )
-- 	local prop = self:createProp( fxState )

-- end

--------------------------------------------------------------------
--Static Sprite
--------------------------------------------------------------------
CLASS: EffectStaticSprite ( EffectTransformNode )
	:MODEL{
		Field 'deck'  :asset('deck2d\\..*');
		Field 'index' :int() :range(0);
		'----';
		Field 'color'    :type('color')  :getset('Color') ;
		Field 'blend' :enum( EnumBlendMode );
	}

function EffectStaticSprite:__init()
	self.color = { 1,1,1,1 }
end

function EffectStaticSprite:getDefaultName()
	return 'sprite'
end

function EffectStaticSprite:getTypeName()
	return 'sprite'
end

function EffectStaticSprite:onLoad( fxState )
	local sprite = MOAIProp.new()
	local deck = loadAsset( self.deck )
	sprite:setDeck( deck )
	setPropBlend( sprite, self.blend )
	--todo: shader	
	self:applyTransformToProp( sprite )

	fxState:linkTransform( sprite )
	fxState:linkPartition( sprite )
	sprite:setColor( unpack( self.color ) )
	fxState[ self ] = sprite
end

function EffectStaticSprite:getColor()
	return unpack( self.color )
end

function EffectStaticSprite:setColor( r,g,b,a )
	self.color = { r,g,b,a }
end


--------------------------------------------------------------------
--Aurora Sprite
--------------------------------------------------------------------
CLASS: EffectAuroraSprite ( EffectTransformNode )
	:MODEL{
		Field 'spritePath' :asset( 'aurora_sprite' );
		Field 'clip'  :string() :selection( 'getClipNames' );
		Field 'mode'  :enum( EnumTimerMode );
		Field 'FPS'   :int() :range( 0,200 ) :widget( 'slider' );
		'----';
		Field 'blend' :enum( EnumBlendMode );
	}

function EffectAuroraSprite:__init()
	self.blend = 'alpha'
	self.mode  = MOAITimer.NORMAL
	self.FPS   = 10
end

function EffectAuroraSprite:getDefaultName()
	return 'aurora'
end

function EffectAuroraSprite:getTypeName()
	return 'aurora'
end

function EffectAuroraSprite:onLoad( fxState )
	local sprite = AuroraSprite()
	sprite:setSprite( self.spritePath )
	sprite:setFPS( self.FPS )
	sprite:play( self.clip, self.mode )
	sprite:setBlend( self.blend )
	self:applyTransformToProp( sprite )
	fxState:linkTransform( sprite.prop )
	fxState:linkPartition( sprite.prop )
	fxState[ self ] = sprite	
end

function EffectAuroraSprite:getClipNames()
	local data = mock.loadAsset( self.spritePath )
	if not data then return nil end
	local result = {}
	for k,i in pairs( data.animations ) do
		table.insert( result, { k, k } )
	end
	return result
end


--------------------------------------------------------------------
--Aurora Sprite
--------------------------------------------------------------------
CLASS: EffectSpineSprite ( EffectTransformNode )
	:MODEL{
		Field 'spritePath' :asset( 'spine' );
		Field 'clip'  :string() :selection( 'getClipNames' );
		Field 'mode'  :enum( EnumTimerMode );
		'----';
		Field 'throttle'  :range( 0 );
		Field 'offset'   ;
		'----';
		Field 'color'    :type('color')  :getset('Color') ;
		Field 'blend' :enum( EnumBlendMode );
	}

function EffectSpineSprite:__init()
	self.blend = 'alpha'
	self.mode  = MOAITimer.NORMAL
	self.clip  = false
	self.color = { 1,1,1,1 }
	self.throttle = 1
	self.offset = 0
end


function EffectSpineSprite:getDefaultName()
	return 'spine'
end

function EffectSpineSprite:getTypeName()
	return 'spine'
end


function EffectSpineSprite:getColor()
	return unpack( self.color )
end

function EffectSpineSprite:setColor( r,g,b,a )
	self.color = { r,g,b,a }
end

-- local function _onSpineAnimStop( anim )
-- 	return anim._effectNode:stop()
-- end

function EffectSpineSprite:onLoad( fxState )
	local sprite = SpineSpriteSimple()
	sprite:setSprite( self.spritePath )
	setPropBlend( sprite.skeleton, self.blend )
	self:applyTransformToProp( sprite )
	
	fxState:linkTransform( sprite.skeleton )
	fxState:linkPartition( sprite.skeleton )

	sprite.skeleton:setColor( unpack( self.color ) )
	sprite:setThrottle( self.throttle )
	local animState = sprite:play( self.clip, self.mode, nil, 'waitAttach', self.offset )
	fxState[ self ] = sprite
	if animState then
		fxState:attachAction( animState )
		animState._effectNode = self
		animState:setListener( MOAIAction.EVENT_STOP, 
			function()
				fxState:removeActiveNode( self )				
				sprite.skeleton:setPartition( nil )
			end
		)
	else
		fxState:removeActiveNode( self )
	end
end

function EffectSpineSprite:getClipNames()
	local data = mock.loadAsset( self.spritePath )
	if not data then return nil end
	local result = {}
	for k,i in pairs( data._animationTable ) do
		table.insert( result, { k, k } )
	end
	return result
end

--------------------------------------------------------------------
registerTopEffectNodeType(
	'sprite-static',
	EffectStaticSprite,
	EffectCategoryTransform	
)


registerTopEffectNodeType(
	'sprite-aurora',
	EffectAuroraSprite,
	EffectCategoryTransform
)

registerTopEffectNodeType(
	'sprite-spine',
	EffectSpineSprite,
	EffectCategoryTransform
)

