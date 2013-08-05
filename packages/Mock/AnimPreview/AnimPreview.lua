context = false
-----
currentSprite  = false
animClipLength = false
animClipNames  = false
------
function onLoad()
	context = gii.createEditCanvasContext()
end

function onResize(w,h)
	context:resize(w,h)	
end

function showAuroraSprite( path )
	local sprite, node = mock.loadAsset( path )
	local names = {}
	for k in pairs( sprite.animations ) do
		table.insert( names, k )
	end
	
	if currentSprite then
		currentSprite:stop()
		context:removeProp(currentSprite.prop) 
		currentSprite=false
		animClipLength= false
	end

	animClipNames = names 
	currentSprite = mock.AuroraSprite()
	currentSprite:load( sprite )
	currentSprite:setFPS( 10 )
	context:insertProp( currentSprite.prop )
	currentSprite.prop:setBlendMode( 
		MOAIProp.GL_SRC_ALPHA, 
		MOAIProp.GL_ONE_MINUS_SRC_ALPHA
		) 
end

function setAnimClip( name )
	if currentSprite then
		animClipLength = currentSprite:getClipLength( name )
		currentSprite:play( name, MOAITimer.LOOP )
	end
end


function onMouseDown( btn )
	if btn=='left' then 
		currentSprite:pause( true ) --unpause
		btnDown = true
	end
end

function onMouseUp( btn )
	if btn=='left' then 
		currentSprite:pause(false)
		btnDown = false
	end
end


function onMouseMove( x, y )
	if not btnDown then return end
	if animClipLength then
		local t = x / context.viewWidth * animClipLength 
		currentSprite:apply( t )		
		_owner:updateCanvas()
	end
end
