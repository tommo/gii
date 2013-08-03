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
require 'mock.asset.ParticleHelper'

local mt1={__newindex=function(t,k,v)
	assert(type(v)=='function')
	rawset(t,k,function(...) setfenv(v,getfenv(2)) return v(...) end)
end
}

local proc=setmetatable({p=setmetatable({},mt1),sp=setmetatable({},mt1)},mt1)

local setfenv,getfenv=setfenv,getfenv

local math=math

function proc.p.moveAlong(ax,ay)
	p.x=p.x+p.dx
	p.y=p.y+p.dy
	if ax then p.dx=p.dx+ax end
	if ay then p.dy=p.dy+ay end
end

function proc.p.slowDown(rate)
	p.dx=p.dx*rate
	p.dy=p.dy*rate
end


function proc.p.moveBack()
	p.x=p.x-p.dx
	p.y=p.y-p.dy
	
end


function proc.p.shake(v)
	p.x=p.x+rand(0-v,v)
	p.y=p.y+rand(0-v,v)
end

function proc.p.moveWave()
	p.x=p.x+p.dy*20
	p.y=p.y+p.dx*10
end

function proc.sp.simple()
	
end

function proc.sp.align()
	sp.rot=vecAngle(p.dy,p.dx)
end

function proc.sp.transform(option)
	if option.x then sp.x=sp.x+option.x end
	if option.y then sp.y=sp.x+option.y end
	if option.sx then sp.sx=sp.sx*option.sx end
	if option.sy then sp.sy=sp.sy*option.sy end
end

function proc.sp.fadeout()
	sp.opacity=ease(1,0,EaseType.EASE_OUT)
end

function proc.sp.turn(v,offset)
	sp.rot=offset and time*v+offset or time*v
end

function proc.sp.color(r,g,b)
	if r then sp.r=r end
	if g then sp.g=g end
	if b then sp.b=b end
end

function proc.sp.tweenColor(c1,c2,easetype)
	local r,g,b=c1.r or 1,c1.g or 1,c1.b or 1
	local r1,g1,b1=c2.r,c2.g,c2.b
	easetype=easetype or EaseType.EASE_OUT
	if r1 then	sp.r=ease(r,r1,easetype) end
	if g1 then	sp.g=ease(g,g1,easetype) end
	if b1 then	sp.b=ease(b,b1,easetype) end
end


function proc.sp.spin(radius,speed,offset)
	now=time*(speed/180*math.pi)+(offset or 0)
	sp.x=p.x+cos(now)*radius
	sp.y=p.y+sin(now)*radius
	sp.rot=now*(180/math.pi)
end

function proc.wave(freq,min,max)
	min=min or 0
	max=max or 1
	freq=freq or 1
	if freq==1 then
		return sin(time*3.141593)*(max-min)+min
	else
		return ((sin(time*3.141593*freq/2)*0.5+0.5)*(max-min)+min)
	end
end

addParticleScriptBuiltinSymbol('proc',proc)