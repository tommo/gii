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
local pairs,ipairs=pairs,ipairs
local tremove=table.remove
local random=math.random
local floor=math.floor
local tonumber=tonumber
local tostring=tostring

local _print = print

function printf(patt,...)
	return print(string.format(patt,...))
end

-----USE this to find  forgotten log location
-- function print(...)
-- 	_print(debug.traceback())
-- 	return _print(...)
-- end


--------Random number helpers
function randi(mi,ma)
	mi,ma=floor(mi),floor(ma)
	return floor(mi+random()*(ma-mi+1))
end

function rand(mi,ma)
	return mi+random()*(ma-mi)
end

function noise(n)
	return (random()*2-1)*n
end

function noisei(n)
	return math.floor( (random()*2-1)*n)
end

function prob(n)
	if n<=0 then return false end
	if n>=100 then return true end
	local r=n
	
	return random()*100<=n 
end

function probselect(t)
	
	local total=0
	for i, s in ipairs(t) do
		total=total+s[1]
	end
	
	local k=random()*total
	local kk=0

	for i, s in ipairs(t) do
		local p=s[1]
		if k>kk and k<=kk+p then return s[2] end
		kk=kk+p
	end
	return t.default
end


function probselect2(t)
	
	local total=0
	local t1={}
	local c=1
	for k, p in pairs(t) do
		total=total+p
		t1[c]={p,k}
		c=c+1
	end
	
	local k=random()*total
	local kk=0

	for i, s in ipairs(t1) do
		local p=s[1]
	if k>kk and k<=kk+p then return s[2] end
		kk=kk+p
	end
	return nil
end

function randselect(t)
	local i=#t
	local k=(math.floor(random()*100*i) % i)+1
	return t[k]
end


function randselectexcept(t,x)
	local v
	local i=#t
	for i=1,10 do
		local k=(math.floor(random()*100*i) % i)+1
		v=t[k]
		if v~=x then break end
	end
	return v
end

function randextract(t)
	local i=#t
	if i<=0 then return nil end
	local k=(math.floor(random()*100*i) % i)+1
	return table.remove(t,k)
end

function table.randremove(t)
	local n=#t
	if n>0 then
		return table.remove(t,randi(1,n))
	else
		return nil
	end
end

-----------

function table.print(t) 
	for k,v in pairs(t) do
		print(k ,v)
	end
end

function table.simplecopy(t)
	local nt={}
	for k,v in pairs(t) do
		nt[k]=v
	end
	return nt
end

function table.listcopy(src,dst,keylist)
	for i, k in ipairs(keylist) do
		dst[k]=src[k]
	end
end

function table.sub(t,f,s)
	local l=#t
	local nt={}
	local e=f+s
	for i=f, e>l and l or e do
		nt[i-f+1]=t[i]
	end
	return nt
end

function table.split(t,s)
	local l=#t
	local t1,t2={},{}
	for i=1, s>l and l or s do
		t1[i]=t[i]
	end
	for i=s+1,l do
		t2[i-s+1]=t[i]
	end
	return t1,t2
end


----------Some Geometry Helpers
local sqrt,atan2=math.sqrt,math.atan2
function distance(x1,y1,x2,y2)
	local dx=x1-x2
	local dy=y1-y2
	return sqrt(dx*dx+dy*dy)
end

function normalize(x,y)
	return sqrt(x*x+y*y)
end

function direction(x1,y1,x2,y2)
	return atan2(y2-y1,x2-x1)
end

function vecDiff(x1,y1,x2,y2)
	local dx=x1-x2
	local dy=y1-y2
	return atan2(dy,dx),sqrt(dx*dx+dy*dy)
end

function inRect(x,y,x0,y0,x1,y1)
	return x>=x0 and x<=x1 and y>=y0 and y<=y1
end

local min,max=math.min,math.max
function rect(x,y,w,h)
	local x1,y1=x+w,y+h
	return min(x,x1),min(y,y1),max(x,x1),max(y,y1)	
end

function rectCenter(x,y,w,h)
	x,y,x1,y1=x-w/2,y-h/2,x+w/2,y+h/2
	return min(x,x1),min(y,y1),max(x,x1),max(y,y1)	
end

