module 'mock'

CLASS: SpineSprite ( SpineSpriteBase )
	:MODEL{
		Field 'defaultClip' :string()  :label('Default') :selection( 'getAnimationNames' );
		Field 'autoPlay'    :boolean() :label('Auto Play');
		Field 'throttle'    ;
	}

registerComponent( 'SpineSprite', SpineSprite )

function SpineSprite:__init()
	self.animState     = false
	self.skeletonData  = false
	self.defaultClip   = ''
	self.autoPlay      = true
	self._onAnimationEvent  = false
	self.throttle      = 1
	self.mixTable      = false
end

function SpineSprite:onStart( entity )
	local default = self.defaultClip
	if self.autoPlay and default and default ~= '' then
		self:play( default, MOAITimer.LOOP )
	end
end

local function _onSpineAnimationEvent( anim, trackId, name, varInt, varFloat, varString )
	return anim.owner:onAnimationEvent( trackId, name, varInt, varFloat, varString )
end

local function _onSpineAnimationComplete( anim, trackId, loopCount )
	return anim.owner:onAnimationComplete( trackId, loopCount )
end

function SpineSprite:getSkeleton()
	return self.skeleton
end

function SpineSprite:getSkeletonData()
	return self.skeletonData
end

function SpineSprite:play( clipName, mode, resetPose, waitAttach, offset )
	if self.animState then
		self.animState:stop( resetPose )
	end
	mode = mode or MOAITimer.NORMAL
	local anim = self:createState()
	anim:setMode( mode )
	if not self:affirmClip( clipName ) then
		_traceback()
		_warn( 'spine anim clip not found:', clipName )
		return false
	end
	
	if resetPose ~= false then
		self.skeleton:setBonesToSetupPose()
	end

	local track = anim:addTrack()
	local span = track:addSpan( 
		0, 
		clipName, 
		mode == MOAITimer.LOOP,
		offset or 0,
		-1
	)
	local duration = span:getDuration()
	anim:setSpan( duration )
	anim:apply( 0 )
	if not waitAttach then
		anim:start()
	end
	anim.owner = self
	-- anim:setListener( EVENT_SPINE_ANIMATION_EVENT, _onSpineAnimationEvent )
	-- anim:setListener( EVENT_SPINE_ANIMATION_COMPLETE, _onSpineAnimationComplete )
	self.animState = anim 
	return anim
end


function SpineSprite:createState()
	local anim = MOAISpineAnimation.new()
	anim:init( self.skeletonData )
	anim:setSkeleton( self.skeleton )
	if self.mixTable then anim:setMixTable( self.mixTable ) end
	anim:throttle( self.throttle )
	return anim
end

function SpineSprite:setThrottle( th )
	self.throttle = th
	if self.animState then
		self.animState:throttle( th )
	end
end

function SpineSprite:stop( resetPose )
	if self.animState then
		self.animState:stop()
		self.animState = false
		if resetPose ~= false then
			self.skeleton:setBonesToSetupPose()
		end
	end
end

function SpineSprite:pause( paused )
	if self.animState then
		self.animState:pause( paused )
	end
end

function SpineSprite:resume()
	return self:pause( false )
end

function SpineSprite:setAnimationEventListener( listener )
	self._onAnimationEvent = listener
end

function SpineSprite:onAnimationEvent( trackId, evName, varInt, varFloat, varString )
	local callback = self._onAnimationEvent
	if callback then
		return callback( evName, varInt, varFloat, varString )
	end
end

function SpineSprite:getAnimationNames()
	if not self.skeletonData then return nil end
	local result = {}
	for k,i in pairs( self.skeletonData._animationTable ) do
		table.insert( result, { k, k } )
	end
	return result
end

function SpineSprite:onDetach( entity )
	self:stop()
	return SpineSpriteBase.onDetach( self, entity )
end

wrapWithMoaiPropMethods( SpineSprite, ':getSkeleton()' )
