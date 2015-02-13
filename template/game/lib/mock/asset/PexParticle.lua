module 'mock'

local function varianceRange( v, variance )
	return { v-variance, v+variance }
end

local GL2ZGL = {
	[ 0 ]      = MOAIProp.GL_ZERO;
	[ 1 ]      = MOAIProp.GL_ONE;
	[ 0x0300 ] = MOAIProp.GL_SRC_COLOR;
	[ 0x0301 ] = MOAIProp.GL_ONE_MINUS_SRC_COLOR;
	[ 0x0302 ] = MOAIProp.GL_SRC_ALPHA;
	[ 0x0303 ] = MOAIProp.GL_ONE_MINUS_SRC_ALPHA;
	[ 0x0304 ] = MOAIProp.GL_DST_ALPHA;
	[ 0x0305 ] = MOAIProp.GL_ONE_MINUS_DST_ALPHA;
	[ 0x0306 ] = MOAIProp.GL_DST_COLOR;
	[ 0x0307 ] = MOAIProp.GL_ONE_MINUS_DST_COLOR;
	[ 0x0308 ] = MOAIProp.GL_SRC_ALPHA_SATURATE;
}

local function pexNodeToLua(xml)
	local result = {}
	for k,v in pairs(xml.children) do
		v = v[1]
		if type(v) == 'table' and v.attributes then
			local node  = {}
			local count = 0
			if k == 'texture' then
				node['name'] = v.attributes['name']
				node['data'] = v.attributes['data'] or false
				count = 2
			else
				for k,v in pairs(v.attributes) do
					local n = tonumber(v)
					node[k] = n or v
					count = count + 1
				end
			end
			if count == 1 and node.value then
				result[k] = node.value
			else
				result[k] = node
			end
		end
	end
	return result
end

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

local fps = 60
function pexToParticleScript( file ) --convert pex to 2 particle script
	local timeScale = 1/fps
	local accScale = timeScale * timeScale

	local xml = MOAIXmlParser.parseFile ( file )

	assert( xml and xml.type=='particleEmitterConfig' )

	local pexData = pexNodeToLua( xml )

	local initScript
	local renderScript

	local t = pexData

	local emitterType = t.emitterType==0 and 'gravity' or 'radial'
	
	local c0  = t.startColor
	local c1  = t.finishColor
	local c0v = t.startColorVariance
	local c1v = t.finishColorVariance

	local hasRadAcc   = t.radialAcceleration~=0 or t.radialAccelVariance~=0
	local hasTanAcc   = t.tangentialAcceleration~=0 or t.tangentialAccelVariance~=0

	local dataInit = {

			emitterType  = emitterType,

			speed         = t.speed * timeScale,
			speedVariance = t.speedVariance * timeScale,
			angle         = t.angle / 180 * math.pi,
			angleVariance = t.angleVariance / 180 * math.pi,

			r0 = c0.red,   r0v = c0v.red,
			g0 = c0.green, g0v = c0v.green,
			b0 = c0.blue,  b0v = c0v.blue,
			a0 = c0.alpha, a0v = c0v.alpha,

			r1 = c1.red,   r1v = c1v.red,
			g1 = c1.green, g1v = c1v.green,
			b1 = c1.blue,  b1v = c1v.blue,
			a1 = c1.alpha, a1v = c1v.alpha,

			startParticleSize         = t.startParticleSize,
			startParticleSizeVariance = t.startParticleSizeVariance,

			finishParticleSize         = t.finishParticleSize,
			finishParticleSizeVariance = t.FinishParticleSizeVariance,

			rot0         = t.rotationStart,
			rot0Variance = t.rotationStartVariance,
			rot1         = t.rotationEnd,
			rot1Variance = t.rotationEndVariance,

			radAcc         = t.radialAcceleration*accScale,
			radAccVariance = t.radialAccelVariance*accScale,
			tanAcc         = t.tangentialAcceleration*accScale,
			tanAccVariance = t.tangentialAccelVariance*accScale,

			hasRadAcc = tostring(hasRadAcc),
			hasTanAcc = tostring(hasTanAcc),

			srcX         = 0,--t.sourcePosition.x,
			srcXVariance = t.sourcePositionVariance.x,
			srcY         = 0,--t.sourcePosition.y,
			srcYVariance = t.sourcePositionVariance.y,

			rps         = t.rotatePerSecond * math.pi/180 * timeScale,
			rpsVariance = t.rotatePerSecondVariance * math.pi/180 * timeScale,

			minRadius         = t.minRadius,
			maxRadius         = t.maxRadius,
			maxRadiusVariance = t.maxRadiusVariance

		}

	if t.blendFuncSource == 1 then dataInit.a1 = 1 dataInit.a0 = 1 end
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

	local dataRender={
		
		emitterType = emitterType,

		gravityX = t.gravity.x * accScale,
		gravityY = t.gravity.y * accScale,

		hasRadAcc = tostring( hasRadAcc ),
		hasTanAcc = tostring( hasTanAcc ),

		easeR = checkColorEase( dataInit, 'r' ),
		easeG = checkColorEase( dataInit, 'g' ),
		easeB = checkColorEase( dataInit, 'b' ),
		easeA = checkColorEase( dataInit, 'a' ),

		r0 = c0.red,
		g0 = c0.green,
		b0 = c0.blue,
		a0 = c0.alpha,

	}

	local render = string.gsub(
			templateRenderScript,
			"%$(%w+)",
			dataRender
		)
	return init, render, pexData

