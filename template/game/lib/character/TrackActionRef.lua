module 'character'

--------------------------------------------------------------------
CLASS: EventActionRef ( CharacterActionEvent )
	:MODEL{
		Field 'actionId' :string() :selection( 'getActionSelection' );
		Field 'loop' :boolean();
		'----';
		Field 'actResetLength' :action('resetLength') :label('Reset Length')
	}

function EventActionRef:__init()
	self.actionId = ''
	self.loop     = false
end

function EventActionRef:isResizable()
	return true
end


function EventActionRef:toString()
	local f = ''
	if self.loop then f = f ..'<L>' end
	return f..( self.actionId or '' )
end


function EventActionRef:getActionSelection()
	local config    = self:getRootConfig()
	local result = {}
	for i, act in ipairs( config.actions ) do
		table.insert( result, { act.name, act.name } )
	end
	return result
end

function EventActionRef:checkCycleRef()
	--todo
	return false
end

function EventActionRef:resetLength()
	if not self.actionId then return end
	local root = self:getRootConfig()
	local act = root:getAction( self.actionId )
	if not act then
		_warn( 'no action found:', self.actionid )
		return
	end
	l = act:calcLength()
	if l and l > 0 then self.length = l end
end

--------------------------------------------------------------------

CLASS: TrackActionRef ( CharacterActionTrack )
:MODEL{
}

function TrackActionRef:__init()
	self.name = 'action_ref'
end

function TrackActionRef:createEvent()
	return EventActionRef()
end

function TrackActionRef:getType()
	return 'action_ref'
end

function TrackActionRef:toString()
	return '<actionR>'..tostring( self.name )
end

function TrackActionRef:start( state )
end

--------------------------------------------------------------------
registerCharacterActionTrackType( 'Action Reference', TrackActionRef )
