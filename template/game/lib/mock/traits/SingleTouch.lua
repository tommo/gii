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

local SingleTouch=newTrait('SingleTouch')

SingleTouch.__overwrite={'onTouch'}

function SingleTouch:onTouch(ev,id,x,y)
	if ev=='press' and not self._touchId then
		if self:testPress(x,y) then
			self._touchId=id
			return self:onPress(x,y)
		end

	elseif ev=='release' and self._touchId==id then
		self._touchId=nil
		return self:onRelease(x,y)

	elseif ev=='drag' and self._touchId==id then
		return self:onDrag(x,y)
	end
end

function SingleTouch:flushTouch()
	self._touchId=nil
end

function SingleTouch:onPress(x,y)
end

function SingleTouch:onDrag(x,y)
end

function SingleTouch:onRelease(x,y)
end

function SingleTouch:testPress(x,y)
	return true
end