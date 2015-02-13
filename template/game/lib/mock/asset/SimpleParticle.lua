module 'mock'

--------------------------------------------------------------------
local function varianceRange( v, variance, minValue, maxValue )
	local min, max = v-variance, v+variance
	if minValue and min < minValue then min = minValue end
	if maxValue and max > maxValue then max = maxValue end
	return { min, max }
end

--------------------------------------------------------------------
local templateInitScript = [[
	--init script
	local function variance(a,b) 
		return b==0 and a or rand(a-b,a+b)
	end

	local function variance1(a,b)	
		return b==0 and a or rand(a-b<0 and 0 or a-b, a+b>1 and 1 or a+b)
	end

	angle=variance($angle,$angleVariance)
		
	s0=variance($startParticleSize,$startParticleSizeVariance)			
	s1=variance($finishParticleSize,$finishParticleSizeVariance)
			
	rot0=variance($rot0,$rot0Variance)
	rot1=variance($rot1,$rot1Variance)

	if '$emitterType'=='gravity' then
		-- speed=variance($speed,$speedVariance)

		-- vx=cos(angle)*speed
		-- vy=sin(angle)*speed
		
		vx = 0
		vy = 0

		if $hasRadAcc then radAcc=variance($radAcc,$radAccVariance)	end
		if $hasTanAcc then tanAcc=variance($tanAcc,$tanAccVariance) end

		if $hasTanAcc or $hasRadAcc then 
			dx=variance($srcX,$srcXVariance)
			dy=variance($srcY,$srcYVariance)
			p.x=p.x+dx
			p.y=p.y+dy
		else
			p.x=p.x+variance($srcX,$srcXVariance)
			p.y=p.y+variance($srcY,$srcYVariance)
		end

	else --radial
		x0=p.x
		y0=p.y

		rps=variance($rps, $rpsVariance)
		
		minRadius=$minRadius
		maxRadius=variance($maxRadius, $maxRadiusVariance)

	end

	r0,g0,b0,a0 = variance1($r0,$r0v),variance1($g0,$g0v),variance1($b0,$b0v),variance1($a0,$a0v)
	r1,g1,b1,a1 = variance1($r1,$r1v),variance1($g1,$g1v),variance1($b1,$b1v),variance1($a1,$a1v)
]]

local templateRenderScript = [[
	--render script
	if '$emitterType'=='gravity' then		
		if $gravityX~=0 then vx=vx+$gravityX end
		if $gravityY~=0 then vy=vy+$gravityY end
		
		if $hasRadAcc or $hasTanAcc then
			a=vecAngle(dy,dx) * (3.14159265355/180)
			
			ca=cos(a)
			sa=sin(a)

			if $hasRadAcc then
				vx=vx+ca*radAcc
				vy=vy+sa*radAcc
			end

			if $hasTanAcc then
				vx=vx-sa*tanAcc
				vy=vy+ca*tanAcc
			end

			-- dx=dx+vx
			-- dy=dy+vy
			dx = dx + p.dx
			dy = dy + p.dy
		end
		
		p.x=p.x+vx
		p.y=p.y+vy

	else --radial

		radius=ease(maxRadius,minRadius)
		
		p.x=x0+cos(angle)*radius
		p.y=y0+sin(angle)*radius

		angle=angle+rps

	end

	sprite()
	local easeType=EaseType.LINEAR
	if $easeR then sp.r = ease( r0, r1,easeType) else sp.r=$r0 end
	if $easeG then sp.g = ease( g0, g1,easeType) else sp.g=$g0 end
	if $easeB then sp.b = ease( b0, b1,easeType) else sp.b=$b0 end
	if $easeA then sp.opacity = ease( a0, a1,easeType) else sp.opacity=$a0 end

	size = ease(s0,s1)
	sp.sx = size
	sp.sy = size

	sp.rot=ease(rot0,rot1)
]]
--------------------------------------------------------------------
---- PEX MODEL
--------------------------------------------------------------------
CLASS: SimpleParticleSystemConfig ()
	:MODEL{
		Field 'deck'          :asset('deck2d\\..*');
		Field 'blend'         :enum( mock.EnumBlendMode );
		Field 'particles'     :int()     :range( 0, 2000 );
		'----';
		Field 'life'           :number() :range( 0, 10 )    :widget('slider');
		Field 'lifeVar'        :number() :range( 0, 10 )    :widget('slider')  :label( 'life.v' );
		Field 'emission'       :int()    :range( 0, 100 )   :widget('slider');
		Field 'frequency'      :number() :range( 0.1, 100 ) :widget('slider');
		Field 'emitSize'       :type('vec2') :range( 0 ) :getset('EmitSize');

		Field 'speed'          :number() :range( 0, 2000 )  :widget('slider');
		Field 'speedVar'       :number() :range( 0, 2000 )  :widget('slider') :label('speed.v');
		Field 'angle'          :number() :range( 0, 360 )  :widget('slider');
		Field 'angleVar'       :number() :range( 0, 180 )  :widget('slider') :label('angle.v');

		'----';
		Field 'size'           :number() :range( 0, 10 )    :widget('slider');
		Field 'size1'          :number() :range( 0, 10 )    :widget('slider');
		Field 'sizeVar'        :number() :range( 0, 10 )    :widget('slider') :label('size.v');
		Field 'rot0'           :number() :range( 0, 3600 )  :widget('slider');
		Field 'rot0Var'        :number() :range( 0, 3600 )  :widget('slider') :label('rot0.v');
		Field 'rot1'           :number() :range( 0, 3600 )  :widget('slider');
		Field 'rot1Var'        :number() :range( 0, 3600 )  :widget('slider') :label('rot1.v');
		
		'----';
		Field 'gravity'       :type('vec2') :range( -5000, 5000 ) :getset('Gravity');
		Field 'accRadial'     :number() :range( -1000, 1000 )  :widget('slider');
		Field 'accRadialVar'  :number() :range( 0, 1000 )  :widget('slider') :label('accRadial.v');
		Field 'accTan'        :number() :range( -1000, 1000 )  :widget('slider');
		Field 'accTanVar'     :number() :range( 0, 1000 )  :widget('slider') :label('accTan.v');
		
		'----';
		Field 'color0'        :type('color') :getset('Color0') ;
		Field 'color1'        :type('color') :getset('Color1') ;
		Field 'colorVarR'     :number() :range( 0, 1 ) :widget('slider') :label('red.v');
		Field 'colorVarG'     :number() :range( 0, 1 ) :widget('slider') :label('green.v');
		Field 'colorVarB'     :number() :range( 0, 1 ) :widget('slider') :label('blue.v');
		Field 'colorVarA'     :number() :range( 0, 1 ) :widget('slider') :label('alpha.v');
	}

