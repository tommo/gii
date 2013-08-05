--FOR HOST Testing purpose
os.execute('../packer')
os.execute('../conv_config')

luaExtName='.lua'

function scriptName(n)
	return n..luaExtName
end

local function configLuaEnv()
	local os=MOAIEnvironment.osBrand

	local jit=rawget(_G,'jit')
	if jit then
		if os=='iOS' then
			luaExtName='.l2'
			package.path='./?.l2;./src/?.l2;./lib/?.l2;?'
			print('Enable byte code version')
		end

		if os~='iOS' then 
			print('JIT turning on')
			jit.on()
		end
	end
end


configLuaEnv()
-------------------
require 'mock.env'
-------------------
mock.injectGlobalSymbols( _G )

packagePath 'scenes'
packagePath 'objects'

packagePath 'facility'
packagePath 'creature'
packagePath 'task'
packagePath 'item'
packagePath 'skill'

packagePath 'res'
packagePath 'utils'
packagePath 'ui'

packagePath 'test'


require 'cfg'
require 'extension'
require 'res'
--scene
NO_WINDOW=false



local function DoTest()
	if NO_WINDOW then
		return OnTestStart()
	end

	local sceneZoom = 1/2
	local deviceZoom =1/2

	local dw,dh=1024,768
	-- dw,dh=960,640

	if checkOS'iOS' then deviceZoom=1 end

	local globalFrameBuferSetting={
			scale=sceneZoom/deviceZoom,

			clearColor=false,
			clearDepth=true,
			-- smooth=true,
			-- smooth= deviceZoom~=1
		}

	globalFrameBuferSetting=false

	game:init{
		-- debugEnabled=false,
		title='HOST_TEST',
		orient='landscape',
		
		screenSize={
			math.floor(dw*sceneZoom),math.floor(dh*sceneZoom)
		},

		virtualDevice={
			type='ipad',
			orient='landscape',
			zoom=deviceZoom
		},

		-- disableTouchSim=true
		globalFrameBuffer=globalFrameBuferSetting
		,
	}

	-- initReceiver('192.168.1.105')
	-- game.debugEnabled=true


	CLASS: GlobalLogic ( Entity )
	function GlobalLogic:onLoad()	
		return OnTestStart(self)
	end
	game:setDebugEnabled(true)

	CLASS: SceneTest ( Scene )

	function SceneTest:onEnter()
		globalLogic = self:addEntity( GlobalLogic() )
		game:setClearDepth(true)
		game:setClearColor(0,0,0,1)
	end

	game:addScene('test',SceneTest())
	game:enterScene('test')
end

-- require 'test_profiler'
-- require 'test_vbo'
-- require 'test_useraction'
-- require 'test_class'
-- require 'test_offsetgrid'
-- require 'test_manualblocker'
-- require 'test_gridhelper'
-- require 'test_blockaction'
-- require 'test_gridfill'
-- require 'test_pathgrid'
-- require 'test_fsm'
-- require 'test_blockgrid'
-- require 'test_hz'
-- require 'test_model'
require 'test_influencemap'
-- require 'test_mddmap'
-- require 'test_bt'
-- require 'test_bt_loader'
-- require 'test_fmod'
-- require 'test_box2d'
-- require 'test_simplex'
-- require 'test_fake3d'
	
return DoTest()