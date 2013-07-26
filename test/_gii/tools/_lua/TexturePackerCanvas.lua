--standalone render context
-- gii.doRuntimeScript('TexpackLoader.lua')
multiSelecting=false
vw,vh=0,0
tw,th=1,1
camScl=1

function onLoad()
	context = gii.createEditCanvasContext() 

	prop=MOAIProp.new()

	deck = MOAIGfxQuad2D.new ()
	deck:setRect ( -64, -64, 64, 64 )

	prop:setDeck(deck)
	prop:setBlendMode( MOAIProp.GL_SRC_ALPHA,MOAIProp.GL_ONE_MINUS_SRC_ALPHA ) 

	propItem=MOAIProp.new()

	context:insertProp(propItem)
	context:insertProp(prop)
	context:addDrawScript(drawBounds)
end

function onResize(w,h)
	context:resize(w,h)
	fitViewport()
end

function fitViewport()
	context:fitViewport(tw,th)	
end

local bounds=false
function clearAtlasBound()
	activeItem=false
	bounds=false
	-- for i, prop in ipairs(bounds) do
	-- 	context.layer.removeProp(prop)
	-- end
	-- bounds={}
end

function showAtlasBound(textures)
	bounds={}	
	for k, item in pairs(textures) do
		bounds[k]=item.rect
	end
end

function drawBounds()
	if not bounds then return end
	MOAIGfxDevice.setPenColor(0,1,1,0.3)
	MOAIGfxDevice.setPenWidth(1)
	for k, rect in pairs(bounds) do
		local x,y,w,h=unpack(rect)
		local x0,y0,x1,y1=x,y,x+w,y+h
		x0,y0,x1,y1=x0-tw/2,y0-th/2,x1-tw/2,y1-th/2
		MOAIDraw.drawRect(x0,-y0,x1,-y1)
	end
	if not activeItem then return end 
	MOAIGfxDevice.setPenColor(1,0,0,1)
	for k, item in pairs(activeItem) do
		local rect=item.rect
		local x,y,w,h=unpack(rect)
		local x0,y0,x1,y1=x,y,x+w,y+h
		x0,y0,x1,y1=x0-tw/2,y0-th/2,x1-tw/2,y1-th/2
		MOAIDraw.drawRect(x0,-y0,x1,-y1)
	end
end

function showTextureQuad(tex, w,h, uv)
	deck:setTexture(tex)
	deck:setRect(-w/2,-h/2,w/2,h/2)
	tw,th=w,h
	if uv then
		deck:setUVRect(unpack(uv))
	else
		deck:setUVRect(0,1,1,0)
	end
	prop:forceUpdate()
	fitViewport()
	_owner:updateCanvas()
end


function showAtlas(atlasPath, itemName)
	clearAtlasBound()
	editingPack=mock.loadAsset(atlasPath)
	local atlasTex=editingPack and editingPack.atlases[1]
	if atlasTex then
		showAtlasBound(editingPack.textures)
		showTextureQuad(atlasTex, atlasTex:getSize())
		return true
	end
	return false
end

function findSubTexture(x,y)
	if not editingPack  then return end
	for k, item in pairs(editingPack.textures) do
		local x1,y1,w,h=unpack(item.rect)
		local dx,dy=x-x1,y-y1
		if dx>0 and dx<w and dy>0 and dy<h then
			return item
		end
	end
	return false
end

function openAsset(path)
	showAtlas(path)	
end

function findSubTextureBySource(src)
	for k, item in pairs(editingPack.textures) do
		if item.source==src then return item end
	end
end

function setSelectedItem( selection )
	activeItem={}
	for src in python.iter(selection) do
		src  = gii.fromUnicode(src)
		item = findSubTextureBySource(src)
		if item then activeItem[src] = item end
	end
	_owner:updateCanvas()
end

function onKeyDown(key)
	if key=='shift' then
		multiSelecting=true
	end
end

function onKeyUp(key)
	if key=='shift' then
		multiSelecting=false
	end
end


function onMouseDown(btn, x,y)
	x,y=context.layer:wndToWorld(x,y)
	local x,y= x+tw/2, -y+th/2
	local item = findSubTexture(x,y)
	if item then
		selectSubTexture(item.source, multiSelecting)
	end
end

function onMouseUp()
end