--------------------------------------------------------------------
function SimpleParticleSystemConfig:__init()
	self.particles  = 200
	
	self.deck    = false
	self.blend   = 'add'

	self.life      = 1
	self.lifeVar   = 0
	self.emission  = 1
	self.frequency = 100
	self.emitSize  = {0,0}

	self.size    = 1
	self.size1   = 1
	self.sizeVar = 0

	self.speed        = 100
	self.speedVar     = 0
	self.angle        = 0
	self.angleVar     = 0
	
	self.rot0         = 0
	self.rot0Var      = 0
	self.rot1         = 0
	self.rot1Var      = 0

	self.accRadial    = 0
	self.accRadialVar = 0
	self.accTan       = 0
	self.accTanVar    = 0

	self.gravity      = { 0, -10 }

	self.color0 = {1,1,1,1}
	self.color1 = {1,1,1,0}

	self.colorVarR = 0
  self.colorVarG = 0
  self.colorVarB = 0
  self.colorVarA = 0

	self.deck = 'decks/particle.deck2d/pac'

end

--------------------------------------------------------------------
function SimpleParticleSystemConfig:getColor0()
	return unpack( self.color0 )
end

function SimpleParticleSystemConfig:setColor0( r,g,b,a )
	self.color0 = {r,g,b,a}
end

--------------------------------------------------------------------
function SimpleParticleSystemConfig:getColor1()
	return unpack( self.color1 )
end

function SimpleParticleSystemConfig:setColor1( r,g,b,a )
	self.color1 = {r,g,b,a}
end

--------------------------------------------------------------------
function SimpleParticleSystemConfig:getEmitSize()
	return unpack( self.emitSize )
end

function SimpleParticleSystemConfig:setEmitSize( w, h )
	self.emitSize = {w,h}
end


--------------------------------------------------------------------
function SimpleParticleSystemConfig:getGravity()
	return unpack( self.gravity )
end

function SimpleParticleSystemConfig:setGravity( x, y )
	self.gravity = { x, y }
end