function rectCenterTop(x,y,w,h)
	x,y,x1,y1=x-w/2,y,x+w/2,y+h
	return min(x,x1),min(y,y1),max(x,x1),max(y,y1)	
end


local sin=math.sin
local cos=math.cos
local pi=math.pi
local piD=pi/180

function math.cosd(d) return cos(piD*d) end

function math.sind(d) return sin(piD*d) end

function arc2d(a) return a/pi*180 end

function d2arc(d) return d*piD end

function circle(x,y,r,a)
	return x+cos(a)*r,y+sin(a)*r
end

local floor=math.floor
function floors(...)
	local t={...}
	for i,v in ipairs(t) do
		t[i]=floor(v)
	end
	return unpack(t)
end

function vecAngle(s,a)
	return s*cos(a),s*sin(a)
end


-------------General Math Helper
function lerp(v1,v2,k)
	local k1=1-k
	return v1*k1+v2*k
end

local lerp=lerp
function rangeMap(v,s0,e0,s1,e1)
	local r1=e0-s0
	local k=(v-s0)/r1
	return lerp(s1,e1,k)
end

local sin=math.sin

function wave(freq,min,max,off)
	off=off or 0
	return (sin(os.clock()*freq*(2*3.141592653)+off)*(max-min)+(min+max))/2
end

function between(a,min,max)
	return a>=min and a<=max
end

function clamp(v,minv,maxv)
	return v>maxv and maxv or v<minv and minv or v
end

function wrap(v,minv,maxv)
	local r=maxv-minv
	if r<=0 then return minv end
	while true do
		if v>=minv and v<maxv then return v end
		if v>=maxv then
			v=minv+v-maxv
		elseif v<minv then
			v=maxv+v-minv
		end
	end
end

math.clamp=clamp
math.wrap=wrap


function inRange(x,y,diff)
	local d=math.abs(x-y)
	return d<=diff
end

function centerRange(center,range)
	return center-range/2,center+range/2
end

function pow2(x)
	local i=2
	while x>i do
		i=i*2
	end
	return i
end

function isFractal(v)
	return not isInteger(v)
end

function isInteger(v)
	return  (math.floor(v)-v)==0
end



-------Table Helpers
function vextend(t,data)
	return setmetatable(data or {},{__index=t})
end

table.vextend=vextend

function table.extend(t,t1)
	for k,v in pairs(t1) do
		t[k]=v
	end
	return t
end

local next=next
function table.len(t)
	local v=0
	for k in pairs(t) do
		v=v+1
	end
	return v
end

function table.sub(t,s,e)
	local t1={}
	local l=#t
	for i=s, e do
		if i>l then break end
		t1[i-s+1]= t[i]
	end

	return t1
end

function table.sum(t)
	local s=0
	for k,v in ipairs(t) do
		s=s+v
	end
	return s
end

local weakMT={__mode='k'}
function table.weak( n )
	return setmetatable(n or {},weakMT)
end

function table.find( t, v )
	for k, v1 in pairs( t ) do
		if v1==v then return k end
	end
	return nil
end


function stringSet(t, v)
	local res={}
	v=v==nil and true or v
	for i, s in ipairs(t) do
		res[s]=v
	end
	return res
end


local autotableMT={
	__index=function(t,k)
		local r={}
		t[k]=r
		return r
	end
}

function newAutoTable(t1)
	return setmetatable(t1 or {},autotableMT)
end



-------------Strange Helpers
function numWithCommas(n)
  return tostring(math.floor(n)):reverse():gsub("(%d%d%d)","%1,")
                                :gsub(",(%-?)$","%1"):reverse()
end


local eachMT={
	__index=function(t,k)
		t.__methodToCall__=k
		return t
	end,
	__call=function(t,t1,...)
		local m={}
		local methodname=t.__methodToCall__
		if t==t1 then
			for i, o in ipairs(t) do
				m[i]=o[methodname](o,...)
			end
		else
			for i, o in ipairs(t) do
				m[i]=o[methodname](...)
			end
		end
		return unpack(m)
	end
}


function eachT(t)
	return setmetatable(t,eachMT)
end

function each(...)
	return eachT({...})
end


