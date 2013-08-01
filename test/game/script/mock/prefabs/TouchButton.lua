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


local activeButton=false

CLASS: TouchButton ( Entity )



function TouchButton:setActive(t)
	if self.state=='down' then
		self:_release()
	end
	-- if not t then self.state='up' end
	return Object.setActive(self,t)
end

function TouchButton:__init(data)
	self.data=data
	if data.sound~=false then
		self.sound=data.sound or 'button.click'
	else
		self.sound=false
	end
	self.onClick=data.onClick
	self.pressTransform=data.pressTransform
	self.clickNeedNoRelease=data.clickNeedNoRelease
end

function TouchButton:onLoad()
	local data=self.data
	if data.deck then
		self.prop=self:addProp{
			deck=data.deck,
			transform=data.deckTransform,
			priority=data.priority or 10
		}
	end
	if data.deckPress then 
		self.propPress=self:addProp{
			deck=data.deckPress,
			transform=data.deckTransform,
			visible=false,
			priority=data.priority or 10
		}
		self.propPress:setVisible(false)
	end
	if data.rect then
		self.rect=data.rect
	end

	if data.label then
		self.textLabel=self:addTextBox{
			text=data.label,
			transform=data.labelTransform,
			priority=data.priority or 10,
			autofit=true,
			style=data.labelStyle or res.styles['default'],
			align=data.labelAlign or 'center'
		}
	end

	self.isToggle=data.isToggle or false
	self.toggle=data.toggle or false
	self:setDeckState(self.toggle)
end

function TouchButton:onPress()
	local t=self.pressTransform
	if t then
		if t.scl then
			self:addScl(unpack(t.scl))
		end
	end
end

function TouchButton:onRelease()
	local t=self.pressTransform
	if t then
		if t.scl then
			local x,y,z=unpack(t.scl)
			x=x and -x or 0
			y=y and -y or 0
			z=z and -z or 0
			self:addScl(x,y,z)
		end
	end
end

function TouchButton:doClick()
	self:_press()
	self:_release()
	
end

function TouchButton:setVisible(x)
	if self.prop then self.prop:setVisible(x) end
	if self.propPress then self.propPress:setVisible(x) end
	if self.textLabel then self.textLabel:setVisible(x) end
end

function TouchButton:_press()
	if activeButton then return end
	activeButton=self
	self:setState('down')
	self:setDeckState(true)
	self:onPress()

	if self.sound then				
		self:playSound(self.sound)
	end
	self:emit('button.down',self)
end

function TouchButton:_release(inside)
	self:setState('up')
	
	if self.isToggle then
		self:setToggle(not self.toggle)
	else
		self:setDeckState(false)
	end

	if  inside or self.clickNeedNoRelease then
		if self.onClick then return self:onClick() end
		self:emit('button.click',self)
	end

	self:emit('button.up',self)
	self:onRelease()
	
	if activeButton==self then activeButton=false end
end

function TouchButton:onDestroy()
	if activeButton==self then
		activeButton=false
	end
end

function TouchButton:setToggle(t)
	self.toggle=t
	self:setDeckState(t)
end

function TouchButton:inside(x,y)
	if self.rect then
		x,y=self:worldToModel(x,y)
		local r=self.rect
		return inRect(x,y,r[1],r[2],r[3],r[4])
	else
		local p=self.prop or self.propPress or self.textLabel
		if p then 
			return p:inside(x,y)
		end
	end
end

function TouchButton:setDeckState(down)
	if down then
		if self.propPress then
			self.propPress:setVisible(true)
			if self.prop then
				self.prop:setVisible(false)
			end
		end
	else
		if self.propPress then
			self.propPress:setVisible(false)
			if self.prop then
				self.prop:setVisible(true)
			end
		end
	end
end

function TouchButton:onTouchEvent(ev,id,x,y)
	if ev=='down' and self.state~='down' and not activeButton then
		x,y=self:wndToWorld(x,y)		
		if self:inside(x,y) then
			self.touchId=id
			self:_press()			
		end

	elseif ev=='up' and self.state=='down' and self.touchId==id then
		self.touchId=false
		x,y=self:wndToWorld(x,y)
		self:_release(self:inside(x,y))

	end
end