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

local pairs,ipairs,setmetatable,unpack=pairs,ipairs,setmetatable,unpack
local insert,remove=table.insert, table.remove
local yield=coroutine.yield
local select = select
local block=MOAICoroutine.blockOnAction

module 'mock'

CLASS: Actor ()


function Actor:__init()
	self.msgbox = {}
	self.state  = 'normal'
	self.coroutines = false
end

--------SIGNAL
function Actor:connect(sig,methodname)
	local connected=self.connected
	if not connected then
		connected={}
		self.connected=connected
	end
	if type(self[methodname])~='function' then
		error('Method not found:'..methodname,2)
	end
	local signal=connectSignalMethod(sig,self,methodname)
	connected[signal]=methodname
end

function Actor:flushSignal(signame)
	while self:pollSignal(signame) do end
end

function Actor:pollSignal(signame, tableResult)
	local polling=self.polling
	
	if polling then
		local poller=polling[signame]
		if poller then
			local firstParam=poller.firstParam
			
			if not firstParam then 
				return false 
			end
			
			if not firstParam.next then
				poller.firstParam=false
				poller.lastParam=false
			else
				poller.firstParam=firstParam.next
			end
			if tableResult then
				return true,firstParam
			else
				return true,unpack(firstParam)
			end
		end
	else
		polling={} 
		self.polling=polling
	end
	
	local poller={
		firstParam=false,
		lastParam=false,		
	}

	local function queue(...)
		local param={...}
		local lastParam=poller.lastParam
		if lastParam then
			lastParam.next=param
			poller.lastParam=param
		else
			poller.lastParam=param
			poller.firstParam=param
		end
		
	end
	poller.sig=connectSignalFunc(signame,queue)
	poller.func=queue
	polling[signame]=poller

	return false
end

function Actor:emit(sig,...)
	return emitSignal(sig,...)
end

function Actor:emitSignal(sig,...)
	return emitSignal(sig,...)
end

function Actor:disconnectAll()
	local connected=self.connected
	if  connected then
		for sig in pairs(connected) do
			sig[self]=nil
		end
	end
	local polling=self.polling
	if polling then
		for signame,p in pairs(polling) do
			p.sig[p.func]=nil
		end
	end
end

---- msgbox?
function Actor:tell(msg, data, source)
	return insert(self.msgbox, {msg,data,source})
end

function Actor:flushMsgBox()
	local box=self.msgbox
	self.msgbox={}
	local onMsg=self.onMsg
	if onMsg then 
		for i, m in ipairs(box) do
			onMsg(self,m[1],m[2],m[3])
		end
	end
end

function Actor:clearMsgBox()
	self.msgbox={}
end

function Actor:pollMsg()
	local m=remove(self.msgbox,1)
	if m then return m[1],m[2],m[3] end
	return nil
end

function Actor:waitMsg(...)
	while true do
		local msg,data=self:pollFindMsg(...)
		if msg then return msg,data end
		yield()
	end
end

function Actor:peekMsg()
	local m=self.msgbox[1]
	if m then return m[1],m[2],m[3] end
	return nil
end

function Actor:pollFindMsg(...)
	local msgbox=self.msgbox
	if not msgbox[1] then return nil end
	local count=select('#',...)

	if count==1 then --single version
		local mm=select(1,...)
		while true do
			local m=remove(msgbox,1)
			if m then
				if m[1]==mm then return m[1],m[2],m[3] end
			else
				break
			end
		end

	else
		while true do
			local m=remove(msgbox,1)
			if m then
				local msg=m[1]
				for i=1, count do
					if msg == select(i,...) then
						return m[1],m[2],m[3]
					end
				end
			else
				break
			end

		end
	end

	return nil
end

---- Subscribe & Broadcast
function Actor:subscribe(target, msgTransform)
	local subs=target._subscribers
	if not subs then
		subs={}
		target._subscribers=subs
	end
	subs[self]=msgTransform or false
	local subed=self._subscribed
	if not subed then
		subed={}
		self._subscribed=subed
	end
	subed[target]=true
end

function Actor:unsubscribe(target)
	local subs=target._subscribers
	if subs then 
		subs[self]=nil
		if self._subscribed then
			self._subscribed[target]=nil
		end
	end
end

function Actor:unsubscribeAll()
	local subed=self._subscribed
	if subed then
		for t in pairs(subed) do
			local subs=t._subscribers
			if subs then t[self]=nil end
		end
	end
	self._subscribed=nil
end