--------------------------------------------------------------------
function SimpleParticleSystemConfig:buildStateScript()
	local fps = 60
	local timeScale = 1/fps
	local accScale = timeScale * timeScale

	local initScript
	local renderScript

	local t = self

	local emitterType = 'gravity'
	
	local c0  = t.color0
	local c1  = t.color1
	local c0v = { t.colorVarR, t.colorVarG, t.colorVarB, t.colorVarA }
	local c1v = { 0, 0, 0, 0 }

	local hasRadAcc   = t.accRadial~=0 or t.accRadialVar~=0
	local hasTanAcc   = t.accTan~=0 or t.accTanVar~=0

	local dataInit = {

			emitterType  = emitterType,

			speed         = t.speed * timeScale,
			speedVariance = t.speedVar * timeScale,
			angle         = t.angle / 180 * math.pi,
			angleVariance = t.angleVar / 180 * math.pi,

			r0 = c0[1],  r0v = c0v[1],
			g0 = c0[2],  g0v = c0v[2],
			b0 = c0[3],  b0v = c0v[3],
			a0 = c0[4],  a0v = c0v[4],

			r1 = c1[1],  r1v = c1v[1],
			g1 = c1[2],  g1v = c1v[2],
			b1 = c1[3],  b1v = c1v[3],
			a1 = c1[4],  a1v = c1v[4],

			startParticleSize         = t.size,
			startParticleSizeVariance = t.sizeVar,

			finishParticleSize         = t.size1,
			finishParticleSizeVariance = 0, --TODO:?

			rot0         = t.rot0,
			rot0Variance = t.rot0Var,
			rot1         = t.rot1,
			rot1Variance = t.rot1Var,

			radAcc         = t.accRadial    * accScale,
			radAccVariance = t.accRadialVar * accScale,
			tanAcc         = t.accTan       * accScale,
			tanAccVariance = t.accTanVar    * accScale,

			hasRadAcc = tostring(hasRadAcc),
			hasTanAcc = tostring(hasTanAcc),

			srcX         = 0,--t.sourcePosition.x,
			srcXVariance = t.emitSize[1],
			srcY         = 0,--t.sourcePosition.y,
			srcYVariance = t.emitSize[2],

			--RADIAL EMITTER
			--TODO
			rps         = 0 * math.pi/180 * timeScale, --TODO
			rpsVariance = 0 * math.pi/180 * timeScale, --TODO

			minRadius         = 0,
			maxRadius         = 0,
			maxRadiusVariance = 0,

		}

	-- if t.blendFuncSource == 1 then dataInit.a1 = 1 dataInit.a0 = 1 end
	local init = string.gsub(
			templateInitScript,
			"%$(%w+)",
			dataInit
		)

	local function checkColorEase( data, field )
		local r0  = data[ field..'0'  ]
		local r0v = data[ field..'0v' ]
		local r1  = data[ field..'1'  ]
		local r1v = data[ field..'1v' ]
		return tostring( not( r0==r1 and r0v==0 and r1v==0 ) )
	end

	local gx,gy = self:getGravity()

	local dataRender={
		
		emitterType = emitterType,

		gravityX = gx * accScale, --TODO
		gravityY = gy * accScale, --TODO

		hasRadAcc = tostring( hasRadAcc ),
		hasTanAcc = tostring( hasTanAcc ),

		easeR = checkColorEase( dataInit, 'r' ),
		easeG = checkColorEase( dataInit, 'g' ),
		easeB = checkColorEase( dataInit, 'b' ),
		easeA = checkColorEase( dataInit, 'a' ),

		r0 = c0[1],
		g0 = c0[2],
		b0 = c0[3],
		a0 = c0[4],

	}

	local render = string.gsub(
			templateRenderScript,
			"%$(%w+)",
			dataRender
		)

	-- print( init )
	-- print( render )

	return init, render
end

--------------------------------------------------------------------
function SimpleParticleSystemConfig:buildSystemConfig()
	local init, render = self:buildStateScript()
	
	--state
	local st = ParticleStateConfig()
	st.name = 'default'
	st.life = varianceRange( self.life, self.lifeVar, 0 )
	st.initScript = init
	st.renderScript = render

	--Emitter
	local em = ParticleEmitterConfig() 
	em.name = 'default'
	em.type = 'timed'
	em.frequency = self.frequency
	em.emission  = self.emission
	em.magnitude = varianceRange( self.speed, self.speedVar )
	em.angle     = varianceRange( self.angle, self.angleVar )

	--System
	local cfg = ParticleSystemConfig()
	cfg.particles = self.particles
	cfg.sprites   = self.particles
	cfg.deck      = self.deck

	local w, h = self:getEmitSize()
	cfg.rect      = { -w/2, -h/2, w, h }

	cfg:addStateConfig( st )
	cfg:addEmitterConfig( em )
	cfg.blend = self.blend
	
	self.systemConfig = cfg
	return cfg
end

--------------------------------------------------------------------
function SimpleParticleSystemConfig:getSystemConfig()
	if self.systemConfig then return self.systemConfig end
	return self:buildSystemConfig()
end

--------------------------------------------------------------------
local function loadSimpleParticleConfig( node )
	local defData   = loadAssetDataTable( node:getObjectFile('def') )
	local simpleSystemConfig = deserialize( nil, defData )
	node.cached.simpleConfig = simpleSystemConfig
	return simpleSystemConfig:getSystemConfig()
end

--------------------------------------------------------------------
registerAssetLoader( 'particle_simple', loadSimpleParticleConfig )
