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


----------------------------
function doRuntimeScript(name)
	local path = GII_DATA_PATH..'/lua/'..name
	return dofile(path)
end

function lupaErrFunc( msg )
	return msg .. '\n' ..debug.traceback()
end

python.seterrfunc( lupaErrFunc )
----------------------------
doRuntimeScript 'MOAInterfaces.lua' --REMOVE THIS?

----------------------------
doRuntimeScript	'bridge.lua'
doRuntimeScript	'MOAIModels.lua'
doRuntimeScript	'debugger.lua'

----------------------------
doRuntimeScript	'renderContext.lua'
doRuntimeScript	'editCanvas.lua'
