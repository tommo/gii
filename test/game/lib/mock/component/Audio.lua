module 'mock'
--------------------------------------------------------------------
--SOUND Listener
--------------------------------------------------------------------
--TODO: add multiple listener support (need host works) ?
CLASS: SoundListener ()
wrapWithMoaiTransformMethods( SoundListener, '_listener' )

function SoundListener:__init()
	local listener = MOAIFmodEventMgr.getMicrophone()
	self._listener = listener
	listener:setVectorForward( 0,0,-1 )
	listener:setVectorUp( 0,1,0 )
end

function SoundListener:onAttach( entity )
	entity:_attachTransform( self._listener )
end

function SoundListener:onDetach( entity )
	-- do nothing...
end

--------------------------------------------------------------------
--SOUND SOURCE
--------------------------------------------------------------------
CLASS: SoundSource ()
function SoundSource:__init()
	self.eventInstances = {}
	self.eventNamePrefix = false
end

function SoundSource:onAttach( entity )
	self._owner = entity
end

function SoundSource:onDetach( entity )
	for evt, k in pairs( self.eventInstances ) do
		evt:stop()
	end
	self.eventInstances = nil
end

function SoundSource:setEventPrefix( prefix )
	self.eventNamePrefix = prefix or false
end

local inheritLoc = inheritLoc
function SoundSource:_addInstance( evt, follow )
	self:clearInstances()
	self.eventInstances[ evt ] = true
	if follow then
		self._owner:_attachTransform( evt )
		evt:forceUpdate()
	end
	return evt
end

function SoundSource:_playEvent3DAt( eventName, x,y,z, follow, looped )
	local prefix = self.eventNamePrefix
	if prefix then eventName = prefix..eventName end
	local evt	
	evt = MOAIFmodEventMgr.playEvent3D( eventName, x,y,z )
	if evt then
		return self:_addInstance( evt, follow~=false )
	else
		_error( 'sound event not found:', eventName )
	end
end

function SoundSource:playEvent3DAt( eventName, x,y,z, follow )
	return self:_playEvent3DAt( eventName, x,y,z, follow, nil )
end

function SoundSource:playEvent3D( eventName, follow )
	local x,y,z
	x,y,z = self._owner:getWorldLoc()
	return self:playEvent3DAt( eventName, x,y,z, follow )
end

function SoundSource:loopEvent3DAt( eventName, x,y,z, follow )
	return self:_playEvent3DAt( eventName, x,y,z, follow, true )
end

function SoundSource:loopEvent3D( eventName, follow )
	local x,y,z
	x,y,z = self._owner:getWorldLoc()
	return self:loopEvent3DAt( eventName, x,y,z, follow )
end

--------------------------------------------------------------------
function SoundSource:_playEvent2D( eventName, looped )
	local prefix = self.eventNamePrefix
	if prefix then eventName = prefix..eventName end
	local evt = MOAIFmodEventMgr.playEvent2D( eventName, looped )
	if evt then
		return self:_addInstance( evt, false )
	else
		_error( 'sound event not found:', eventName )
	end
end

function SoundSource:playEvent2D( eventName )
	return self:_playEvent2D( eventName, nil )
end

function SoundSource:loopEvent2D( eventName )
	return self:_playEvent2D( eventName, true )
end

function SoundSource:isBusy()
	self:clearInstances()
	return next(self.eventInstances) ~= nil
end
	
function SoundSource:clearInstances()
	local t1 = {}
	for evt, k in pairs( self.eventInstances ) do
		if evt:isValid() then
			t1[ evt ] = k
		end
	end
	self.eventInstances = t1
end
