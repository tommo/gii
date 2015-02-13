module 'mock'

--------------------------------------------------------------------
local function _unpack(m)
	local tt=type(m)
	if tt=='number' then return m,m end
	if tt=='table' then  return unpack(m) end
	if tt=='function' then  return m() end
	error('????')
end

--------------------------------------------------------------------
CLASS: EffectNodeParticleSystem  ( EffectNode )
CLASS: EffectNodeParticleState   ( EffectNode )
CLASS: EffectNodeParticleEmitter ( EffectTransformNode )
CLASS: EffectNodeParticleForce   ( EffectTransformNode )

----------------------------------------------------------------------
--CLASS: EffectNodeParticleSystem
--------------------------------------------------------------------
EffectNodeParticleSystem :MODEL{
	Field 'blend'        :enum( EnumBlendMode );
	Field 'deck'         :asset( 'deck2d\\..*' ); -- :meta{ search_terms = 'particle' };
	'----';
	Field 'particleLimit'    :int()  :range(0);
	Field 'spriteLimit'      :int()  :range(0);
	'----';
	Field 'syncTransform' :boolean();
}

function EffectNodeParticleSystem:__init()
	self.particleLimit = 100
	self.spriteLimit   = self.particleLimit
	self.blend = 'add'
	self.deck  = false
	self.syncTransform = false
end

function EffectNodeParticleSystem:getDefaultName()
	return 'particle'
end

function EffectNodeParticleSystem:getTypeName()
	return 'system'
end

function EffectNodeParticleSystem:postBuild()
	local states   = {}
	local forces   = {}
	local emitters = {}
	--build state
	local regs = {}
	for i, child in pairs( self.children ) do
		local c = child:getClassName()
		if child:isInstance( EffectNodeParticleState ) then
			table.insert( states, child )
			child:_buildScript( regs )
		elseif child:isInstance( EffectNodeParticleEmitter ) then
			table.insert( emitters, child )
		elseif child:isInstance( EffectNodeParticleForce ) then
			table.insert( forces, child )
		end
	end

	local regCount = 0
	if regs.named then
		for k,r in pairs(regs.named) do
			if r.referred then 
				regCount = math.max( r.number, regCount )
			end
		end
	end
	self.regCount     = regCount
	self.emitterNodes = emitters
	self.stateNodes   = states
	self.forceNodes   = forces
	self.stateCount   = #self.stateNodes
	self._built = true	
end

function EffectNodeParticleSystem:buildSystem( system, fxState )
	assert( self._built )
	system = system or MOAIParticleSystem.new()
	system:reserveStates    ( self.stateCount )
	system:reserveSprites   ( self.spriteLimit )
	system:reserveParticles ( self.particleLimit, self.regCount )
	system:setDrawOrder( MOAIParticleSystem.ORDER_REVERSE )

	system.config = self

	setPropBlend( system, self.blend )
	local deck = mock.loadAsset( self.deck )
	system:setDeck( deck )
	
	--build child nodes	
	local emitters = {}
	local forces   = {}
	
	local stateNodes   = self.stateNodes
	local forceNodes   = self.forceNodes
	local emitterNodes = self.emitterNodes

	--build forces
	for i, node in ipairs( forceNodes ) do
		local force = node:buildForce()
		forces[ i ] = force
		fxState[ node ] = force
	end
	
	--build states
	for i, s in ipairs( stateNodes ) do
		local state = s:buildState()
		for j, f in ipairs( forces ) do
			state:pushForce( f )
		end
		system:setState( i, state )
	end

	--add emitters
	for i, node in pairs( emitterNodes ) do
		local em = node:buildEmitter()
		em:setSystem( system )
		emitters[ i ] = em
		fxState[ node ] = em
	end

	fxState[ self ] = system
		
	return system, emitters, forces
end

