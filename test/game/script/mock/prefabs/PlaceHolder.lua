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

CLASS: PlaceHolder ( Entity )
local draw = MOAIDraw
local gfx  = MOAIGfxDevice

local function _onDrawRect(self)	
	gfx.setPenColor(unpack(self.color))
	draw.drawRect(self.x0,self.y0,self.x1,self.y1)
end

local function _onDrawFilledRect(self)
	gfx.setPenColor(unpack(self.color))
	draw.fillRect(self.x0,self.y0,self.x1,self.y1)
end

local function _onDrawCircle(self)
	gfx.setPenColor(unpack(self.color))
	draw.drawCircle(self.cx,self.cy,self.radius,16)
end

local function _onDrawFilledCircle(self)
	gfx.setPenColor(unpack(self.color))
	draw.fillCircle(self.cx,self.cy,self.radius,16)
end


function PlaceHolder:__init(data)
	self.color=data and data.color or {1,1,1,1}
	local type,filled='rect',false
	if data then
		type,filled=data.type,data.filled
	end

	if type=='rect' then		
		self.onDraw=filled and _onDrawFilledRect or _onDrawRect
		local w,h=10,10
		if data and data.size then
			w,h=unpack(data.size)
		end

		self.x0=-w/2
		self.y0=-h/2
		self.x1=w/2
		self.y1=h/2

	elseif type=='circle' then
		self.onDraw=filled and _onDrawFilledCircle or _onDrawCircle 
		self.cx=0
		self.cy=0
		local r=data and data.radius or 10
		self.radius=r

		self.x0=-r
		self.y0=-r
		self.x1=r
		self.y1=r
	end

	if data and data.noRect then self.onGetRect=false end

end

function PlaceHolder:onLoad()
	self:attach( DrawScript() )
end

function PlaceHolder:onGetRect()
	return self.x0,self.y0,self.x1,self.y1
end

function PlaceHolder:getWorldBounds()
	return self._scriptDeck:getWorldBounds()
end
