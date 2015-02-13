module 'character'

EnumEventTempoType = {
	{ 'reset', 'reset' },
	{ 'beat',  'beat' },
	{ 'sub',   'sub' },
}

EnumEventTempoBeatType = {
	{ 'any', 'any' },
	{ 'on' , 'on'  },
	{ 'off', 'off' },
}

--------------------------------------------------------------------
CLASS: EventTempo ( CharacterActionEvent )
	:MODEL{
		Field 'type'  :enum( EnumEventTempoType );
		Field 'value' :number() :range( 0, 4 ) :widget('slider') :meta{ step = 0.25 };
		Field 'wait'  :number() :range( 0, 4 ) :widget('slider') :meta{ step = 0.25 };
		'----';
		Field 'strict' :boolean();
		'----';
		Field 'waitBeatType' :enum( EnumEventTempoBeatType );
	}

function EventTempo:__init()
	self.type  = 'beat'
	self.value = 0
	self.wait  = 0
	self.strict = false
	self.waitBeatType = 'any'
end

function EventTempo:toString()
	local t = self.type
	if t == 'reset' then return 'R' end

	local output = ''
	if t == 'beat' then
		if self.value == 0 then
			output = 'B( ? )'
		else
			output = string.format( 'B( %d )', self.value )
		end
	elseif t == 'sub' then
		output = string.format( '[ %.2f ]', self.value )
	elseif t == 'match' then
		output = 'B( ? )'	
	end
	if self.wait > 0 then
		output = output .. string.format( ' +%.2f', self.wait )
	end
	return output
end

--------------------------------------------------------------------
CLASS: TrackTempo ( CharacterActionTrack )
	:MODEL{}

function TrackTempo:__init()
	self.name = 'tempo'
end

function TrackTempo:getType()
	return 'tempo'
end

function TrackTempo:createEvent()
	return EventTempo()
end

function TrackTempo:hasKeyFrames()
	return true
end

function TrackTempo:findEvent( name )
	for i, ev in ipairs( self.events ) do
		if ev.name == name then return ev end
	end
	return nil
end

function TrackTempo:findEvents( name )
	local res = {}
	for i, ev in ipairs( self.events ) do
		if ev.name == name then table.insert( res, ev ) end
	end
	return unpack( res )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Tempo', TrackTempo )