local _count = 0
function EffectNodeParticleSystem:onLoad( fxState )
	local system, emitters, forces = self:buildSystem( nil, fxState )	
	fxState:linkVisible  ( system )
	fxState:attachAction ( system )
	fxState:linkPartition( system )

	for _, em in pairs( emitters ) do
		fxState:attachAction( em )
	end
	_count = _count + 1

	if self.syncTransform then --attach system only
		fxState:linkTransform( system )
	else --attach emitter/forces only
		--TODO: need rotation/scale
		for _,em in pairs( emitters ) do
			fxState:linkTransform( em )
		end
		for _,f in pairs( forces ) do
			fxState:linkTransform( f )
		end
	end
end

function EffectNodeParticleSystem:onStop( fxState )
	local system = fxState[ self ]
	system:stop()
	system:setPartition( nil )	
end

--------------------------------------------------------------------
--CLASS:  EffectNodeParticleState
--------------------------------------------------------------------
CLASS: ParticleScriptParam ()

function ParticleScriptParam:get()
end

function ParticleScriptParam:set( ... )
end

--------------------------------------------------------------------
CLASS: ParticleScriptParamNumber ( ParticleScriptParam )
	:MODEL{
 		Field 'key'    :string();
 		Field 'value'  :number();
	}

function ParticleScriptParamNumber:__init()
	self.value = 1
end

function ParticleScriptParamNumber:set( v )
	self.value = v
end

function ParticleScriptParamNumber:get()
	return self.value
end

--------------------------------------------------------------------
CLASS: ParticleScriptParamColor ( ParticleScriptParam )
	:MODEL{
 		Field 'key'    :string();
 		Field 'color'  :type('color');
	}
function ParticleScriptParamColor:__init()
	self.color = {1,1,1,1}
end

function ParticleScriptParamColor:set( r,g,b,a )
	self.color = {
		r or 1,
		g or 1,
		b or 1,
		a or 1,
	}
end

function ParticleScriptParamColor:get()
	return unpack( self.color )
end

--------------------------------------------------------------------
--------------------------------------------------------------------
EffectNodeParticleState :MODEL{
		Field 'name'         :string() ;
		Field 'active'       :boolean() ;
		Field 'life'         :type('vec2') :range(0) :getset('Life');
		Field 'script'       :string() :no_edit();
		Field 'params'       :array( ParticleScriptParam ) :sub() :no_edit();
	}

function EffectNodeParticleState:__init()
	self.name         = 'state'
	self.active       = true
	self.life         = { 1, 1 }
	self.script = [[
function render()
	proc.p.moveAlong()
	sprite()
end
]]
	self.params = {}
	self.moaiParticleState = MOAIParticleState.new()
end

function EffectNodeParticleState:getDefaultName()
	return 'state'
end

function EffectNodeParticleState:getTypeName()
	return 'state'
end

function EffectNodeParticleState:getParamN( k )	
	local par = self.params[ k ]
	if not par then return 0 end
	return par:get()
end

function EffectNodeParticleState:setParamN( k, v )
	local par = self.params[ k ]
	if not par then
		par = ParticleScriptParamNumber()
		self.params[ k ] = par
	end
	par:set( v )
end

function EffectNodeParticleState:getParamC( k )	
	local par = self.params[ k ]
	if not par then return 1,1,1,1 end
	return par:get()
end

function EffectNodeParticleState:getParamCStr( k )	
	local r,g,b,a = self:getParamC( k )
	return string.format( '%.3f,%.3f,%.3f,%.3f', r,g,b,a )
end

function EffectNodeParticleState:setParamC( k, r,g,b,a )
	local par = self.params[ k ]
	if not par then
		par = ParticleScriptParamColor()
		self.params[ k ] = par
	end
	par:set( r,g,b,a )
end

