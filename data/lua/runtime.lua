module( 'gii', package.seeall )
--------------------------------------------------------------------
--Env
--------------------------------------------------------------------
GII_VERSION_MAJOR = 0
GII_VERSION_MINOR = 1
GII_VERSION_REV   = 0

--------------------------------------------------------------------
--Setup package path
--------------------------------------------------------------------
package.path = package.path 
	.. ( ';' .. GII_PROJECT_SCRIPT_LIB_PATH .. '/?.lua' )
	.. ( ';' .. GII_PROJECT_SCRIPT_LIB_PATH .. '/?/init.lua' )


--------------------------------------------------------------------
function doRuntimeScript(name)
	local path = GII_DATA_PATH..'/lua/'..name
	return dofile(path)
end

--------------------------------------------------------------------
function lupaErrFunc( msg )
	return msg .. '\n' ..debug.traceback(2)
end

python.seterrfunc( lupaErrFunc ) --lupa err func

--------------------------------------------------------------------
doRuntimeScript 'MOAInterfaces.lua' --REMOVE THIS?

----------------------------
doRuntimeScript	'bridge.lua'
doRuntimeScript	'debugger.lua'

--------------------------------------------------------------------
doRuntimeScript	'MOAIModel.lua'
doRuntimeScript	'LuaModule.lua'

----------------------------
doRuntimeScript	'RenderContext.lua'
doRuntimeScript	'EditCanvasContext.lua'
