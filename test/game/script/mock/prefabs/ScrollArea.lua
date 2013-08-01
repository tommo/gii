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

local CLASS: ScrollAreaInner ( Entity )

local fillRect=MOAIDraw.fillRect
local setPenColor=MOAIGfxDevice.setPenColor


CLASS: ScrollArea ( Entity )

function ScrollArea:__init(data)	
	self.setting=table.extend( 
				{
					width=100,
					height=100,
					innerWidth=1000,
					innerHeight=1000,
					maxSpeed=20,
					damping=.95,
					scrollbar=false,					
				},data.setting)
end

function ScrollArea:onLoad()
	local l=self.scene:addLayer(self)
	self.inner=self:addChild(ScrollAreaInner(),nil,l)
	self.innerLayer=l
	self.touch=false

	self.px,self.py=0,0 --press pos

	self.sx,self.sy=0,0 --scroll pos
	self.tx,self.ty=0,0

	self.vx,self.vy=0,0 --speed
	local setting=self.setting
	self:setRect(setting.width,setting.height)
	self:setInnerRect(setting.innerWidth,setting.innerHeight)

end

function ScrollArea:setScroll(x,y)
	-- self.inner:setLoc(x,y)
	self.sx,self.sy=x or 0 ,y  or 0
end

function ScrollArea:setRect(w,h)
	
	self.width=w
	self.height=h
	local x0,y0=self:modelToWorld(0,0)
	local x1,y1=self:modelToWorld(w,-h)
	self.inner:setScissorRect(x0,y0,x1,y1)
end

function ScrollArea:setInnerRect(w,h)
	self.innerWidth=w
	self.innerHeight=h
end


-- function ScrollArea:onDraw()
-- 	local r,g,b,a=0,1,0,.2
-- 	setPenColor(r,g,b,a)
-- 	local gfx=game.gfx
-- 	-- local x,y=self:modelToWnd(0,0)
-- 	-- print(x,y)
-- 	-- local x1,y1=self:modelToWnd(self.width,-self.height)
-- 	fillRect(0,0,self.width,-self.height)
-- end



function ScrollArea:onUpdate()

	local setting=self.setting
	
	if self.touch then
		local ms=setting.maxSpeed
		self.vx=math.clamp(self.tx-self.sx,-ms,ms)
		self.vy=math.clamp(self.ty-self.sy,-ms,ms)
	end

	local nx,ny=self.sx+self.vx, self.sy+self.vy
	local dw=self.innerWidth-self.width
	local dh=self.innerHeight-self.height
	if nx<0 or dw<=0 then
		nx=0
		self.vx=0
	elseif nx>dw then
		nx=dw
		self.vx=0
	else
		self.vx=self.vx*setting.damping
	end

	if ny<0 or dh<=0 then
		ny=0
		self.vy=0
	elseif ny>dh then 
		ny=dh
		self.vy=0
	else
		self.vy=self.vy*setting.damping
	end

	self.sx=nx
	self.sy=ny
	self.inner:setLoc(nx,ny)

end

function ScrollArea:inside(x,y)
	x,y=self:worldToModel(x,y)
	return x>=0 and x<=self.width and -y>=0 and -y<=self.height
end

function ScrollArea:onTouchEvent(ev,id,x,y)
	local x,y=self:wndToWorld(x,y)
	
	if ev=='press' then
		if not self.touch and self:inside(x,y) then
			self.touch=id
			self.dx=self.sx-x
			self.dy=self.sy-y

			self.tx=self.sx
			self.ty=self.sy
		end
	elseif ev=='release' then
		if self.touch==id then
			self.touch=false
			-- self.tx=x+self.dx
			-- self.ty=y+self.dy
		end

	elseif ev=='drag' then
		if self.touch==id then
			self.tx=x+self.dx
			self.ty=y+self.dy
		end
	end
	
end


return ScrollArea