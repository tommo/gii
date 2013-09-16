module( 'gii', package.seeall )
--------------------------------------------------------------------
--Env
--------------------------------------------------------------------
--[[
	PROJECT ENVIRONMENT VARIABLES
	* should be set by either editor or runtime launcher 
]]
-- GII_VERSION_MAJOR           = 0
-- GII_VERSION_MINOR           = 1
-- GII_VERSION_REV             = 0
-- GII_PROJECT_SCRIPT_PATH     = 'game/script'
-- GII_PROJECT_ASSET_PATH      = 'game/asset'
-- GII_PROJECT_SCRIPT_LIB_PATH = 'game/lib'


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
--EDITOR MODULES
--------------------------------------------------------------------
doRuntimeScript 'MOAInterfaces.lua' --REMOVE THIS?

----------------------------
doRuntimeScript	'bridge.lua'
doRuntimeScript	'debugger.lua'

--------------------------------------------------------------------
doRuntimeScript	'MOAIModel.lua'

----------------------------
doRuntimeScript	'RenderContext.lua'
doRuntimeScript	'EditCanvasContext.lua'


--------------------------------------------------------------------
--DEFAULT RUNTIME MODULES
--------------------------------------------------------------------
require 'GameModule'
GameModule.addGameModulePath( GII_PROJECT_ASSET_PATH .. '/?.lua' )
GameModule.addGameModulePath( GII_PROJECT_ASSET_PATH .. '/?/init.lua' )
