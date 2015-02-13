module 'character'

--------------------------------------------------------------------
CLASS: EventSpineAnimation ( CharacterActionEvent )
	:MODEL{
		Field 'clip'  :string() :selection( 'getSpineClipSelection' );
		Field 'loop'  :boolean();
		Field 'reversed'  :boolean();
		Field 'resetOnPlay'  :boolean();
		'----';
		Field 'offset' :range(0);
		'----';
		Field 'actResetLength' :action('resetLength') :label('Reset Length')
	}

function EventSpineAnimation:__init()
	self.length = 1
	self.clip   = ''
	self.loop   = false
	self.resetOnPlay = true
	self.offset = 0
	self.reversed = false
end

function EventSpineAnimation:getSpineClipSelection()
	local config = self:getRootConfig()
	local spinePath = config:getSpine()
	local spineData = mock.loadAsset( spinePath )
	if not spineData then return nil end
	local result = {}
	for k,i in pairs( spineData._animationTable ) do
		table.insert( result, { k, k } )
	end
	return result
end

function EventSpineAnimation:isResizable()
	return true
end

function EventSpineAnimation:toString()
	local clip = self.clip
	if not clip or clip == '' then return '<nil>' end
	local flags = ''
	if self.loop then
		flags = flags .. 'L'
	end
	if self.reversed then
		flags = flags .. 'R'
	end
	if flags~='' then
		return string.format( '[%s]%s', flags, clip )
	else
		return clip
	end
end

function EventSpineAnimation:setClip( name )
	self.clip = name
end

function EventSpineAnimation:resetLength()
	if not self.clip then return end
	local root = self:getRootConfig()
	if not root then return end	
	local spinePath = root.spinePath
	if not spinePath then return end
	local data = mock.loadAsset( spinePath )
	if not data then return end
	local l = data:getAnimationDuration( self.clip )
	if l and l > 0 then self.length = l*1000 end
end

--------------------------------------------------------------------
CLASS: TrackSpineAnimation ( CharacterActionTrack )
	:MODEL{
		Field 'startFix1' :boolean()
}

function TrackSpineAnimation:__init()
	self.startFix1 = false
	self.name = 'animation'
end

function TrackSpineAnimation:createEvent()
	return EventSpineAnimation()
end

function TrackSpineAnimation:hasKeyFrames()
	return false
end

function TrackSpineAnimation:getType()
	return 'spine'
end

function TrackSpineAnimation:toString()
	return '<spine>' .. tostring( self.name )
end

local _started = {}
function TrackSpineAnimation:start( state )
	--build MOAISpineAnimationTrack
	local target      = state.target
	local spineTracks = state.spineTracks
	if not spineTracks then 
		spineTracks = {}
		state.spineTracks = spineTracks
	end
	local spineState = target.spineState
	if not spineState then
		spineState = target.spineSprite:createState()
		target.spineState = spineState
	end
	
	spineState:pause( false )
	spineState:setTime( 0 )
	spineState:apply( 0 )
	spineState:setSpan( state.length )
	if state.loop then
		spineState:setMode( MOAITimer.LOOP )
	else
		spineState:setMode( MOAITimer.NORMAL )
	end
	spineState:attach( state:getTimer() )
	local animTrack = spineState:addTrack()
	spineTracks[ self ] = animTrack
	for i, ev in ipairs( self.events ) do
		local l = ev.length/1000
		animTrack:addSpan( ev.pos/1000, ev.clip, ev.loop, ev.offset, l>0 and l or nil, ev.reversed )
	end
	spineState:apply( 0.0 )
	target.spineSprite:getSkeleton():updateSpine()
end

function TrackSpineAnimation:stop( state )	
	local spineTracks = state.spineTracks
	if not spineTracks then return end
	local spineState = state.target.spineState
	local track = spineTracks[ self ]
	spineState:removeTrack( track )
	spineState:stop()
	spineTracks[ self ] = nil
end

function TrackSpineAnimation:pause( state, paused )
	local spineState = state.target.spineState
	spineState:pause( paused )
end

function TrackSpineAnimation:setThrottle( state, t )
	local spineState = state.target.spineState
	if spineState then
		-- spineState:throttle( t )
	end
end

function TrackSpineAnimation:apply( state, t, t1 )
	local spineState = state.target.spineState
	if spineState then
		if self.startFix1 then
			spineState:apply( t + 0.001, t1 and ( t1 + 0.001 ) )
		else
			spineState:apply( t, t1 )
		end
	end
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Spine Animation', TrackSpineAnimation )
