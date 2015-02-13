require 'mock.asset.ParticleHelper'
require 'mock.asset.ParticleProcs'
module 'mock'

local makeParticleSystem, makeParticleForce, makeParticleEmitter

--------------------------------------------------------------------
local function _unpack(m)
	local tt=type(m)
	if tt=='number' then return m,m end
	if tt=='table' then  return unpack(m) end
	if tt=='function' then  return m() end
	error('????')
end


local EnumParticleType = { 
	{'distance', 'distance'},
	{'timed', 'timed' }
}

--------------------------------------------------------------------
CLASS:  ParticleEmitterConfig()
	:MODEL {
		Field 'name'      :string();
		Field 'type'      :enum( EnumParticleType );
		Field 'distance'  :number()  :range(0) ;
		Field 'frequency' :type('vec2') :range(0)  :getset('Frequency');
		Field 'emission'  :type('vec2') :range(0)  :getset('Emission');		
		Field 'duration'  :number();
		Field 'surge'     :int();
		'----';
		Field 'magnitude' :type('vec2') :range(0)  :getset('Magnitude');		
		Field 'angle'     :type('vec2') :range(-360, 360) :getset('Angle');	
		'----';
		Field 'radius'    :type('vec2') :range(0) :getset('Radius');
		Field 'rect'      :type('vec2') :range(0) :getset('Rect');
	}

function ParticleEmitterConfig:__init()
	self.name      = 'emitter'
	self.type      = 'timed'
	self.distance  = 10
	self.frequency = { 10, 10 }
	self.magnitude = { 10, 10 }
	self.angle     = { 0, 0 }
	self.surge     = 0
	self.emission  = {1,1}
	self.radius    = {5,5}
	self.rect      = {0,0}
	self.duration  = -1
end

function ParticleEmitterConfig:build()
	local em
	if self.type == 'distance' then
		em = MOAIParticleDistanceEmitter.new()
	else
		em = MOAIParticleTimedEmitter.new()
	end	
	self:updateEmitter( em )
	return em
end

function ParticleEmitterConfig:updateEmitter( em )

	if self.distance and em.setDistance then em:setDistance( _unpack( self.distance ) ) end
	if self.frequency and em.setFrequency then 
		local f1, f2 = _unpack( self.frequency )		
		em:setFrequency( 1/f1, f2 and 1/f2 or 1/f1 )
	end

	em.name = self.name
	if self.angle     then em:setAngle( _unpack(self.angle) ) end
	if self.magnitude then em:setMagnitude( _unpack(self.magnitude) ) end

	if self.radius[1] > 0 or self.radius[1] > 0 then 
		em:setRadius( _unpack(self.radius) )
	else
		local w, h = unpack( self.rect )
		em:setRect( -w/2, -h/2, w/2, h/2 )
	end
	if self.emission then em:setEmission(_unpack(self.emission)) end
	if self.surge    then em:surge(self.surge) end
	if em.setDuration then 
		em:setDuration( self.duration )
	end

end

--------------------------------------------------------------------
function ParticleEmitterConfig:setFrequency( f1, f2 )
	self.frequency = { f1 or 0 , f2 or 0 }
end

function ParticleEmitterConfig:getFrequency()
	return unpack( self.frequency )
end

function ParticleEmitterConfig:setEmission( e1, e2 )
	self.emission = { e1 or 0 , e2 or 0 }
end

function ParticleEmitterConfig:getEmission()
	return unpack( self.emission )
end

function ParticleEmitterConfig:setMagnitude( min, max )
	min = min or 0
	self.magnitude = { min, max or min }
end

function ParticleEmitterConfig:getMagnitude()
	return unpack( self.magnitude )
end

function ParticleEmitterConfig:setAngle( min, max )
	min = min or 0
	self.angle = { min, max or min }
end

function ParticleEmitterConfig:getAngle()
	return unpack( self.angle )
end

function ParticleEmitterConfig:setRadius( r1, r2 )
	self.radius = { r1 or 0 , r2 or 0 }
end

function ParticleEmitterConfig:getRadius()
	return unpack( self.radius )
end

function ParticleEmitterConfig:setRect( w, h )
	self.rect = { w or 1, h or 1 }
end

function ParticleEmitterConfig:getRect()
	return unpack( self.rect )
end

--------------------------------------------------------------------
CLASS:  ParticleStateConfig()
	:MODEL {
		Field 'name'         :string() ;
		Field 'active'       :boolean() ;
		Field 'life'         :type('vec2') :range(0) :getset('Life');
		Field 'initScript'   :string() :no_edit();
		Field 'renderScript' :string() :no_edit();
	}


function ParticleStateConfig:__init()
	self.name         = 'state'
	self.active       = true
	self.initScript   = ''
	self.renderScript = 'proc.p.moveAlong()\nsprite()\n'
	self.life         = { 1, 1 }
end