function Actor:broadcast(msg,data)
	local subs=self._subscribers
	if not subs then return end
	for obj,transform in pairs(subs) do
		if transform then
			local m1=transform[msg]			
			local tt=type(m1)
			if tt=='function' then
				m1(obj,msg,data,self)
			elseif tt=='string' then
				obj:tell( m1, data, self )
			elseif tt~=false then
				obj:tell( msg, data, self )
			end
		else
			obj:tell( msg, data, self )
		end
	end
end

---------coroutine control
local function coroutineFunc( coroutines, coro, func, ...)
	func( ... )
	coroutines[ coro ] = nil  --automatically remove self from thread list
end

function Actor:addCoroutine( func, ... )
	
	local coro=MOAICoroutine.new()
	
	local coroutines = self.coroutines
	if not coroutines then
		coroutines = {}
		self.coroutines = coroutines
	end
	local tt = type( func )
	if tt == 'string' then --method name
		local _func = self[ func ]
		assert( type(_func) == 'function' , 'method not found:'..func )
		coro:run( coroutineFunc,
			coroutines, coro, _func, self,
			...)
	elseif tt=='function' then --function
		coro:run( coroutineFunc,
			coroutines, coro, func,
			...)
	else
		error('unknown coroutine func type:'..tt)
	end

	coroutines[coro] = true
	return coro
end

----------state control

function Actor:setState(s)
	--TODO: add acceptable state table
	local ps   = self.state
	self.state = s
	local onStateChange = self.onStateChange
	if onStateChange then return onStateChange( self, s, ps ) end
end

function Actor:getState()
	return self.state
end


function Actor:inState(s1,...)
	for i = 1, select( '#', ... ) do
		local s = select( i , ... )
		if s == s1 then return s end
	end
	return false
end

local stringfind=string.find
local function  _isStartWith(a,b,b1,...)
	if stringfind(a,b)==1 then return true end --a:startWith(b)
	if b1 then return _isStartWith(a,b1,...) end
	return false
end

function Actor:inStateGroup(s1,...)
	return _isStartWith(self.state,s1,...)
end

------------wait controls
function Actor:waitStateEnter(...)
	local count = select( '#', ... ) 
	if count == 1 then
		local s = select( 1, ... )
		while true do
			local ss = self.state
			if ss == s then return ss end			
			yield()
		end
	else
		while true do
			local ss = self.state
			for i = 1, count do
				if ss == select(i,...) then
					return ss
				end
			end
			yield()
		end
	end
end

function Actor:waitStateLeave(s)
	while self.state == s do
		yield()
	end
	return self.state
end

function Actor:waitStateChange()
	local s = self.state
	while s == self.state do
		yield()
	end
	return self.state
end

function Actor:waitFieldEqual( name, v )
	while true do
		if self[name]==v then return true end
		yield()
	end
end

function Actor:waitFieldNotEqual( name, v )
	while true do
		if self[name]~=v then return true end
		yield()
	end
end

function Actor:waitFieldTrue( name )
	while true do
		if self[name] then return true end
		yield()
	end
end

function Actor:waitFieldFalse( name )
	while true do
		if not self[name] then return true end
		yield()
	end
end

function Actor:waitSignal(sig)
	local result=nil
	local f=function(...)
		result={...}
	end
	connectSignalFunc(sig,f)
	while not result do yield() end
	disconnectSignal(sig,f)
	return unpack(result)
end

function Actor:waitFrames(f)
	for i=1,f do
		yield()
	end
end

function Actor:waitTime(t)
	local timer=MOAITimer.new()
	timer:setSpan(t)
	timer:start()
	return block(timer)
end

function Actor:timeoutSignal( sig, t )
	local result=nil
	local f=function(...)
		result={...}
	end
	connectSignalFunc(sig,f)
	local t0=self:getTime()
	while not result do 
		if self:getTime()-t0>=t then break end
		yield() 
	end
	disconnectSignal(sig,f)
	if result then 
		return true,unpack(result)
	else
		return false
	end
end

local currentThread=MOAICoroutine.currentThread
function Actor:pauseThisThread( noyield )
	local th = currentThread()
	if th then
		th:pause() 
		if not noyield then	return yield() end
	else 
		error("no thread to pause")
	end
end

function Actor:wait(a)
	if type(a)     == 'number' then
		return self:waitTime(a)
	elseif type(a) == 'table'  then
		return self:waitActionBoth(a)
	elseif type(a) == 'string' then
		return self:waitSignal(a)
	else
		return block(a)
	end
end
----------MOAIAction control

