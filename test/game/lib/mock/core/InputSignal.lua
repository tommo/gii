--[[
* MOCK framework for Moai

* Copyright (C) 2012 Tommo Zhou(tommo.zhou@gmail.com).  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
]]

module 'mock'

local signalEnabled={
	['mouse.move']=false,
	['mouse.down']=false,
	['mouse.up']=false,

	['touch.down']=false,
	['touch.up']=false,
	['touch.move']=false,

	['key.down']=false,
	['key.up']=false,

}


for key in pairs(signalEnabled) do
	registerSignal(key)
end

local keyListener
local touchListener
local mouseListener

local emit=emitSignal
local function tryEmit(sig,...)
	if signalEnabled[sig] then return emit(sig,...) end
end



function enableInputSignal(t) 
	--signal process affects performance, disabled by default
	if signalEnabled[t]==nil then	return error('no signal found:'..t) end
	if signalEnabled[t] then return end

	signalEnabled[t]=true

	local h=t:sub(1,3)
	if h=='mou' then --mouse
		if not mouseListener then
			mouseListener=function(ev,x,y,z,btn,fake)
				if ev=='move' then
					return tryEmit('mouse.move',x,y,z,btn,fake)
				elseif ev=='down' then
					return tryEmit('mouse.down',x,y,z,btn,fake)
				elseif ev=='up' then
					return tryEmit('mouse.up',x,y,z,btn,fake)
				end
			end
			addMouseListener(mouseListener,mouseListener)
		end

	elseif h=='tou' then --tou

		if not touchListener then

			touchListener=function(ev,id,x,y,fake)
				if ev=='move' then
					return tryEmit('touch.move',id,x,y,fake)
				elseif ev=='down' then
					return tryEmit('touch.down',id,x,y,fake)
				elseif ev=='up' then
					return tryEmit('touch.up',id,x,y,fake)
				end
			end

			addTouchListener(touchListener,touchListener)
		end


	elseif h=='key' then --key
		if not keyListener then
			keyListener=function(key,down,fake)
				if down then 
					return tryEmit('key.down',key,fake)
				else
					return tryEmit('key.up',key,fake)
				end
			end
			addKeyListener(keyListener,keyListener)
		end


	elseif h=='mot' then --motion
	end

end


function enableInputSignals(t)
	for i,k in ipairs(t) do
		enableInputSignal(k)
	end
end