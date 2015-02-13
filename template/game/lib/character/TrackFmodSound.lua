module 'character'

local function fixpath(p)
	p=string.gsub(p,'\\','/')
	return p
end

local function stripExt(p)
	return string.gsub( p, '%..*$', '' )
end

local function stripDir(p)
	p=fixpath(p)
	return string.match(p, "[^\\/]+$")
end

--------------------------------------------------------------------
CLASS: EventFmodSound ( CharacterActionEvent )
	:MODEL{
		Field 'sound'  :asset( 'fmod_event' );
		Field 'loop'   :boolean();
		Field 'ahead'    :int();
	}
function EventFmodSound:__init()
	self.length = 0
	self.loop   = false
	self.ahead  = 0
end

function EventFmodSound:resizable()
	return false
end

function EventFmodSound:start( state, pos )
	if self.sound then 
		local target = state.target
		if self.loop then
			local evt = target.soundSource:loopEvent2D( self.sound )
		else
			local evt = target.soundSource:playEvent2D( self.sound )
		end
	end
end

function EventFmodSound:getKeyFramePos()
	return self.pos - self.ahead
end

function EventFmodSound:toString()
	if not self.sound then return '<nil>' end
	local name = stripDir( self.sound )
	return self.loop and '<loop>'..name or name
end

--------------------------------------------------------------------
CLASS: TrackFmodSound ( CharacterActionTrack )
	:MODEL{}

function TrackFmodSound:__init()
	self.name = 'sound'
end

function TrackFmodSound:getType()
	return 'fmod_sound'
end

function TrackFmodSound:createEvent()
	return EventFmodSound()
end

function TrackFmodSound:toString()
	return '<fmod>' .. tostring( self.name )
end
--------------------------------------------------------------------
registerCharacterActionTrackType( 'Fmod Sound', TrackFmodSound )
