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

CLASS: FakeInput ( Entity )
-- function FakeInput:threadDrag(x0,y0,x1,y1,time)

-- end
local fakeId=0
function FakeInput:onLoad()
	fakeId=fakeId+1
	self.inputId='fake'..fakeId	
	self.state='up'
	self.px,self.py=0,0
end

function FakeInput:down()
	if self.state=='up' then
		_sendTouchEvent('down',self.inputId,self.x,self.y)
		self:setState'down'
	end
end

function FakeInput:up()
	if self.state=='down' then
		_sendTouchEvent('up',self.inputId,self.x,self.y)
		self:setState'up'
	end
end

function FakeInput:updateInputPos()
	local x,y=self:getLoc()
	self.px=self.x
	self.py=self.y

	self.x,self.y=self:worldToWnd(x,y,0)
	local moved=false
	if self.px~=self.x or self.py~=self.y then 
		moved=true
	end

	return moved
end

function FakeInput:onUpdate()
	local moved=self:updateInputPos()
	if moved and self:inState'down' then
		_sendTouchEvent('move',self.inputId,self.x,self.y)
	end
end

function FakeInput:drag(...)
	if self.dragThread then 
		error'drag unfinished'
	end

	self.dragThread=self:addCoroutine('threadDrag',...)
	return self.dragThread
end

function FakeInput:threadDrag(x0,y0,x1,y1,time,easeType,poseOnly)

	if self.state=='up' then
		self:setLoc(x0,y0)
		self:updateInputPos()
		-- self:wait(0.1)
		if not poseOnly then self:down() end

		self:wait(self:seekLoc(x1,y1,0,time or .2,easeType))

		if not poseOnly then self:up() end
		
		self.dragThread=false
	end
end

return FakeInput