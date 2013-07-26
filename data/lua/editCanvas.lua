module('gii')

local defaultFont = false
function getDefaultFont()
	if not defaultFont then
		defaultFont = MOAIFont.new()
		defaultFont:load( getAppPath('data/VeraBd.ttf') )
		local defaultStyle = MOAITextStyle.new()
		defaultStyle:setFont( defaultFont )
		defaultStyle:setSize( 11 )
	end
	return defaultFont
end

local function makeBackgroundProp( )
	local bgProp = MOAIProp.new()
	local bgDeck = MOAIScriptDeck.new()
	local color = {.1,.1,.1,1}
	local size  = {0,0}
	bgDeck:setRect(0,0,1,1)
	bgDeck:setDrawCallback(function()
		local w,h =size[1],size[2]
		MOAIGfxDevice.setPenColor(unpack(color))
		MOAIDraw.fillRect(-w/2,h/2,w/2,-h/2)
	end
	)
	bgProp:setDeck(bgDeck)
	bgProp:setPriority(-10000)
	bgProp._color = color
	bgProp._size  = size
	return bgProp
end


---------Common Context Helper
local EditCanvasContext = {}

function createEditCanvasContext()
	local layer = MOAILayer.new ()
	local camera=MOAICamera2D.new()
	local viewport = MOAIViewport.new ()

	MOAISim.pushRenderPass ( layer )
	layer:setViewport ( viewport )
	layer:showDebugLines( false )
	layer:setCamera(camera)

	local bgColor = {.1,.1,.1,1}
	bgProp = makeBackgroundProp( 
		bgColor, layer, camera 
		)
	layer:insertProp(bgProp)
	bgProp:setParent(camera)
	local context={
		layer      = layer,
		camera     = camera,
		cameraScl  = 1,
		viewport   = viewport,
		background = bgProp,
		viewWidth  = 0,
		viewHeight = 0,
		hudProps   = {}
	}
	context = setmetatable( context, { __index = EditCanvasContext } )
	return context
end

function EditCanvasContext:createHUDText()
	local box = MOAITextBox.new()
	box:setPriority( 10000 )
	box:setYFlip( true )
	box:setAlignment( MOAITextBox.CENTER_JUSTIFY )
	box:setStyle( defaultStyle )
	self.layer:insertProp(box)
	box:setParent(self.camera)
	self.hudProps[box] = true
	return box
end

function EditCanvasContext:getSize()
	return self.viewWidth, self.viewHeight
end

function EditCanvasContext:resize( w, h )
	self.viewport:setSize(w,h)
	self.viewport:setScale(w,h)

	self.viewWidth, self.viewHeight = w, h

	local size = self.background._size
	size[1]=w
	size[2]=h

	for hud in pairs(self.hudProps) do
		hud:setRect(-w/2 ,-h/2, w/2, h/2)
	end
end

function EditCanvasContext:setBackgroundColor(r,g,b,a)
	local bgColor = self.background._color
	bgColor[1] = r 
	bgColor[2] = g 
	bgColor[3] = b 
	bgColor[4] = a 
end

function EditCanvasContext:insertProp( p )
	return self.layer:insertProp( p )
end

function EditCanvasContext:removeProp( p )
	return self.layer:removeProp( p )
end

function EditCanvasContext:setCameraScl( scl )
	self.camera:setScl(scl,scl,1)
	self.cameraScl=scl
end
function EditCanvasContext:setCameraLoc( x, y )
	self.camera:setLoc( x, y )
end

function EditCanvasContext:wndToWorld( x, y )
	return self.layer:wndToWorld( x, y )
end

function EditCanvasContext:worldToWnd( x, y, z )
	return self.layer:worldToWnd( x, y, z )
end


function EditCanvasContext:fitViewport( w,h )
	local scl=1
	local vw,vh = self.viewWidth, self.viewHeight
	if w * h<=0 then return end
	if vw*vh<=0 then return end
	scl = math.max(h/vh, w/vw)
	self:setCameraScl(scl)
end

function EditCanvasContext:addDrawScript(func, option )
	option = option or {}
	priority= option.priority or 1000
	w = option.w or 10000
	h = option.h or 10000
	local prop = MOAIProp.new()
	local deck = MOAIScriptDeck.new()
	deck:setDrawCallback( func )	
	deck:setRect(-w/2,-h/2,w/2,h/2)
	prop:setDeck(deck)
	prop:setPriority(priority)
	prop:setBlendMode( MOAIProp.GL_SRC_ALPHA,MOAIProp.GL_ONE_MINUS_SRC_ALPHA ) 
	self:insertProp(prop)
	return prop,deck
end


