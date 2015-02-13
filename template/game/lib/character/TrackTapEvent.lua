module 'character'

--------------------------------------------------------------------
CLASS: TrackTapEvent ( CharacterActionTrack )
	:MODEL{}

function TrackTapEvent:__init()
	self.name = 'tap'
end

function TrackTapEvent:getType()
	return 'tap'
end

function TrackTapEvent:createEvent( evType )
	return EventTap()
end

function TrackTapEvent:toString()
	return '<msg>' .. tostring( self.name )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'TapEvent', TrackTapEvent )


--------------------------------------------------------------------
EnumTapEventMessage = _ENUM_V{
	'move',
	'attack',
}

EnumTapTypes = _ENUM_V{
	'tap',
	'slash'
}

EnumTapAngle = _ENUM_V{
	'N',
	'NE',
	'E',
	'SE',
	'S',
	'SW',
	'W',
	'NW',
}

CLASS: EventTap ( CharacterActionEvent )
	:MODEL{
		Field 'tapType' :enum( EnumTapTypes);
		Field 'duration' :int();
		Field 'slashAngle' :enum(EnumTapAngle);
		'----';
		Field 'message' :enum( EnumTapEventMessage );
		Field 'arg'     :string();
	}
function EventTap:__init()
	self.tapType  = 'tap'
	self.duration = 1
	self.slashAngle = 'E'

	self.length = 0
	self.name   = 'message'
	self.message = 'attack'

	self.arg    = false
end

function EventTap:isResizable()
	return true
end

function EventTap:start( state, pos )	
	state.target:tell( 'tap!', self )
end

local tapTypeToAlias = {
	[ 'tap'   ] = 'T';
	[ 'slash' ] = 'S';
}
function EventTap:toString()
	--[S/T]msg
	local alias = self.tapType
	local k = string.format(
		'[%s]%s', tapTypeToAlias[ self.tapType ], self.tapType
		)
	return k
end

