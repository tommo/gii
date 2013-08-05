function OnTestStart( logic )
	local camera = logic:addSibling( Entity() )
	camera:attach( mock.Camera{
				ortho = true,
				farPlane = 10000,
				nearPlane = -100
			} ) 

	local gen = MOAISimplexNoiseGenerator.new()
	print "-- seed noise --"
	local seed = 1234
	print ( 'seed = ', seed )
	gen:seedNoise( seed )

	print "-- 1d noise --"
	print( gen:genNoise1D (10.1) )

	print "-- 2d noise --"
	print( gen:genNoise2D (1.0, 2.0) )

	print "-- 3d noise --"
	print( gen:genNoise3D (10.1, 0.2, 0.5) )

	local tex = MOAIImageTexture.new()
	local w ,h = 32, 32
	tex:init( w, h )
	local scl = 0.5
	
	for y = 1, h do
		for x = 1, w do
			local v = gen:genNoise2D( x * scl, y * scl )
			v = ( v + 1 ) / 2
			tex:setRGBA( x, y, v, v, v, 1 )
		end
	end

	tex:invalidate( 0, 0, w, h )
	local deck = MOAIGfxQuad2D.new()
	deck:setTexture( tex )
	deck:setRect( -64, -64, 64, 64 )

	local entity = logic:addSibling( Entity() )
	entity:attach( mock.Prop{
			deck = deck
		})

end