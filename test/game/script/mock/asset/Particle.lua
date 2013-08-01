require 'mock.asset.ParticleHelper'
require 'mock.asset.ParticleProcs'
module 'mock'

local makeParticleSystem, makeParticleForce, makeParticleEmitter
local function _unpack(m)
	local tt=type(m)
	if tt=='number' then return m,m end
	if tt=='table' then  return unpack(m) end
	if tt=='function' then  return m() end
	error('????')
end

--------------------------------------------------------------------
CLASS: ParticleSystemConfig ()
function ParticleSystemConfig:__init( data )
	self.data = data
	-- self.dynamicState = data.dynamicState == true
	self.allowPool = data.allowPool ~= false
	--poolable system needs state&emitters
	self.prebuiltStates  = false
	self.prebuiltScripts = {}
	self.systemPool      = {}
	self.emitterDatas    = {}
	self.stateCount      = 0
	self.regCount        = 0
	
	self:_prebuild()
end

function ParticleSystemConfig:requestSystem() --TODO: pool?
	return self:buildSystem()
end

function ParticleSystemConfig:buildScript( s )
	local cache = self.scriptCache
	local script = cache[ s ]
	if s then return s end
	s = makeParticleScript( s )
end

function ParticleSystemConfig:_prebuild()
	--build scripts
	local data = self.data
	local states = {}
	local scripts = {}
	local reg = {}

	for name, sdata in pairs( data.states ) do
		self.stateCount = self.stateCount + 1
		local iscript, rscript = false, false
		if sdata.init then
			iscript = makeParticleScript( sdata.init, reg )
		end
		if sdata.render then
			rscript = makeParticleScript( sdata.render, reg )
		end
		scripts[ sdata ] = { iscript, rscript }
	end

	if reg.named then
		for k,r in pairs(reg.named) do
			if r.referred then 
				self.regCount= r.number>regCount and r.number or regCount
			end
		end
	end

	self.prebuiltScripts = scripts

	if self.allowPool then
		local sys = self:buildSystem()
		self:_pushToPool( sys )
	end

	if data.emitters then
		local emitterDatas = self.emitterDatas
		for k, d in pairs( data.emitters ) do
			emitterDatas[ k ] = d
		end
	end

end

function ParticleSystemConfig:_pushToPool( sys )
	if not self.allowPool then return end
	self.systemPool[ sys ] = true
end

function ParticleSystemConfig:_buildState( sdata )
	local scripts = assert( self.prebuiltScripts[ sdata ], sdata )
	local state = MOAIParticleState.new()

	if sdata.damping  then state:setDamping( sdata.damping ) end
	if sdata.mass     then state:setMass( _unpack(sdata.mass) ) end
	if sdata.term     then state:setTerm( _unpack(sdata.term) ) end
		
	if scripts[1] then state:setInitScript   ( scripts[1] ) end
	if scripts[2] then state:setRenderScript ( scripts[2] ) end
	
	if sdata.forces then
		for i,f in ipairs(sdata.forces) do
			if type(f)=='table' then
				local force=makeParticleForce(f)
				state:pushForce(force)
			else
				state:pushForce(f)
			end
		end
	end

	return state
end

function ParticleSystemConfig:_buildStates( )
	local allowPool = self.allowPool
	if allowPool and self.prebuiltStates then return self.prebuiltStates end

	local data       = self.data
	local stateCount = self.stateCount
	local states     = {}
	local stateNames = {}
	for i, sdata in ipairs( data.states ) do
		local s = self:_buildState( sdata )
		if s.name then
			stateNames[ s.name ] = s
		end
		states[ i ] = s
	end

	for i, s in ipairs( states ) do --link states
		local nextName = s.next
		local ns
		if nextName then
			ns = stateName [ nextName ]  --ASSERT here
		elseif i<stateCount then --try next in list
			ns = states[ i + 1 ]			
		end
		if ns then s:setNext( ns ) end
	end

	if allowPool then self.prebuiltStates = states end

	return states
end


function ParticleSystemConfig:buildSystem()
	local allowPool = self.allowPool
	if allowPool then
		local pool = self.systemPool
		local sys = next( pool )
		if sys then 
			pool[ sys ] = nil
			return sys
		end
	end

	--Build System
	local data = self.data
	local system = MOAIParticleSystem.new()
	system:reserveStates( self.stateCount )
	for i, s in ipairs( self:_buildStates() ) do
		system:setState( i, s )
	end
	system:reserveSprites   ( data.sprites or 100 )
	system:reserveParticles ( data.particles or 50, self.regCount+1 )

	assert(data.deck) 
	setupMoaiProp( system, data )
	if data.surge then system:surge(data.surge) end
	system.config = self
	
	return system
end

function ParticleSystemConfig:buildEmitter( emitterName )
	local edata = self.emitterDatas[ emitterName ]
	assert( edata, 'emitter not found:'..emitterName )

	local em
	if edata.type == 'distance' then
		em = MOAIParticleDistanceEmitter.new()
		if edata.distance then em:setDistance( _unpack( edata.distance ) ) end
	else
		em = MOAIParticleTimedEmitter.new()
		if edata.frequency then em:setFrequency( _unpack( edata.frequency ) ) end
	end

	if edata.angle then em:setAngle( _unpack(edata.angle) ) end
	if edata.magnitude then em:setMagnitude( _unpack(edata.magnitude) ) end
	if edata.radius then 
		em:setRadius( _unpack(edata.radius) )
	elseif edata.rect then 
		em:setRect( _unpack(edata.rect) )
	end
	if edata.emission then em:setEmission(_unpack(edata.emission)) end
	if edata.surge then em:surge(edata.surge) end
	return em
end


--[[
	task of ParticleSystem is to:
	1. hold ParticleState
	2. hold ParticleEmitterSettings
]]

function loadParticleSystem( node )
	local systemData = loadAssetDataTable( node:getObjectFile('def') or node:getFilePath() )
	if systemData then 
		return ParticleSystemConfig( systemData )
	else
		return false
	end
end

registerAssetLoader( 'particle_system', loadParticleSystem )


--------------------------------------------------------------------

function makeParticleForce(option)
	assert(type(option)=='table')
	local ft=option.type or 'force'
	
	local f=MOAIParticleForce.new()

	if ft=='force' then
		f:setType(MOAIParticleForce.FORCE)
	elseif ft=='gravity' then
		f:setType(MOAIParticleForce.GRAVITY)
	elseif ft=='offset' then
		f:setType(MOAIParticleForce.OFFSET)
	end
	if option.magnitude then
		if option.radius then
			if option.magnitude>0 then
				f:initBasin(option.radius,option.magnitude)
			else
				f:initAttractor(option.radius,-option.magnitude)
			end
		else
			f:initRadial(option.magnitude)
		end
	else
		f:initLinear(option.x or 0,option.y or 0)
	end
	f.name=option.name
	return f
end


