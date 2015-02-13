module 'mock'

CLASS: ParticleEmitter ()
	:MODEL{
		Field 'system'  :type( ParticleSystem );
		Field 'emitterName' :string() :getset('EmitterName');
	}

wrapWithMoaiTransformMethods( ParticleEmitter, 'emitter' )

function ParticleEmitter:__init()
	self.system      = false
	self.emitter     = false
	self.emitterName = 'default'
end

function ParticleEmitter:onStart()
	self:updateEmitter()
end

function ParticleEmitter:onDetach()
	self:stop()
end

function ParticleEmitter:getEmitterName()
	return self.emitterName
end

function ParticleEmitter:setEmitterName( n )
	self.emitterName = n
	-- self:updateEmitter()
end

function ParticleEmitter:updateEmitter()
	local system = self.system
	if not system then return end

	if self.emitter then self.emitter:stop() end
	local name = self.emitterName
	local emitter = name and system:addEmitter( name )
	self.emitter = emitter
	if emitter then
		emitter:start()
		self._entity:_attachTransform( emitter )
	end
end

function ParticleEmitter:surge( count )
	if self.emitter then
		return self.emitter:surge( count )
	end
end

function ParticleEmitter:pause()
	if self.emitter then
		self.emitter:pause()
	end
end


function ParticleEmitter:start()
	if self.emitter then
		self.emitter:start()
	end
end


function ParticleEmitter:stop()
	if self.emitter then
		self.emitter:stop()
	end
end

mock.registerComponent( 'ParticleEmitter', ParticleEmitter )