end


local function loadPexParticleConfig( node )
	local configPath = node:getAbsObjectFile( 'def' )

	--data
	local init, render, pexData = pexToParticleScript( configPath )

	local minLife,maxLife=
			math.max( 0, pexData.particleLifeSpan - pexData.particleLifespanVariance ),
			pexData.particleLifeSpan + pexData.particleLifespanVariance

	local emission =
		pexData.maxParticles
		/ ( math.max( 0.1, pexData.particleLifeSpan + pexData.particleLifespanVariance ) )
		/ 60 /2
	if emission < 1 then emission = 1 end

	--state
	local st = ParticleStateConfig()
	st.name = 'default'
	st.life = maxLife
	st.initScript = init
	st.renderScript = render

	--Emitter
	local em = ParticleEmitterConfig() 
	em.name = 'default'
	em.type = 'timed'
	em.frequency = 60 --FIXME
	em.magnitude = varianceRange( pexData.speed, pexData.speedVariance )
	em.emission  = emission
	em.angle     = varianceRange( pexData.angle, pexData.angleVariance )

	--System
	local cfg = ParticleSystemConfig()
	cfg.particles = pexData.maxParticles
	cfg.sprites   = pexData.maxParticles
	-- cfg.deck      = 'decks/yaka.deck2d/slot'
	cfg:addStateConfig( st )
	cfg:addEmitterConfig( em )
	cfg.blend = { 
			GL2ZGL[ pexData.blendFuncSource ] or 0, 
			GL2ZGL[ pexData.blendFuncDestination ] or 0
		}

	--Texture
	--TODO
	local texName = pexData['texture']['name']
	local texData = pexData['texture']['data']
	local deck = MOAIGfxQuad2D.new ()
	deck:setRect ( -.5, -.5, .5, .5 )

	if texData then
	else
		local tex = loadAsset( node:getSiblingPath( texName ) )
		if tex then
			if tex.type == 'sub_texture' then
				deck:setTexture( tex.atlas )
				deck:setUVRect( unpack( tex.uv ) )
			else
				deck:setTexture( tex )
				deck:setUVRect( 0, 1, 1, 0 )
			end
		end
	end
	cfg.deck = deck
	return cfg
end

registerAssetLoader( 'particle_pex', loadPexParticleConfig )