function ParticleStateConfig:build( regs )
	regs = regs or {}

	local iscript, rscript = false, false
	local init,render
	init   = self.initScript and string.trim(self.initScript) or ''
	render = self.renderScript and string.trim(self.renderScript) or ''

	if  init ~= '' then
		local initFunc = loadstring( init )
		if initFunc then iscript = makeParticleScript( initFunc, regs ) end
	end
	if render ~= '' then
		renderFunc = loadstring( render )
		if renderFunc then	rscript = makeParticleScript( renderFunc, regs ) end
	end

	local regCount = 0
	if regs.named then
		for k,r in pairs(regs.named) do
			if r.referred then 
				regCount = math.max( r.number, regCount )
			end
		end
	end

	builtScripts = { iscript, rscript }
	
	local state = MOAIParticleState.new()

	if self.damping  then state:setDamping( self.damping ) end
	if self.mass     then state:setMass( _unpack(self.mass) ) end
	if self.life     then state:setTerm( _unpack(self.life) ) end
		
	if builtScripts[1] then state:setInitScript   ( builtScripts[1] ) end
	if builtScripts[2] then state:setRenderScript ( builtScripts[2] ) end
	
	-- if self.forces then
	-- 	for i,f in ipairs(self.forces) do
	-- 		if type(f)=='table' then
	-- 			local force=makeParticleForce(f)
	-- 			state:pushForce( force )
	-- 		else
	-- 			state:pushForce( f )
	-- 		end
	-- 	end
	-- end

	return state
end

function ParticleStateConfig:setLife( l1, l2 )
	self.life         = { l1, l2 or l1 }
end

function ParticleStateConfig:getLife()
	return unpack( self.life )
end

--------------------------------------------------------------------
BLEND_MODES = {
	{'alpha',    'alpha'},
	{'add',      'add'},
	{'multiply', 'multiply'},
	{'normal',   'normal'},
	{'mask',     'mask'},
	{'solid',    'solid'},
}

CLASS:  ParticleSystemConfig()
	:MODEL{
		Field 'particles'    :int()  :range(0);
		Field 'sprites'      :int()  :range(0);
		Field 'emitters'     :array( ParticleEmitterConfig ) :sub() :no_edit();
		Field 'states'       :array( ParticleStateConfig )   :ref() :no_edit(); 
		Field 'blend'        :enum( BLEND_MODES );
		Field 'deck'         :asset( 'deck2d\\..*' );
	}

function ParticleSystemConfig:__init()
	self.particles = 100
	self.sprites   = 100
	self.deck      = false
	self.stateCount = 0
	self.emitters  = {}
	self.states    = {}
	self.allowPool = true
	self.systemPool = {}
end

function ParticleSystemConfig:addEmitterConfig( config )
	config = config or ParticleEmitterConfig()
	table.insert( self.emitters, config )
	return config
end

function ParticleSystemConfig:addStateConfig( config )
	config =  config or ParticleStateConfig() 
	table.insert( self.states, config )
	return config
end

function ParticleSystemConfig:update()
end

function ParticleSystemConfig:buildStates()
	local regs = {}

	local builtStates = {}
	for i, state in pairs( self.states ) do
		table.insert( builtStates , state:build( regs ) )
	end
	local regCount = 0
	if regs.named then
		for k,r in pairs(regs.named) do
			if r.referred then 
				regCount = math.max( r.number, regCount )
			end
		end
	end

	return builtStates, regCount
end

function ParticleSystemConfig:buildEmitter( name )
	if not self.builtSystem then
		self:buildSystem() 
	end

	for i, emConfig in ipairs( self.emitters ) do
		if emConfig.name == name then
			local em = emConfig:build()
			em:setSystem( self.builtSystem )
			return em
		end
	end
	return nil
end

function ParticleSystemConfig:buildSystem()
	if self.built then return end

	local system = MOAIParticleSystem.new()
	local states, regCount = self:buildStates( regs )

	system:reserveStates( #states )
	for i, s in ipairs( states ) do
		system:setState( i, s )
	end
	system.particleCount = self.particles or 50
	system.spriteCount   = self.sprites or 100
	system.regCount = regCount + 1 
	system:reserveSprites   ( system.spriteCount )
	system:reserveParticles ( system.particleCount, system.regCount )
	system:setDrawOrder( MOAIParticleSystem.ORDER_REVERSE )
	if self.surge then system:surge(self.surge) end
	
	setupMoaiProp( system, self )

	system.config = self

	self.builtSystem = system
	return system
end

function ParticleSystemConfig:_pushToPool( sys )
	if not self.allowPool then return end
	table.insert( self.systemPool, sys )	
	sys:clearSprites()
	sys:reserveParticles( sys.particleCount, sys.regCount )
end

function ParticleSystemConfig:requestSystem()
	local sys = table.remove( self.systemPool )
	if sys then return sys end
	sys = self:buildSystem()
	return sys
end

--[[
	task of ParticleSystem is to:
	1. hold ParticleState
	2. hold ParticleEmitterSettings
]]

function loadParticleSystem( node )
	local defData   = loadAssetDataTable( node:getObjectFile('def') )
	local systemConfig = deserialize( nil, defData )
	return systemConfig
end


function saveParticleSystem( config, path )
	return serializeToFile( config, path )
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


