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


--------------------------------------------------------------------
local DebugHelper = mock.DebugHelper
_codemark = function(s,...) return DebugHelper:setCodeMark(s,...) end
--------------------------------------------------------------------

local startTimePoints={}
function _logtime(name)
	local t1=os._clock()
	startTimePoints[name]=t1
end

function _logtime_end(name)
	local t1=os._clock()
	local t=startTimePoints[name]
	if t then
		printf('time for "%s": %d',name, (t1-t)*1000)
		startTimePoints[name]=false
	end
end

--------------------------------------------------------------------
local logLevelNames = {
	['status']  =  MOAILogMgr.LOG_STATUS,
	['warning'] =  MOAILogMgr.LOG_WARNING,
	['error']   =  MOAILogMgr.LOG_ERROR,
	['none']    =  MOAILogMgr.LOG_NONE,
}

local _logLevel = MOAILogMgr.LOG_WARNING
local _logFile  = false
function setLogLevel( level )
	if type(level) == 'string' then
		level = logLevelNames[level] or MOAILogMgr.LOG_STATUS
	end
	MOAILogMgr.setLogLevel( level )
	_logLevel = level
end

function openLogFile( path )
	_logFile = path
	MOAILogMgr.openFile( path )
end

function closeLogFile()
	MOAILogMgr.closeFile()
	_logFile = false
end

function getLogFile()
	return _logFile
end

--------------------------------------------------------------------
local MOAILog = MOAILogMgr.log
function _log(...) 
	for i = 1, select( '#', ... ) do
		local v = select( i, ... )
		MOAILog( tostring(v) )	
		MOAILog('\t')
	end
	MOAILog('\n')
end

local function _nilFunc() end


function _logf( patt, ... )
	return _log( string.format( patt, ... ) )
end


function _stat( ... )
	if _logLevel >= MOAILogMgr.LOG_STATUS then
		MOAILog('[STATUS:Lua]\t')
		return _log( ... )
	end
end

function _statf( patt, ... )
	if _logLevel >= MOAILogMgr.LOG_STATUS then
		return _stat( string.format( patt, ... ) )
	end
end

function _error( ... )
	if _logLevel >= MOAILogMgr.LOG_ERROR then
		print( debug.traceback( 2 ) )
		MOAILog('[ERROR:Lua]\t')
		return _log( ... )
	end
end

function _errorf( patt, ... )
	if _logLevel >= MOAILogMgr.LOG_ERROR then
		return _error( string.format( patt, ... ) )
	end
end

function _warn( ... )
	if _logLevel >= MOAILogMgr.LOG_WARNING then
		MOAILog('[WARN:Lua]\t')
		return _log( ... )
	end
end

function _warnf( patt, ... )
	if _logLevel >= MOAILogMgr.LOG_WARNING then
		return _warn( string.format( patt, ... ) )
	end
end

function _traceback( msg, ... )
	print( msg )
	print( debug.traceback(2) )
end

--------------------------------------------------------------------
function reportHistogram()
	MOAILuaRuntime.reportHistogram( 'histogram' )
	local f = io.open( 'histogram', 'r' )
	print( f:read( '*a' ) )
	f:close()
end
