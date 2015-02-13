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

local os=MOAIEnvironment.osBrand

DebugHelper = {}

function DebugHelper:startCrittercism( k1, k2, k3 )
	--TODO: support android
	if os=='iOS' then
		MOAICrittercism.init(
			k1, k2, k3
		)
		self.crittercism = true
	end
end

function DebugHelper:setCodeMark( s, ... )
	if self.crittercism then
		MOAICrittercism.leaveBreadcrumb( string.format( s, ... ) )
	end
end

function DebugHelper:reportUsage()
	print'---------'
	print('FPS:',MOAISim.getPerformance())
	print('Objects:',MOAISim.getLuaObjectCount())
	print('Memory:')
	table.foreach(MOAISim.getMemoryUsage(),print)
	print('--------')

	if game.scenes then
		for k,s in pairs( game.scenes ) do
			local count=table.len(s.objects)
			if count>0 then
				printf('Object in scene "%s": %d',s.name,count)
			end
		end
	end
	print('--------')
	-- print(MOAISim.reportHistogram())
end


function DebugHelper:showDebugLines(show)
	show=show~=false
	for i, l in pairs(moailayers)	 do
		l:showDebugLines(show)
	end
end

function DebugHelper:setDebugEnabled(d)
	self.debugEnabled=d or false
	if not self.debugger then
		require("clidebugger")
		self.debugger=clidebugger
	end
	MOAIDebugLines.setStyle ( MOAIDebugLines.PARTITION_CELLS, 2, 1, 1, 1 )
	MOAIDebugLines.setStyle ( MOAIDebugLines.PARTITION_PADDED_CELLS, 1, 0.5, 0.5, 0.5 )
	MOAIDebugLines.setStyle ( MOAIDebugLines.PROP_WORLD_BOUNDS, 2, 0.75, 0.75, 0.75 )
end

function DebugHelper:pause(msg)
	if self.debugger then
		return self.debugger.pause(msg)
	end
end

function DebugHelper:exitOnError( enabled )
	enabled = enabled~=false
	if enabled then
		MOAISim.setTraceback(
			function(msg)
				print( debug.traceback(msg, 2) )
				os.exit()
			end)
	end
end


--------------------------------------------------------------------
--Profiler ( using ProFi )

Profiler = { coroWrapped = false }
function Profiler:start( time, reportPath )
	local ProFi=require 'mock.tools.ProFi'	
	self.ProFi = ProFi
	--wrap moai coroutine
	if not self.coroWrapped then
		self.coroWrapped = true
		local MOAICoroutineIT = MOAICoroutine.getInterfaceTable()
		local _run = MOAICoroutineIT.run
		MOAICoroutineIT.run = function(self, func,...)
			return _run(self, 
				function(...)
					ProFi:start()
					return func(...)
				end,...)
		end
	end
	--auto stop settings
	if time then
		laterCall( time, function() 
				self:stop()
				if reportPath then 
					self:writeReport( reportPath )
				end
			end)
	end
	--start
	ProFi:setGetTimeMethod(	MOAISim.getDeviceTime	)
	_stat 'start profiler...'
	ProFi:start()
end

function Profiler:stop()
	self.ProFi:stop()
	_stat 'stop profiler...'
end

function Profiler:writeReport( path )
	_statf( 'writing profiler report to : %s', path )
	self.ProFi:writeReport( path )
end



--------------------------------------------------------------------
local tracingCoroutines = setmetatable( {}, { __mode = 'kv' } )
function _reportTracingCoroutines()
	local count = {}
	local countActive = {}
	for coro, tb in pairs( tracingCoroutines ) do
		count[ tb ] = ( count[ tb ] or 0 ) + 1
		if coro:isBusy() then
			countActive[ tb ] = ( countActive[ tb ] or 0 ) + 1
		end
	end
	for tb, c in pairs( count ) do
		if c > 1 then
			print( '------CORO COUNT:', c, countActive[ tb ] )
			print( tb )
		end
	end
end

local oldNew = MOAICoroutine.new
MOAICoroutine.new = function( ... )
	local coro = oldNew( ... )
	tracingCoroutines[ coro ] = debug.traceback( 3 )
	return coro
end

--------------------------------------------------------------------
--dump calltree



--------------------------------------------------------------------
--command
CLASS: DebugCommand ()
	:MODEL{}

function DebugCommand:onExec()
end

function DebugCommand:finish()
end

function DebugCommand:fail()
end