function EffectNodeParticleState:_buildScript( regs )
	regs = regs or {}
	self:updateScriptParams()
	local script = self.script
	local script1 = script:gsub(
		'${(%w+)}', 
		function(k) return self:getParamN( k ) end
	)
	script1 = script1:gsub(
		'${{(%w+)}}', 
		function(k) return self:getParamCStr( k ) end
	)
	
	local chunk, err = loadstring( script1, 'PARTICLE SCRIPT' )
	local env = {}
	--error
	
	if not chunk then
		print( err )
		return
	end

	setfenv( chunk, env )
	local res, err = pcall( chunk )
	if not res then
		print( err )
	end

	local initFunc   = env['init']
	local renderFunc = env['render']

	local iscript = initFunc and makeParticleScript( initFunc, regs ) or false
	local rscript = renderFunc and makeParticleScript( renderFunc, regs ) or false
	self.builtScripts = { iscript, rscript }
end

function EffectNodeParticleState:buildState()
	local state = MOAIParticleState.new()
	state:clearForces()

	if self.damping  then state:setDamping( self.damping ) end
	if self.mass     then state:setMass( _unpack(self.mass) ) end
	if self.life     then state:setTerm( _unpack(self.life) ) end
	local iscript, rscript = unpack( self.builtScripts )
	if iscript then state:setInitScript   ( iscript ) end
	if rscript then state:setRenderScript ( rscript ) end
	return state
end

function EffectNodeParticleState:setLife( l1, l2 )
	self.life         = { l1, l2 or l1 }
end

function EffectNodeParticleState:getLife()
	return unpack( self.life )
end

function EffectNodeParticleState:updateScriptParams()
	local script = self.script
	--find number params
	local params = self.params
	local checked = {}
	for n in string.gmatch( script, '${(%w+)}' ) do
		if not params[ n ] then			
			self:setParamN( n, 1 )
		end
		checked[ n ] = true
	end

	--find color params
	for n in string.gmatch( script, '${{(%w+)}}' ) do
		if not params[ n ] then
			self:setParamC( n, 1,1,1,1 )
		end
		checked[ n ] = true
	end

	--remove unwanted param?
	local toremove = {}
	for k in pairs( self.params ) do
		if not checked[ k ] then toremove[ k ] = true end
	end
	for k in pairs( toremove ) do
		self.params[ k ] = nil
	end

end

function EffectNodeParticleState:buildParamProxy()
	self:updateScriptParams()
	local proxyClass = _rawClass()
	local modelTable = {}
	for k, param in pairs( self.params ) do
		local f = Field( k )
		if param:isInstance( ParticleScriptParamColor ) then
			f:type('color')
		else
			f:number()
		end
		f:set( function( obj, ... ) return param:set( ... ) end )
		f:get( function( obj ) return param:get() end )
		table.insert( modelTable, f )
	end
	proxyClass:MODEL( modelTable )
	return proxyClass()
end


----------------------------------------------------------------------
--CLASS: EffectNodeParticleEmitter
--------------------------------------------------------------------
EffectNodeParticleEmitter :MODEL {
		'----';
		Field 'emission'  :type('vec2') :range(0)  :getset('Emission');		
		Field 'duration'  :number();
		Field 'surge'     :int();
		'----';
		Field 'magnitude' :type('vec2') :getset('Magnitude');		
		Field 'angle'     :type('vec2') :range(-360, 360) :getset('Angle');	
		'----';
		Field 'radius'    :type('vec2') :range(0) :getset('Radius');
		Field 'rect'      :type('vec2') :range(0) :getset('Rect');
	}

function EffectNodeParticleEmitter:__init()
	self.name      = 'emitter'
	self.magnitude = { 0, 0 }
	self.angle     = { 0, 0 }
	self.surge     = 0
	self.emission  = {1,1}
	self.radius    = {0,0}
	self.rect      = {0,0}
	self.duration  = -1
end

function EffectNodeParticleEmitter:updateEmitterCommon( em )
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
	self:applyTransformToProp( em )	
end

function EffectNodeParticleEmitter:getDefaultName()
	return 'emitter'
end

function EffectNodeParticleEmitter:getTypeName()
	return 'emitter'
end

function EffectNodeParticleEmitter:buildEmitter()
	local emitter = MOAIParticleTimedEmitter.new()
	emitter:updateEmitterCommon( emitter )
	return emitter
