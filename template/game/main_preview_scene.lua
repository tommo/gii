GII_TESTING = true

GII_PROJECT_SCRIPT_LIB_PATH = 'game/lib'
GII_PROJECT_ASSET_PATH      = 'game/asset'

package.path = ''
	.. ( GII_PROJECT_SCRIPT_LIB_PATH .. '/?.lua' .. ';'  )
	.. ( GII_PROJECT_SCRIPT_LIB_PATH .. '/?/init.lua' .. ';'  )
	.. package.path

require 'gamelib'

GameModule.addGameModulePath( GII_PROJECT_ASSET_PATH .. '/?.lua' )
GameModule.addGameModulePath( GII_PROJECT_ASSET_PATH .. '/?/init.lua' )
-- mock.setLogLevel( 'status' )

mock.TEXTURE_ASYNC_LOAD = true
-- mock.TEXTURE_ASYNC_LOAD = false
--------------------------------------------------------------------
--Game Startup Config
--------------------------------------------------------------------
mock.init( 'env/config/game_config.json' )

if game.previewingScene then
	mock.game:openSceneByPath( game.previewingScene )
	mock.game:start()
else
	os.exit()
end

