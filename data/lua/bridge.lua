local rawget,rawset= rawget,rawset

local bridge = GII_PYTHON_BRIDGE
module('gii',package.seeall)
_M.bridge = bridge
--------------------------------------------------------------------
-- CORE FUNCTIONS
--------------------------------------------------------------------
--communication
_M.emitPythonSignal     = bridge.emitPythonSignal
_M.emitPythonSignalNow  = bridge.emitPythonSignalNow
_M.connectPythonSignal  = bridge.connectPythonSignal
_M.registerPythonSignal = bridge.registerPythonSignal

--data
_M.sizeOfPythonObject   = bridge.sizeOfPythonObject
_M.newPythonDict        = bridge.newPythonDict
_M.newPythonList        = bridge.newPythonList
_M.appendPythonList     = bridge.appendPythonList
_M.deletePythonList     = bridge.deletePythonList
_M.fromUnicode          = bridge.fromUnicode
_M.toUnicode            = bridge.toUnicode
_M.getDict              = bridge.getDict
_M.setDict              = bridge.setDict

--other
_M.throwPythonException = bridge.throwPythonException
_M.getTime              = bridge.getTime

--data conversion
local encodeDict=bridge.encodeDict
local decodeDict=bridge.decodeDict

function tableToDict(table)
	local json=MOAIJsonParser.encode(table)
	return decodeDict(json)
end

function tableToList(table)
	local list=bridge.newPythonList()
	for i, v in ipairs(table) do
		appendPythonList(list,v)
	end
	return list
end

function dictToTable(dict) --just one level?
	local json = encodeDict(dict)
	return MOAIJsonParser.decode(json)
end

local _sizeOf=sizeOfPythonObject
function listToTable(list)
	local c=_sizeOf(list)
	local r={}
	for i = 1, c do
		r[i]=list[i-1]
	end
	return r
end

--------------------------------------------------------------------
-- EDITOR RELATED
--------------------------------------------------------------------
function changeSelection(obj,...)
	if obj then
		bridge.changeSelection(newPythonList(obj,...))
	else
		bridge.changeSelection(nil)
	end
end

-- Environment
-- getProjectExtPath = bridge.getProjectExtPath
-- getProjectPath    = bridge.getProjectPath
-- getAppPath        = bridge.getAppPath
app = bridge.app


--------------------------------------------------------------------
-- PYTHON-LUA DELEGATION CREATION
--------------------------------------------------------------------
function loadLuaWithEnv(file, env, ...)
	local env = setmetatable(env or {}, 
			{__index=function(t,k) return rawget(_G,k) end}
		)
	local func, err=loadfile(file)
	if not func then
		error('Failed load script:'..file..'\n'..err, 2)
	end
	setfenv(func, env)
	local args = {...}
	
	local function _f()
		return func( unpack( args ))
	end
	local function _onError( err, level )
		print ( err )
		print( debug.traceback( level or 2 ) )
		return err, level
	end

	local succ, err = xpcall( _f, _onError )
	if not succ then
		error('Failed start script:'.. file, 2)
	end
	return env
end

--------------------------------------------------------------------
-- Lua Functions For Python
--------------------------------------------------------------------
--TODO: rename MOEIHELPER
stepSim                 = assert(MOEIHelper.stepSim)
setBufferSize           = assert(MOEIHelper.setBufferSize)
local renderFrameBuffer = assert(MOEIHelper.renderFrameBuffer) --a manual renderer caller

local function renderTable(t)
	for i,f in ipairs(t) do
		local tt=type(f)
		if tt=='table' then
			renderTable(f)
		elseif tt=='userdata' then
			renderFrameBuffer(f)
		end
	end
end

function manualRenderAll()
	local rt=MOAIRenderMgr.getBufferTable()
	if rt then
		renderTable(rt)
	end
	renderFrameBuffer(MOAIGfxDevice.getFrameBuffer())
end


-------------------------------------------