end

function EffectNodeParticleEmitter:getTransformNode( state )
	return state[ self ]
end

function EffectNodeParticleEmitter:setActive( state, active )
	local em = state[ self ]
	if not em then return end
	if active then
		em:start()
	else
		em:stop()
	end
end

--------------------------------------------------------------------
function EffectNodeParticleEmitter:setEmission( e1, e2 )
	self.emission = { e1 or 0 , e2 or 0 }
end

function EffectNodeParticleEmitter:getEmission()
	return unpack( self.emission )
end

function EffectNodeParticleEmitter:setMagnitude( min, max )
	min = min or 0
	self.magnitude = { min, max or min }
end

function EffectNodeParticleEmitter:getMagnitude()
	return unpack( self.magnitude )
end

function EffectNodeParticleEmitter:setAngle( min, max )
	min = min or 0
	self.angle = { min, max or min }
end

function EffectNodeParticleEmitter:getAngle()
	return unpack( self.angle )
end

function EffectNodeParticleEmitter:setRadius( r1, r2 )
	self.radius = { r1 or 0 , r2 or 0 }
end

function EffectNodeParticleEmitter:getRadius()
	return unpack( self.radius )
end

function EffectNodeParticleEmitter:setRect( w, h )
	self.rect = { w or 1, h or 1 }
end

function EffectNodeParticleEmitter:getRect()
	return unpack( self.rect )
end


--------------------------------------------------------------------
--CLASS: EffectNodeParticleTimedEmitter
--------------------------------------------------------------------
CLASS: EffectNodeParticleTimedEmitter( EffectNodeParticleEmitter )
:MODEL{
	Field 'frequency' :type('vec2') :range(0)  :getset('Frequency');
}

function EffectNodeParticleTimedEmitter:__init()
	self.frequency = { 10, 10 }
end

function EffectNodeParticleTimedEmitter:getTypeName()
	return 'emitter-timed'
end

function EffectNodeParticleTimedEmitter:buildEmitter()
	local emitter = MOAIParticleTimedEmitter.new()
	self:updateEmitterCommon( emitter )
	local f1, f2 = _unpack( self.frequency )		
	emitter:setFrequency( 1/f1, f2 and 1/f2 or 1/f1 )
	return emitter
end

function EffectNodeParticleTimedEmitter:setFrequency( f1, f2 )
	self.frequency = { f1 or 0 , f2 or 0 }
end

function EffectNodeParticleTimedEmitter:getFrequency()
	return unpack( self.frequency )
end

--------------------------------------------------------------------
--CLASS: EffectNodeParticleDistanceEmitter
--------------------------------------------------------------------
CLASS: EffectNodeParticleDistanceEmitter( EffectNodeParticleEmitter )
:MODEL{
	Field 'distance'  :number()  :range(0) ;
}

function EffectNodeParticleDistanceEmitter:__init()
	self.distance  = 10
end

function EffectNodeParticleDistanceEmitter:getTypeName()
	return 'emitter-distance'
end

function EffectNodeParticleDistanceEmitter:buildEmitter()
	local emitter = MOAIParticleDistanceEmitter.new()
	self:updateEmitterCommon( emitter)
	emitter:setDistance( _unpack( self.distance ) )
	return emitter
end


----------------------------------------------------------------------
--CLASS: EffectNodeParticleForce
--------------------------------------------------------------------
EffectNodeParticleForce :MODEL{
	Field 'forceType' :enum( EnumParticleForceType );
	'----';
	Field 'loc'       :type('vec3') :tuple_getset('loc') :label('Loc'); 
	'----';
}

function EffectNodeParticleForce:__init()
	self.forceType = MOAIParticleForce.OFFSET
	self.loc = {0,0,0}
end

function EffectNodeParticleForce:getDefaultName()
	return 'force'
end

function EffectNodeParticleForce:getTypeName()
	return 'force'
end