local function _oneOf(v,a,b,...)
	if v==a then return true end
	if b~=nil then
		return _oneOf(v,b,...)
	end
	return false
end

oneOf = _oneOf


--------------TIME & DATE
function formatSecs(s,hour) --return 'mm:ss'
	local m=math.floor(s/60)
	local ss=s-m*60
	if hour then
		local hh=math.floor(s/60/60)
		m=m-hh*60
		return string.format('%02d:%02d:%02d',hh,m,ss)
	else
		return string.format('%02d:%02d',m,ss)
	end
end


function fakeSecs(s) --return '00:ss(99)'
	-- local m=math.floor(s/60)
	-- local ss=s-m*60
	if s>99 then s=99 end
	return string.format('%02d:%02d',0,s)
end


local function timeDiffName(t2,t1)
	local diff=os.difftime(t2,t1)
	if diff<60 then
		return diff..'secs'
	elseif diff<60*60 then
		return math.floor(diff/60)..' mins'
	elseif diff<60*60*24 then
		return math.floor(diff/60/60)..' hours'
	elseif diff<60*60*24*7 then
		return math.floor(diff/60/60/24)..' days'
	elseif diff<60*60*60*24*30 then
		return math.floor(diff/60/60/24/7)..' weeks'
	else
		return math.floor(diff/60/60/24/30)..' months'
	end
end

----------Color helpers
local ssub=string.sub

function hexcolor(s,alpha) --convert #ffffff to (1,1,1)
	local r,g,b
	r=tonumber('0x'..ssub(s,2,3))/255
	g=tonumber('0x'..ssub(s,4,5))/255
	b=tonumber('0x'..ssub(s,6,7))/255
	return r,g,b,alpha or 1
end


function HSL(h, s, l, a)
   if s == 0 then return l,l,l,a or 1 end
   -- h, s, l = h/60, s, l
   h=h/60
   local c = (1-math.abs(2*l-1))*s
   local x = (1-math.abs(h%2-1))*c
   local m,r,g,b = (l-.5*c), 0,0,0
   if h < 1     then r,g,b = c,x,0
   elseif h < 2 then r,g,b = x,c,0
   elseif h < 3 then r,g,b = 0,c,x
   elseif h < 4 then r,g,b = 0,x,c
   elseif h < 5 then r,g,b = x,0,c
   else              r,g,b = c,0,x
   end
   return 
   	math.ceil((r+m)*256)/256,
   	math.ceil((g+m)*256)/256,
   	math.ceil((b+m)*256)/256,
   	a or 1
end


function gradColor(colors,k)
	local count=#colors
	
	assert(count>1)

	local spans=count-1
	local pitch=1/spans
	local start=math.floor(k/pitch)
	
	local frac=(k-start*pitch)/pitch
	


	local r1,g1,b1,a1 = unpack(colors[start+1])
	local r2,g2,b2,a2 = unpack(colors[math.min(start+2,count)])
	
	-- print(r1,g1,b1,r2,g2,b2,frac)

	return lerp(r1,r2,frac),
		   lerp(g1,g2,frac),
		   lerp(b1,b2,frac),
		   lerp(a1 or 1,a2 or 1,frac)
end



------------extend clock closure
function newClock(srcTimer)
	srcTimer=srcTimer or os.clock
	-- local base=srcTimer()
	local paused=true
	local lasttime=0
	local elapsed=0

	return function(op,arg)
		op = op or 'get'

		if op=='reset' then
			lasttime=srcTimer()
			elapsed=0
			paused=true
			return 0
		elseif op=='set' then
			lasttime=srcTimer()
			elapsed=arg	or 0		
			return elapsed
		end

		if paused then
			if op=='get' then
				return elapsed
			elseif op=='resume' then
				paused=false
				lasttime=srcTimer()
				return elapsed
			end
		else
			local newtime=srcTimer()
			elapsed=elapsed+(newtime-lasttime)
			lasttime=newtime
			if op=='get' then
				return elapsed
			elseif op=='pause' then
				paused=true
				return elapsed
			end
		end
	end
end


