module 'character'

--------------------------------------------------------------------
CLASS: EventAlign ( CharacterActionEvent )
	:MODEL{
		Field 'name' :string()
	}

function EventAlign:toString()
	return self.name or '<nil>'
end

function EventAlign:start( target, pos )
	local nextAlign = self:findNextEvent()
	if not nextAlign then return end
	local pos1 = nextAlign
	local throttle = 1 --calc
	target:setThrottle( throttle )
end

function EventAlign:isResizable()
	return false
end

--------------------------------------------------------------------
CLASS: TrackAlign ( CharacterActionTrack )
	:MODEL{}

function TrackAlign:__init()
	self.name = 'align'
end

function TrackAlign:getType()
	return 'align'
end

function TrackAlign:createEvent()
	return EventAlign()
end

function TrackAlign:hasKeyFrames()
	return true
end

function TrackAlign:findEvent( name )
	for i, ev in ipairs( self.events ) do
		if ev.name == name then return ev end
	end
	return nil
end

function TrackAlign:findEvents( name )
	local res = {}
	for i, ev in ipairs( self.events ) do
		if ev.name == name then table.insert( res, ev ) end
	end
	return unpack( res )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Align', TrackAlign )
