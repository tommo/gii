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

local signalTable={}
local weakmt={__mode='kv'}
local function getSignal(sig)
	local s=signalTable[sig]
	if not s then 
		return error('signal not found:'..sig)
	end
	return s
end

function connectSignalFunc(sig, func)
	local s=getSignal(sig)
	s[func]=true
	return s
end

function connectSignalMethod(sig, obj, methodname)
	local s=getSignal(sig)
	local m=obj[methodname]
	s[obj]=m
	return s
end

connectSignal = connectSignalFunc

function disconnectSignal(sig,key)
	local s=getSignal(sig)
	s[key]=nil
end

function registerSignal(sig)
	assert(type(sig)=='string','signal name should be string')
	local s=signalTable[sig]
	if s then return error('duplicated signal name:'..sig) end
	-- s=setmetatable({},weakmt)
	s={}
	signalTable[sig]=s
	return s
end

function registerSignals(sigtable)
	for i,k in ipairs(sigtable) do
		registerSignal(k)
	end	
end

function emitSignal(sig,...)
	local s=getSignal(sig)

	for k,v in pairs(s) do
		if v==true then --key is funciton
			k(...)
		else
			v(k,...)
		end
	end
end

