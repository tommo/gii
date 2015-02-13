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

local traits={}

function getTrait(name)
	return traits[name]
end

function applyTrait(class,name,allowOverwrite)
	local t=getTrait(name)
	assert(t,'No trait found:'..name)
	local onApplyTrait
	local __overwrite=t.__overwrite or {}

	for k,v in pairs(t) do
		local v1=class[k]

		if k~='__overwrite' then 
			if v1 and not allowOverwrite then
				if not __overwrite[k] then
					return error(
						string.format(
						'trait member conflict: %s -> %s',name,k)
					)
				end
			end

			if k~='onApplyTrait' then
				class[k]=v
			else
				onApplyTrait=v
			end
		end
		if not class.__traits then
			class.__traits={}
		end
		
		class.__traits[name]=t

		if onApplyTrait then
			onApplyTrait(t,class)
		end
	end
	return class
end

function registerTrait(name,trait)
	assert(not traits[name], 'Trait already defined:'..name)
	traits[name]=trait
	return trait
end

function newTrait(name)
	local t={}
	return registerTrait(name,t)
end


require 'traits.SingleTouch'