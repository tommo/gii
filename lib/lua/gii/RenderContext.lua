module( 'gii' )


local renderContextTable = {}
--[[
	RenderContext incluces:
		1. an action root
		2. a render table
	shares:
		layer information
		prop
		assets
]]

local currentContext    = false
local currentContextKey = false

local ContextChangeListeners = {}

function createRenderContext( key )
	local root = MOAICoroutine.new()
	local context = {
		key              = key,
		w                = false,
		h                = false,
		clearColor       = { 0,0,0,0 },
		actionRoot       = root,
		bufferTable      = {},
		renderTableMap   = {},
	}
	renderContextTable[ key ] = context
	root:run( function() local dt = coroutine.yield() end )
end


function addContextChangeListeners( f )
	ContextChangeListeners[ f ] = true
end

function removeContextChangeListener( f )
	ContextChangeListeners[ f ] = nil
end

function changeRenderContext( key, w, h )
	if currentContextKey == key then return end
	local context = renderContextTable[key]
	assert ( context, 'no render context for:'..tostring(key) )
	for f in pairs( ContextChangeListeners ) do
		f( key, currentContextKey )
	end

	local deviceBuffer = MOAIGfxDevice.getFrameBuffer()

	if currentContext then --persist context
		local bufferTable  = MOAIRenderMgr.getBufferTable()
		local renderTableMap = {}
		for i, fb in pairs( bufferTable ) do
			if fb ~= deviceBuffer then
				renderTableMap[i] = { fb, fb:getRenderTable() } 
			end
		end
		currentContext.bufferTable       = bufferTable
		currentContext.renderTableMap    = renderTableMap
		currentContext.deviceRenderTable = deviceBuffer:getRenderTable()
		currentContext.actionRoot        = MOAIActionMgr.getRoot()		
		-- local res = gii.bridge.GLHelper.getClearColor()
		-- currentContext.clearColor=gii.listToTable(res)
	end

	--TODO: persist clear depth& color flag(need to modify moai)
	
	currentContext    = context
	currentContextKey = key
	currentContext.w  = w
	currentContext.h  = h

	-- local r,g,b,a=unpack(currentContext.clearColor)
	-- MOAIGfxDevice.getFrameBuffer():setClearColor(r,g,b,a)
	for i, p in ipairs( currentContext.renderTableMap ) do
		local fb = p[1]
		local rt = p[2]
		fb:setRenderTable( rt )
	end
	MOAIRenderMgr.setBufferTable ( currentContext.bufferTable )	
	deviceBuffer:setRenderTable  ( currentContext.deviceRenderTable )
	MOAIActionMgr.setRoot        ( currentContext.actionRoot )
end


function getCurrentRenderContextKey()
	return currentContextKey
end

function getCurrentRenderContext()
	return currentContext
end

function getRenderContext( key )
	return renderContextTable[ key ]
end

function setCurrentRenderContextActionRoot( root )
	currentContext.actionRoot = root
	MOAIActionMgr.setRoot( root )
end

function setRenderContextActionRoot( key, root )
	local context =  getRenderContext( key )
	if key == currentContextKey then
		MOAIActionMgr.setRoot( root )
	end
	if context then
		context.actionRoot = root
	end
end

local keymap_GII={
	["alt"]        = 163 ;
	["pause"]      = 168 ;
	["menu"]       = 245 ;
	[","]          = 44 ;
	["0"]          = 48 ;
	["4"]          = 52 ;
	["8"]          = 56 ;
	["sysreq"]     = 170 ;
	["@"]          = 64 ;
	["return"]     = 164 ;
	["7"]          = 55 ;
	["\\"]         = 92 ;
	["insert"]     = 166 ;
	["d"]          = 68 ;
	["h"]          = 72 ;
	["l"]          = 76 ;
	["p"]          = 80 ;
	["t"]          = 84 ;
	["x"]          = 88 ;
	["right"]      = 180 ;
	["meta"]       = 162 ;
	["escape"]     = 160 ;
	["home"]       = 176 ;
	["'"]          = 96 ;
	["space"]      = 32 ;
	["3"]          = 51 ;
	["backspace"]  = 163 ;
	["pagedown"]   = 183 ;
	["slash"]      = 47 ;
	[";"]          = 59 ;
	["scrolllock"] = 166 ;
	["["]          = 91 ;
	["c"]          = 67 ;
	["z"]          = 90 ;
	["g"]          = 71 ;
	["shift"]      = 160 ;
	["k"]          = 75 ;
	["o"]          = 79 ;
	["s"]          = 83 ;
	["w"]          = 87 ;
	["delete"]     = 167 ;
	["down"]       = 181 ;
	["."]          = 46 ;
	["2"]          = 50 ;
	["6"]          = 54 ;
	[":"]          = 58 ;
	["b"]          = 66 ;
	["f"]          = 70 ;
	["j"]          = 74 ;
	["pageup"]     = 182 ;
	["up"]         = 179 ;
	["n"]          = 78 ;
	["r"]          = 82 ;
	["v"]          = 86 ;
	["f12"]        = 187 ;
	["f13"]        = 188 ;
	["f10"]        = 185 ;
	["f11"]        = 186 ;
	["f14"]        = 189 ;
	["f15"]        = 190 ;
	["control"]    = 161 ;
	["f1"]         = 176 ;
	["f2"]         = 177 ;
	["f3"]         = 178 ;
	["f4"]         = 179 ;
	["f5"]         = 180 ;
	["f6"]         = 181 ;
	["f7"]         = 182 ;
	["f8"]         = 183 ;
	["f9"]         = 184 ;
	["tab"]        = 161 ;
	["numlock"]    = 165 ;
	["end"]        = 177 ;
	["-"]          = 45 ;
	["1"]          = 49 ;
	["5"]          = 53 ;
	["9"]          = 57 ;
	["="]          = 61 ;
	["]"]          = 93 ;
	["a"]          = 65 ;
	["e"]          = 69 ;
	["i"]          = 73 ;
	["m"]          = 77 ;
	["q"]          = 81 ;
	["u"]          = 85 ;
	["y"]          = 89 ;
	["left"]       = 178 ;
	["shift"]      = 256 ;
	["control"]    = 257 ;
	["alt"]        = 258 ;

}

local keyname = {}
for k,v in pairs(keymap_GII) do
	keyname[v] = k
end

function getKeyName(code)
	return keyname[code]
end
