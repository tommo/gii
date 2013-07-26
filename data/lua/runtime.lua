module('gii',package.seeall)
----------------------------
function doRuntimeScript(name)
	local path = GII_DATA_PATH..'/lua/'..name
	return dofile(path)
end

--------------------------------------------------------------------
GII_VERSION_MAJOR = 0
GII_VERSION_MINOR = 1
GII_VERSION_REV   = 0
--------------------------------------------------------------------

----------------------------
doRuntimeScript 'MOAInterfaces.lua' --REMOVE THIS?
----------------------------

doRuntimeScript	'bridge.lua'
doRuntimeScript	'moduleBridge.lua'
doRuntimeScript	'model.lua'
doRuntimeScript	'MOAIModels.lua'
doRuntimeScript	'debugger.lua'
doRuntimeScript	'renderContext.lua'
----------------------------
doRuntimeScript	'editCanvas.lua'
