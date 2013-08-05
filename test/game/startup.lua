--------------------------------------------------------------------
package.path = package.path 
	.. ( ';' .. 'game/script' .. '/?.lua' )
	.. ( ';' .. 'game/script' .. '/?/init.lua' )
	.. ( ';' .. 'game/lib' .. '/?.lua' )
	.. ( ';' .. 'game/lib' .. '/?/init.lua' )


MOCK_ASSET_LIBRARY_INDEX = 'env/config/asset_table.json'

--------------------------------------------------------------------
---Envrionment
--------------------------------------------------------------------
luaExtName = '.lua'

function scriptName(n)
	return n..luaExtName
end

function setLuaExtName(ext)
	ext = ext or '.lua'
	luaExtName = ext
	package.path = package.path:gsub( '%.lua', ext )
end

local function configLuaEnv()
	--TODO: allow config lua extension name through project?
	local os=MOAIEnvironment.osBrand

	local jit=rawget(_G,'jit')
	if jit then
		if os=='iOS' then
			setLuaExtName( '.l2' )
			_stat('Enable byte code version')
		end
	--start jit?
		if os~='iOS' then 
			_stat('JIT turning on')
			jit.on()
		end
	end
end

configLuaEnv()

-------------------
require 'mock.env'
require 'init'
-------------------

setLogLevel( 'status' )
mock.loadAssetLibrary()

require 'sceneTest'