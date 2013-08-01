module 'mock'


--------------------------------------------------------------------
CLASS: ParticleSystem ()
wrapWithMoaiPropMethods( ParticleSystem, '_system' )

function ParticleSystem:__init( config )
	self._system = config:buildSystem()
	self._config = config
	self._system:start()
end

function ParticleSystem:onAttach( owner )
	owner:_insertPropToLayer( self._system )
	self._owner = owner
end

function ParticleSystem:onDetach( owner )
	owner:_removePropFromLayer( self._system )
	self.config:_pushToPool( self._system )
end

--------------------------------------------------------------------
function ParticleSystem:start()
	return self._system:start()
end


--------------------------------------------------------------------
function ParticleSystem:addEmitter( emitterName )
	if not emitterName then
		local em = MOAIParticleTimedEmitter.new()
		self._owner:_attachTransform( em )
		em:forceUpdate()
		em:setSystem( self._system )		
		em:start()
		return em
	end

	local em = self._config:buildEmitter( emitterName )
	self._owner:_attachTransform( em )
	em:forceUpdate()
	em:setSystem( self._system )
	em:start()
	--TODO: attach as new component?
	return em
end

function ParticleSystem:clearEmitters()
end

function ParticleSystem:getState( name )
end

function ParticleSystem:addForceToAll( force )
end

function ParticleSystem:addForceToState( stateName, force )
end

--------------------------------------------------------------------
registerComponentType( 'ParticleSystem', ParticleSystem )

function Entity:addParticleSystem( option )
	return self:attach( ParticleSystem( option ) )
end

updateAllSubClasses( Entity )

