module 'character'

--------------------------------------------------------------------
CLASS: EventMark ( CharacterActionEvent )
	:MODEL{
		Field 'name' :string()
	}

function EventMark:toString()
	return self.name or '<nil>'
end

--------------------------------------------------------------------
CLASS: TrackMark ( CharacterActionTrack )
	:MODEL{}

function TrackMark:__init()
	self.name = 'mark'
end

function TrackMark:getType()
	return 'mark'
end

function TrackMark:createEvent()
	return EventMark()
end

function TrackMark:hasKeyFrames()
	return true
end

function TrackMark:findEvent( name )
	for i, ev in ipairs( self.events ) do
		if ev.name == name then return ev end
	end
	return nil
end

function TrackMark:findEvents( name )
	local res = {}
	for i, ev in ipairs( self.events ) do
		if ev.name == name then table.insert( res, ev ) end
	end
	return unpack( res )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Mark', TrackMark )
