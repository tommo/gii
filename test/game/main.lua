--------------------------------------------------------------------
---Envrionment

luaExtName = '.lua'

function scriptName(n)
	return n..luaExtName
end

function setLuaExtName(ext)
	ext = ext or '.lua'
	luaExtName = ext
	package.path = package.path:gsub( '%.lua', ext )
end

--------------------------------------------------------------------
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

----
MOCK_ASSET_LIBRARY_INDEX = '.moei/asset_table.json'

-------------------
require 'mock.env'
-------------------
setLogLevel( 'warning' )
mock.loadAssetLibrary()

