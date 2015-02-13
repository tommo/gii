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

CLASS: DebugView ( GlobalEntity )

function DebugView:onLoad()
	local w,h = game:getResolution()
	self.text = self:addTextBox{
		rect  = {-w,h,0,0},
		color = {0,1,0},
		align = 'right'
	}

	self:setLoc( game:getPos('right-top',0,0) )
	self.watches={}
end

function DebugView:addWatch(name,obj,field)
	local w={
		name=name,
		type='field',
		field=field,
		data=table.weak{
			obj=obj,
		}
	}
	table.insert(self.watches,w)
end

function DebugView:addFuncWatch(name,func,arg)
	local w={
		name=name,
		type='func',
		arg=arg,
		func=func,
	}
	table.insert(self.watches,w)
end

function DebugView:onUpdate()
	local watches=self.watches
	local result=''
	for i,w in ipairs(watches) do
		local name,v
		name=w.name

		if w.type=='field' then
			local obj=w.data.obj
			local field=w.field
			if obj then
				local v=obj[field]
			else
				table.remove(watches,i)
			end	
		else
			v=w.func(w.arg)			
		end
		result=result..string.format('%s : %s\n',name,tostring(v))
	end
	self.text:setString(result)
end

