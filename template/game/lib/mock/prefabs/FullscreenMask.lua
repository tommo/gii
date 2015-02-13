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
CLASS: FullscreenMask ( Object )

local fillRect=MOAIDraw.fillRect
local setPenColor=MOAIGfxDevice.setPenColor

function FullscreenMask:onDraw()
	if  not self.visible then return end

	local r,g,b,a=extractColor(self.color)
	if a <=0 then return end
	setPenColor(r,g,b,a)
	-- print(extractColor(self.color))

	local gfx=game.gfx
	fillRect(-gfx.w/2,-gfx.h/2,gfx.w,gfx.h)
end

function FullscreenMask:fade(r,g,b,a,time,ease)	
	return self.color:seekColor(r,g,b,a,time,ease)	
end

function FullscreenMask:set(r,g,b,a)
	return self.color:setColor(r,g,b,a)
end

function FullscreenMask:hide()
	self.visible=false
end

function FullscreenMask:show()
	self.visible=true
end


function FullscreenMask:onLoad()
	
	self.color=MOAIColor.new()
	self.color:setColor(1,1,1,1)
	self.visible=true

	self._scriptDeck:setPriority(10000)	
end




local block=MOAICoroutine.blockOnAction
function FullscreenMask:slash(r,g,b,t)
	t=t or 0.7
	if self.slashMaskThread then 
		self.slashMaskThread:stop()
	end
	local thread=MOAICoroutine.new()
	thread:run(function()
		self:show()
		self:set(r,g,b,0)
		block(self:fade(r,g,b,.8,0.01))
		block(self:fade(r,g,b,0,t,MOAIEaseType.EASE_IN))
		self:set(r,g,b,0)
		self:hide()
	end)
	self.slashMaskThread=thread
	return thread
end

return FullscreenMask