function tickTimer(defaultInterval,srcTimer)
	srcTimer=srcTimer or os.clock
	local baseTime=srcTimer()
	defaultInterval=defaultInterval or 1
	return function(interval)
		interval=interval or defaultInterval
		local ntime=srcTimer()
		if ntime>= baseTime+interval then
			baseTime=baseTime+interval
			return true
		end
		return false
	end
end


function ticker(m,i)
	i=i or 0
	local t=coroutine.wrap(function()
		while true do
			i=i+1
			if i>=m then
				i=coroutine.yield(true) or 0
			else
				coroutine.yield(false) 
			end
		end
	end)
	return t
end

function tickerd(m,i)
	i=i or 0
	local t=coroutine.wrap(function()
		local mm=m
		while true do
			i=i+1
			if i>=mm then
				mm=coroutine.yield(true) or m
				i=0
			else
				mm=coroutine.yield(false) or m
			end
		end
	end)
	return t
end


----String Helpers

function string.startWith(s,s1)
	local ss=string.sub(s,1,#s1)
	return ss==s1
end

function string.endWith(s,s1)
	local l=#s1
	local ss=string.sub(s,-l,-1)
	return ss==s1
end

function checkDimension(x,y,w,h)
	return (x==w and y==h) or (x==h and y==w)
end

-------Debug Helper?
local nameCounters={} --setmetatable({},{__mode='k'})
function nameCount(name,c)
	local v=nameCounters[name] or 0
	v=v+c
	print(name, c>0 and "+"..c or "-"..math.abs(c),'-> ',v)
	nameCounters[name]=v
	return v
end

function dostring(s,...)
	local f=loadstring(s)
	return f(...)
end

local counts={}
function callLimiter(name,count,onExceed)
	if not count then counts[name]=0 return end
	local c=counts[name] or 0
	c=c+1
	if c>=count then 
		if onExceed then onExceed() end
		return error('call limited exceed:'..name)
	end
	counts[name]=c
end

function loadSheetData(t,container) --load data converted from spreadsheet
	--read column title
	container=container or {}
	for tname,sheet in pairs(t) do
		
		local mode
		if tname:match('@kv') then 
			mode='kv'
		elseif tname:match('@list') then
			mode='list'
		elseif tname:match('@raw') then
			mode='raw'
		else
			mode='normal'
		end

		tname=tname:match('([^@]*)[%.@]*')
		local r1=sheet[1]
		local colCount=#r1
		local result={}

		if mode~='raw' then
			for i=2,#sheet do
				local row=sheet[i]
				if next(row) then --skip empty row
				
					if mode=='list' then
						local data={}
						for j=1,colCount do
							local col=r1[j]
							data[col]=row[j]
						end
						result[i-1]=data
					else
						local key=row[1]
						if key then
							assert(not result[key], "duplicated key:"..key)
							if mode=='kv' then
								data=row[2]
							else
								data={}
								for j=2,colCount do
									local col=r1[j]
									data[col]=row[j]
								end
							end
							result[key]=data
						end
					end

				end --end if empty 
			end --endfor
		else--raw mode
			result=sheet
		end
		-- print(">>>>table:",tname,result)
		-- for k,v in pairs(result) do
		-- 	print(k,v)
 	-- 	end
 	-- 	print("------")
		container[tname]=result
	end

	return container
end

io.stdout:setvbuf("no")

function makeStrictTable(t)
	return setmetatable(t or {}, {
			__index=function(t,k) error("item not found:"..k, 2) end
		}
	)
end


--------STACK & QUEUE
function newStack()
	local s={}
	local t=0
	local function pop(self) --fake parameter
		if t==0 then return nil end
		local v=s[t]
		s[t]=nil
		t=t-1
		return v
	end

	local function peek(self)
		return t>0 and s[t] or nil
	end

	local function push(self,v)
		t=t+1
		s[t]=v
		return v
	end

	return {_stack=s, pop=pop,peek=peek,push=push}
end

function newQueue()
	local s={}
	local t=0
	local h=0
	local function pop(self) --fake parameter
		if h>=t then return nil end
		h=h+1
		local v=s[h]
		s[h]=nil
		return v
	end

	local function peek(self)
		return h>=t and s[h] or nil
	end

	local function push(self,v)
		t=t+1
		s[t]=v
		return v
	end

	return {_queue=s, pop=pop,peek=peek,push=push}
end
