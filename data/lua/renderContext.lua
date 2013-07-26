module('gii')


local renderContextTable={}
--[[
RenderContext incluces:
	1. an action root
	2. a render table
shares:
	layer information
	prop
	assets
]]

local currentContext=false

function createRenderContext(key)
	local context={
		key=key,
		w=false,
		h=false,
		clearColor={0,0,0,0}
	}
	renderContextTable[key]=context
	local root=MOAICoroutine.new()
	root:run(function() local dt=coroutine.yield() end)
	context.actionRoot=root
end


function changeRenderContext(key, w, h)	
	local context=renderContextTable[key]
	assert (context, 'no render context for:'..tostring(key))

	if currentContext==context then return end	
	
	if currentContext then --persist context
		currentContext.actionRoot=MOAIActionMgr.getRoot()
		local fb=MOAIGfxDevice.getFrameBuffer()
		currentContext.renderTable=fb:getRenderTable()
		currentContext.bufferTable=MOAIRenderMgr.getBufferTable()
		-- local res = gii.bridge.GLHelper.getClearColor()
		-- currentContext.clearColor=gii.listToTable(res)
	end

	--TODO: persist clear depth& color flag(need to modify moai)
	
	currentContext=context
	MOAIGfxDevice.getFrameBuffer():setRenderTable(currentContext.renderTable)
	-- local r,g,b,a=unpack(currentContext.clearColor)
	-- MOAIGfxDevice.getFrameBuffer():setClearColor(r,g,b,a)
	MOAIRenderMgr.setBufferTable(currentContext.bufferTable)	
	MOAIActionMgr.setRoot(currentContext.actionRoot)
end


-- function setCurrentRenderContextSize(w,h)
-- 	local context=currentContext
-- 	if context then
-- 		context.w=w
-- 		context.h=h
-- 	end
-- end

function getCurrentContext()
	return currentContext
end


local keymap_GII={
	["alt"] = 163 ;
	["pause"] = 168 ;
	["menu"] = 245 ;
	[","] = 44 ;
	["0"] = 48 ;
	["4"] = 52 ;
	["8"] = 56 ;
	["sysreq"] = 170 ;
	["@"] = 64 ;
	["return"] = 164 ;
	["7"] = 55 ;
	["\\"] = 92 ;
	["insert"] = 166 ;
	["d"] = 68 ;
	["h"] = 72 ;
	["l"] = 76 ;
	["p"] = 80 ;
	["t"] = 84 ;
	["x"] = 88 ;
	["right"] = 180 ;
	["meta"] = 162 ;
	["escape"] = 160 ;
	["home"] = 176 ;
	["'"] = 96 ;
	["space"] = 32 ;
	["3"] = 51 ;
	["backspace"] = 163 ;
	["pagedown"] = 183 ;
	["slash"] = 47 ;
	[";"] = 59 ;
	["scrolllock"] = 166 ;
	["["] = 91 ;
	["c"] = 67 ;
	["z"] = 90 ;
	["g"] = 71 ;
	["shift"] = 160 ;
	["k"] = 75 ;
	["o"] = 79 ;
	["s"] = 83 ;
	["w"] = 87 ;
	["delete"] = 167 ;
	["down"] = 181 ;
	["."] = 46 ;
	["2"] = 50 ;
	["6"] = 54 ;
	[":"] = 58 ;
	["b"] = 66 ;
	["f"] = 70 ;
	["j"] = 74 ;
	["pageup"] = 182 ;
	["up"] = 179 ;
	["n"] = 78 ;
	["r"] = 82 ;
	["v"] = 86 ;
	["f12"] = 187 ;
	["f13"] = 188 ;
	["f10"] = 185 ;
	["f11"] = 186 ;
	["f14"] = 189 ;
	["f15"] = 190 ;
	["control"] = 161 ;
	["f1"] = 176 ;
	["f2"] = 177 ;
	["f3"] = 178 ;
	["f4"] = 179 ;
	["f5"] = 180 ;
	["f6"] = 181 ;
	["f7"] = 182 ;
	["f8"] = 183 ;
	["f9"] = 184 ;
	["tab"] = 161 ;
	["numlock"] = 165 ;
	["end"] = 177 ;
	["-"] = 45 ;
	["1"] = 49 ;
	["5"] = 53 ;
	["9"] = 57 ;
	["="] = 61 ;
	["]"] = 93 ;
	["a"] = 65 ;
	["e"] = 69 ;
	["i"] = 73 ;
	["m"] = 77 ;
	["q"] = 81 ;
	["u"] = 85 ;
	["y"] = 89 ;
	["left"] = 178 ;
	["shift"] = 256 ;
	["control"] = 257 ;
	["alt"] = 258 ;

}

local keyname={}
for k,v in pairs(keymap_GII) do
	keyname[v]=k
end

function getKeyName(code)
	return keyname[code]
end