function EffectNodeParticleForce:buildForce()
	local f = MOAIParticleForce.new()
	f:setLoc( unpack( self.loc ) )
	self:updateForce( f )
	return f
end

function EffectNodeParticleForce:updateForce( f )
end

function EffectNodeParticleForce:getTransformNode( state )
	return state[ self ]
end

--------------------------------------------------------------------
CLASS: EffectNodeForceAttractor ( EffectNodeParticleForce )
	:MODEL{
		Field 'radius';
		Field 'magnitude';
}

function EffectNodeForceAttractor:__init()
	self.radius = 100
	self.magnitude = 1	
end

function EffectNodeForceAttractor:updateForce( f )
	f:initAttractor( self.radius, self.magnitude )
end

function EffectNodeForceAttractor:getTypeName()
	return 'force-attractor'
end

function EffectNodeForceAttractor:getDefaultName()
	return 'attractor'
end


--------------------------------------------------------------------
CLASS: EffectNodeForceBasin ( EffectNodeParticleForce )
	:MODEL{
		Field 'radius';
		Field 'magnitude';
}

function EffectNodeForceBasin:__init()
	self.radius = 100
	self.magnitude = 1	
end

function EffectNodeForceBasin:updateForce( f )
	f:initBasin( self.radius, self.magnitude )
end

function EffectNodeForceBasin:getDefaultName()
	return 'basin'
end

function EffectNodeForceBasin:getTypeName()
	return 'force-basin'
end

--------------------------------------------------------------------
CLASS: EffectNodeForceLinear ( EffectNodeParticleForce )
	:MODEL{
		Field 'vector'       :type('vec3') :getset('Vector') :label('Vector'); 
}

function EffectNodeForceLinear:__init()
	self.vector = {1,0,0}
end

function EffectNodeForceLinear:setVector( x,y,z )
	self.vector = {x,y,z}
end

function EffectNodeForceLinear:getVector()
	return unpack( self.vector )
end

function EffectNodeForceLinear:updateForce( f )
	f:initLinear( unpack( self.vector ) )
end

function EffectNodeForceLinear:getTypeName()
	return 'force-linear'
end

function EffectNodeForceLinear:getDefaultName()
	return 'linear'
end


--------------------------------------------------------------------
CLASS: EffectNodeForceRadial ( EffectNodeParticleForce )
	:MODEL{
		Field 'magnitude';
}

function EffectNodeForceRadial:__init()
	self.magnitude = 1	
end

function EffectNodeForceRadial:updateForce( f )
	f:initRadial( self.magnitude )
end

function EffectNodeForceRadial:getTypeName()
	return 'force-radial'
end

function EffectNodeForceRadial:getDefaultName()
	return 'radial'
end


registerTopEffectNodeType( 
	'particle-system',
	EffectNodeParticleSystem,
	{ 
		'particle-state'             ,
		'particle-emitter-timed'     , 
		'particle-emitter-distance'  ,
		'particle-force-linear'      ,
		'particle-force-radial'      ,
		'particle-force-attractor'   ,
		'particle-force-basin'       ,
	}
)

registerEffectNodeType( 
	'particle-state',
	EffectNodeParticleState
)

registerEffectNodeType( 
	'particle-emitter-timed',
	EffectNodeParticleTimedEmitter,
	EffectCategoryTransform
)

registerEffectNodeType( 
	'particle-emitter-distance',
	EffectNodeParticleDistanceEmitter,
	EffectCategoryTransform
)

registerEffectNodeType( 
	'particle-force-linear',
	EffectNodeForceLinear,
	EffectCategoryTransform
)

registerEffectNodeType( 
	'particle-force-radial',
	EffectNodeForceRadial,
	EffectCategoryTransform
)

registerEffectNodeType( 
	'particle-force-attractor',
	EffectNodeForceAttractor,
	EffectCategoryTransform
)

registerEffectNodeType( 
	'particle-force-basin',
	EffectNodeForceBasin,
	EffectCategoryTransform
)

