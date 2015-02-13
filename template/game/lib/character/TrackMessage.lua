module 'character'

--------------------------------------------------------------------
local _messageEventTypes = {}

function registerActionMessageEventType( t, clas )
	if _messageEventTypes[ t ] then
		_error( 'duplicated action message event type', t )
	end
	_messageEventTypes[ t ]	 = clas
end

--------------------------------------------------------------------
CLASS: TrackMessage ( CharacterActionTrack )
	:MODEL{}

function TrackMessage:__init()
	self.name = 'message'
end

function TrackMessage:getType()
	return 'message'
end

function TrackMessage:getDefaultEventType()
	return 'simple'
end

function TrackMessage:getEventTypes()
	local names = {}
	for k,clas in pairs( _messageEventTypes ) do
		table.insert( names, k )
	end
	table.sort( names )
	return names
end

function TrackMessage:createEvent( evType )
	local clas = _messageEventTypes[ evType ]
	assert( clas )
	return clas()
end

function TrackMessage:toString()
	return '<msg>' .. tostring( self.name )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Message', TrackMessage )


--------------------------------------------------------------------
CLASS: EventMessage ( CharacterActionEvent )
	:MODEL{
		Field 'message' :string();
		Field 'arg'     :string()
	}
function EventMessage:__init()
	self.length = 0
	self.name   = 'message'
	self.arg    = false
end

function EventMessage:isResizable()
	return true
end

function EventMessage:start( state, pos )	
	state.target:tell( self.message, self )
end

function EventMessage:toString()
	return tostring( self.message )
end


registerActionMessageEventType( 'simple', EventMessage )

