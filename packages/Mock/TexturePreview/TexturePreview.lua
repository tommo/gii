--standalone render context
texWidth, texHeight = 1, 1

hud = false
context = false

function onLoad()
	context  = gii.createEditCanvasContext() 
	prop     = MOAIProp.new()
	quadDeck = MOAIGfxQuad2D.new ()
	quadDeck:setRect ( -64, -64, 64, 64 )

	prop:setDeck(quadDeck)
	prop:setBlendMode( MOAIProp.GL_SRC_ALPHA,MOAIProp.GL_ONE_MINUS_SRC_ALPHA ) 

	context:insertProp(prop)
	context:addDrawScript(drawBounds)
	hud = context:createHUDText()
end

function onResize(w,h)
	context:resize(w,h)
	fitViewport()
	context:fitViewport(texWidth,texHeight)
end

function fitViewport()
	context:fitViewport( texWidth, texHeight )
	fitScale = context.cameraScl
end

function actualPixelViewport()
	context:setCameraScl(1, 1, 1)
	fitScale = 1
end

local bounds=false
function clearAtlasBound()
	bounds=false
	-- for i, prop in ipairs(bounds) do
	-- 	layer.removeProp(prop)
	-- end
	-- bounds={}
end

function showAtlasBound(textures)
	bounds={}	
	for k, item in pairs(textures) do
		bounds[k]=item.rect
	end
end

function showQuadLists( path )
	local quadListDeck = mock.loadAsset( path )	
	prop:setDeck(quadListDeck)
	prop:setIndex(1)
	prop:forceUpdate()
	local w,h = prop:getDims()
	if w then
		texWidth, texHeight = w,h
	end
	fitViewport()
	_owner:updateCanvas()
end

function drawBounds()
	if not bounds then return end
	MOAIGfxDevice.setPenColor(0,1,0,0.5)
	for k, rect in pairs(bounds) do
		local x, y, w, h = unpack(rect)
		local x0, y0, x1, y1 = x, y, x+w, y+h
		x0, y0, x1, y1 = x0-texWidth/2, y0-texHeight/2, x1-texWidth/2, y1-texHeight/2
		MOAIDraw.drawRect(x0,-y0,x1,-y1)
	end
end

function showTextureQuad( tex, w,h, uv )
	quadDeck:setTexture(tex)
	quadDeck:setRect( -w/2, -h/2, w/2, h/2 )
	texWidth,texHeight = w, h
	hud:setString( string.format(' %d * %d ',w,h) )

	if uv then
		quadDeck:setUVRect(unpack(uv))
	else
		quadDeck:setUVRect(0,1,1,0)
	end
	
	prop:setDeck(quadDeck)	
	prop:forceUpdate()

	fitViewport()
	_owner:updateCanvas()
end

function showTexture(path)
	clearAtlasBound()
	tex = mock.loadAsset(path)
	if not tex then return false end 
	if tex.type == 'sub_texture' then
		showTextureQuad( tex.atlas, tex.w, tex.h, tex.uv)
	else
		showTextureQuad( tex, tex:getSize() )
	end
	return true
end

function showSubTexture(atlasPath, itemName)
	clearAtlasBound()
	local pack=mock.loadAsset(atlasPath)
	local item=pack and pack.textures[itemName]
	if item then
		showTextureQuad(item.atlas, item.w, item.h, item.uv)
		return true
	end
	return false
end

function showAtlas(atlasPath, itemName)
	local pack=mock.loadAsset(atlasPath)
	local atlasTex=pack and pack.atlases[1]
	if atlasTex then
		showAtlasBound(pack.textures)
		showTextureQuad(atlasTex, atlasTex:getSize())
		return true
	end
	return false
end

dragging=false
function onMouseDown(btn, x,y)
	if btn~='left' then return end
	local vw, vh = context:getSize()
	x =   x-vw/2
	y = -(y-vh/2)
	dragging=true

	context:setCameraScl(1)
	context:setCameraLoc(x*fitScale,y*fitScale)

	_owner:updateCanvas()
end

function onMouseUp(btn,x,y)
	if btn~='left' then return end
	dragging=false

	context:setCameraLoc(0 ,0)
	fitViewport()
	_owner:updateCanvas()
end

function onMouseMove(x,y)
	if not dragging then return end
	local vw, vh = context:getSize()
	x =   x-vw/2
	y = -(y-vh/2)

	context:setCameraLoc(x*fitScale,y*fitScale)
	_owner:updateCanvas()
end

