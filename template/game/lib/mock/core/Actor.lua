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
local insert,remove = table.insert, table.remove
local yield = coroutine.yield
local select = select
local block = MOAICoroutine.blockOnAction

module 'mock'


CLASS: Actor ()
:MODEL{	
}


function Actor:__init()
	self.state  = 'normal'
	self.msgListeners = {}
	self.coroutines = false
end

--------------------------------------------------------------------
-- LOCAL Signal
--------------------------------------------------------------------
function Actor:registerSignal( id, localMethod )
end

function Actor:signal( id )
end

function Actor:emit( id )
end

--------------------------------------------------------------------
--------GLOBAL SIGNAL
--------------------------------------------------------------------
function Actor:connect( sig, slot )
	return self:connectForObject( self, sig, slot )
end

function Actor:connectForObject( obj, sig, slot )
	local connectedSignals = self.connectedSignals
	if not connectedSignals then
		connectedSignals = {}
		self.connectedSignals = connectedSignals
	end
	
	local tt = type( slot )
	if tt == 'function' then
		local func = slot
		local signal = connectSignalFunc( sig, func )
		table.insert( connectedSignals, { obj, signal, func } )
		
	elseif tt == 'string' then
		local methodName = slot
		if type( obj[methodName] )~='function' then
			error( 'Method not found:'..methodName, 2 )
		end
		local signal = connectSignalMethod( sig, obj, methodName )
		table.insert( connectedSignals, { obj, signal, obj } )

	else
		error( 'invalid slot type:' .. tt )
	end
end

function Actor:emit( sig, ... )
	return emitSignal( sig, ... )
end

function Actor:disconnectAll()
	local connectedSignals = self.connectedSignals
	if not connectedSignals then return end
	for i, entry in ipairs( connectedSignals ) do
		local sig, obj = entry[ 2 ], entry[ 3 ]
		sig[ obj ]=nil
	end
	self.connectedSignals = false
end

function Actor:disconnectAllForObject( owner )
	local connectedSignals = self.connectedSignals
	if not connectedSignals then return end
	local signals1 = {}
	for i, entry in ipairs(connectedSignals) do
		local owner1, sig, obj = unpack( entry )
		if owner == owner1 then
			sig[ obj ] = nil
		else
			table.insert( signals1, entry )
		end		
	end
	self.connectedSignals = signals1
end

--------------------------------------------------------------------
---- MSGListener: a string message based approach
--------------------------------------------------------------------
function Actor:addMsgListener( listener )
	table.insert( self.msgListeners, listener )
	return listener
end

function Actor:removeMsgListener( listener )
	if not listener then return end
	local msgListeners = self.msgListeners
	for i, v in ipairs( msgListeners ) do
		if v == listener then 
			table.remove( msgListeners, i )
			return
		end
	end
end

function Actor:clearMsgListeners()
	self.msgListeners = {}
end

function Actor:tell( msg, data, source )
	for i, listener in pairs( self.msgListeners ) do
		local r = listener( msg, data, source )
		if r == 'cancel' then break	end
	end
end

---------coroutine control
local function _coroutineFuncWrapper( coro, func, ... )
	func( ... )
end

local function _coroutineMethodWrapper( coro, func, obj, ... )
	func( obj, ... )
end

function Actor:_weakHoldCoroutine( newCoro )
	local coroutines = self.coroutines
	if not coroutines then
		coroutines = { [newCoro] = true }
		self.coroutines = coroutines
		return newCoro
	end
	--remove dead ones
	local dead = {}
	for coro in pairs( coroutines ) do
		if coro:isDone() then
			dead[ coro ] = true
		end
	end
	for coro in pairs( dead ) do
		coroutines[ coro ] = nil
	end
	coroutines[ newCoro ] = true
	return newCoro	
end


--------------------------------------------------------------------
function Actor:_createCoroutine( defaultParent, func, obj, ... )
	local coro = MOAICoroutine.new()	

	if defaultParent then coro:setDefaultParent( defaultParent ) end
	local tt = type( func )
	if tt == 'string' then --method name
		local _func = obj[ func ]
		assert( type(_func) == 'function' , 'method not found:'..func )
		coro:run( _coroutineMethodWrapper, coro, _func, obj, ... )
	elseif tt=='function' then --function
		coro:run( _coroutineFuncWrapper, coro, func, ... )
	else
		error('unknown coroutine func type:'..tt)
	end

	local coro = self:_weakHoldCoroutine( coro )
	return coro
end

function Actor:addCoroutineP( func, ... )
	return self:addCoroutinePFor( self, func, ... )
end

function Actor:addCoroutine( func, ... )
	return self:addCoroutineFor( self, func, ... )
end

function Actor:addCoroutinePFor( obj, func, ... )
	return self:_createCoroutine( true, func, obj, ... )
end

function Actor:addCoroutineFor( obj, func, ... )
	return self:_createCoroutine( false, func, obj, ... )
end


local function _coroDaemonInner( obj, f, ... )
	local inner = self:addCoroutineFor( obj, f, ... )
end

local function _coroDaemon( self, obj, f, ... )
	local inner = self:addCoroutineFor( obj, f, ... )
	while not inner:isDone() do
		coroutine.yield()
	end
end

function Actor:addDaemonCoroutine( f, ... )
	return self:addDaemonCoroutineFor( self, f, ... )	
end

function Actor:addDaemonCoroutineFor( obj, f, ... )
	local daemon = MOAICoroutine.new()
	daemon:setDefaultParent( true )
	daemon:run( _coroDaemon, self, obj, f, ... )
	return self:_weakHoldCoroutine( daemon )
end

function Actor:clearCoroutines()
	if not self.coroutines then return end
	for coro in pairs( self.coroutines ) do
		coro:stop()
	end
	self.coroutines = nil
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


function Actor:inState(...)
	for i = 1, select( '#', ... ) do
		local s = select( i , ... )
		if s == self.state then return s end
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

function Actor:waitStateExit(s)
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
	if t > 1000 then
		error('??? wrong wait time ???'..t)
	end
	local timer = MOAITimer.new()
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
	elseif a then
		return block(a)
	end
end
----------MOAIAction control

