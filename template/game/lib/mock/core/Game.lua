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

module 'mock'

local gii = rawget( _G, 'gii' )
local collectgarbage = collectgarbage
local pairs,ipairs,setmetatable,unpack=pairs,ipairs,setmetatable,unpack

--------------------------------------------------------------------
----GAME MODULES
--------------------------------------------------------------------

require 'GameModule'
function loadAllGameModules( scriptLibrary )
	if scriptLibrary then
		local data = game:loadJSONData( scriptLibrary )
		if data then 
			for k,v in pairs( data ) do
				GameModule.addGameModuleMapping( k, v )
			end
		end
	end
	for k, node in pairs( getAssetLibrary() ) do
		if node:getType() == 'lua' then
			local modulePath = k:gsub( '/', '.' )
			modulePath = modulePath:sub( 1, #modulePath - 4 )
			GameModule.loadGameModule( modulePath )
		end
	end
	validateAllClasses()
end

--------------------------------------------------------------------
registerSignals{
	'msg',
	'app.start',
	'app.resume',
	'app.end',

	'game.init',
	'game.start',
	'game.pause',
	'game.resume',
	'game.stop',
	'game.update',

	'gfx.resize',
	'device.resize',

	'mainscene.open',
	'mainscene.refresh',
	'mainscene.close',

	'scene.update',

	'layer.update',
	'layer.add',
	'layer.remove',

	'game_config.save',
	'game_config.load',
}


--------------------------------------------------------------------
CLASS: Game () 
	
--------------------------------------------------------------------
--- INITIALIZATION
--------------------------------------------------------------------

function Game:__init()
	self.initialized          = false
	self.graphicsInitialized  = false
	self.currentRenderContext = 'game'    -- for editor integration

	self.version = ""
	self.editorMode = false
	self.scenes        = {}
	self.layers        = {}
	self.gfx           = { w = 640, h = 480, viewportRect = {0,0,640,480} }
	self.time          = 0
	self.mainScene     = Scene()

	local l = self:addLayer( 'main' )
	l.default = true
	self.defaultLayer = l
end

local defaultGameOption={
	title            = 'Hatrix Game',

	settingFileName  = '_settings',
	debugEnabled     = false,

	virtualDevice    = 'iphone',
	screenKeepAspect = true,

	globalFrameBuffer= false,
	forceResolution  = false
}

function Game:loadConfig( path, fromEditor )
	_stat( 'loading game config from :', path )
	assert ( path, 'no config path!' )
	local file = io.open( path, 'r' )
	if not file then 
		_error( 'game configuration not found:', path )
		return 
	end

	local text = file:read('*a')
	file:close()
	local data = MOAIJsonParser.decode( text )
	if not data then
		_error( 'game configuration not parsed:', path )
		return
	end

	return self:init( data, fromEditor )
end

function Game:init( option, fromEditor )
	_stat( '...init game' )
	self.editorMode  = fromEditor or false
	self.initialized = true
	
	self.assetLibraryIndex = option['asset_library']
	self.name    = option['name'] or 'GAME'
	self.version = option['version'] or '0.0.1'
	self.title   = option['title'] or self.name

	--grahpics profile( only for desktop version? )
	self.graphicsOption = option['graphics']

	self:initGraphics( fromEditor )
	
	_stat( '...loading asset library' )
	loadAssetLibrary( self.assetLibraryIndex )
	
	_stat( '...loading game modules' )
	loadAllGameModules( option['script_library'] or false )

	--load layers
	_stat( '...setting up layers' )
	for i, data  in ipairs( option['layers'] or {} ) do
		local layer 

		if data['default'] then
			layer = self.defaultLayer
			layer.name = data['name']
		else
			layer = self:addLayer( data['name'] )
		end
		layer:setSortMode( data['sort'] )
		layer:setVisible( data['visible'] ~= false )
		layer:setEditorVisible( data['editor_visible'] ~= false )
		layer.parallax = data['parallax'] or {1,1}
		layer.priority = i
		layer:setLocked( data['locked'] )
	end

	table.sort( self.layers, 
		function( a, b )
			local pa = a.priority or 0
			local pb = b.priority or 0
			return pa < pb
		end )
	
	if fromEditor then
		local layer = self:addLayer( '_GII_EDITOR_LAYER' )
		layer.priority = 1000000
	end

	----- Global Objects
	_stat( '...loading global game objects' )
	self.globalObjectLibrary = GlobalObjectLibrary()
	self.globalObjectLibrary:load( option['global_objects'] )

	--load setting data
	_stat( '...loading setting data' )
	self.settingFileName = option['setting_file'] or 'setting'
	self.userDataPath    = MOAIEnvironment.documentDirectory or '.'
	local settingData = self:loadSettingData( self.settingFileName )
	self.settingData  = settingData or {}

	_stat( '...setting up action root' )
	-------Setup Action Root
	self.time     = 0
	self.throttle = 1
	self.isPaused = false

	local actionRoot=MOAITimer.new()
	actionRoot:setMode( MOAITimer.CONTINUE )
	
	MOAIActionMgr.setRoot( actionRoot )
	local actionRootDecoy=MOAICoroutine.new()	
	actionRootDecoy:run( function()
			while true do
				local dt = coroutine.yield()
				self:onRootUpdate( dt ) --delta time get passed in
			end
		end
	)

	self.actionRoot = actionRoot
	self:setThrottle( 1 )

	-------Setup Callbacks
	_stat( '...setting up session callbacks' )
	if rawget( _G, 'MOAIApp' ) then
		MOAIApp.setListener(
			MOAIApp.SESSION_END, 
			function() return emitSignal('app.end') end 
			)
		MOAIApp.setListener(
			MOAIApp.SESSION_START,
			function(resume) return emitSignal( resume and 'app.resume' or 'app.start' ) end 
			)
	end

	MOAIGfxDevice.setListener (
		MOAIGfxDevice.EVENT_RESIZE,
		function( width, height )	return self:onResize( width, height )	end
		)

	----make inputs work
	_stat( 'init input handlers' )
	initDefaultInputEventHandlers()

	----audio
	_stat( 'init audio' )
	initFmodDesigner()

	----physics
	_stat( 'init physics' )
	self:setupBox2DWorld()

	----extra
	_stat( '...extra init' )
	-- collectgarbage( 'setpause',   70  )
	-- collectgarbage( 'setstepmul', 150 )	
	-- MOAILuaRuntime.reportGC( true )

	MOAISim.clearLoopFlags()
	MOAISim.setLoopFlags( 
			0
			-- + MOAISim.LOOP_FLAGS_MULTISTEP
			-- + MOAISim.LOOP_FLAGS_DEFAULT
			-- + MOAISim.LOOP_FLAGS_SOAK
			+ MOAISim.SIM_LOOP_ALLOW_BOOST
			-- + MOAISim.SIM_LOOP_ALLOW_SOAK
			
			+ MOAISim.SIM_LOOP_FORCE_STEP
			-- + MOAISim.SIM_LOOP_NO_DEFICIT
			+ MOAISim.SIM_LOOP_NO_SURPLUS
		)
	-- MOAISim.setLongDelayThreshold( 100 )
	-- MOAISim.setBoostThreshold( 3 )	
	-- MOAISim.setStepMultiplier( 2 )	

	
	----ask other systems to initialize
	emitSignal( 'game.init', option )

	----load scenes
	if option['scenes'] then
		for alias, scnPath in ipairs( option['scenes'] ) do
			self.scenes[ alias ] = scnPath
		end
	end
	
	self.entryScene = option['entry_scene']
	self.previewingScene = option['previewing_scene']

	self.mainScene:init()
	_stat( '...init game done!' )
end

function Game:saveConfigToTable()
	local layerConfigs = {}
	for i,l in pairs( self.layers ) do
		if l.name ~= '_GII_EDITOR_LAYER'  then
			layerConfigs[i] = {
				name     = l.name,
				sort     = l.sortMode,
				visible  = l.visible,
				default  = l.default,
				locked   = l.locked,
				parallax = l.parallax,
				editor_visible  = l.editorVisible,
				-- priority = l.priority
			}
		end
	end

	local data = {
		name           = self.name,
		version        = self.version,
		title          = self.title,
		asset_library  = self.assetLibraryIndex,
		graphics       = self.graphicsOption,
		layers         = layerConfigs,
		global_objects = self.globalObjectLibrary:save(),
		scenes         = self.scenes,
		entry_scene    = self.entryScene,
		previewing_scene  = self.previewingScene
	}
	emitSignal( 'game_config.save', data )
	return data
end

function Game:saveConfigToString()
	local data = self:saveConfigToTable()
	return encodeJSON( data )
end

function Game:saveConfigToFile( path )
	local data = self:saveConfigToTable()
	return self:saveJSONData( data, path, 'game config' )
end

function Game:saveJSONData( data, path, dataInfo )
	dataInfo = dataInfo or 'json'
	local output = encodeJSON( data )
	local file = io.open( path, 'w' )
	if file then
		file:write(output)
		file:close()
		_stat( dataInfo, 'saved to', path )
	else
		_error( 'can not save ', dataInfo , 'to' , path )
	end
end

function Game:loadJSONData( path, dataInfo )
	local file = io.open( path, 'rb' )
	if file then
		local str = file:read('*a')
		-- local str = MOAIDataBuffer.inflate( str )
		local data = MOAIJsonParser.decode( str )
		if data then
			_stat( dataInfo, 'loaded from', path )
			return data
		end
		_error( 'invalid json data for ', dataInfo , 'at' , path )
	else
		_error( 'file not found for ', dataInfo , 'at' , path )
	end
end

--------------------------------------------------------------------
--------Graphics related
--------------------------------------------------------------------
function Game:initGraphics( fromEditor )
	local option = self.graphicsOption or {}
	
	local w, h = getDeviceResolution()
	if w * h == 0 then
		w, h  = option['device_width'] or 800, option['device_height'] or 600
	end

	self.deviceWidth  = w
	self.deviceHeight = h

	self.width   = option['width']  or w
	self.height  = option['height'] or h

	self.viewportMode = option['viewport_mode'] or 'fit'

	local fullscreen = option['fullscreen'] or false
	self.fullscreen = fullscreen	

	_stat( 'opening window', self.title, w, h,  self.deviceWidth, self.deviceHeight )
	if not fromEditor then
		--FIXME: crash here if no canvas shown up yet
		MOAISim.openWindow( self.title, self.deviceWidth, self.deviceHeight  )
	end
	self.graphicsInitialized = true
	if self.pendingResize then
		self.pendingResize = nil
		self:onResize( unpack( pendingResize ) )
	end
end

function Game:setViewportScale( w, h )
	if self.width == w and self.height == h then return end
	self.width  = w
	self.height = h
	_stat( 'gfx.resize', w, h )
	emitSignal( 'gfx.resize', w, h )
end

function Game:getViewportScale()
	return self.width, self.height
end

function Game:setDeviceSize( w, h )
	self.deviceWidth  = w
	self.deviceHeight = h
	-- _stat( 'device.resize', w, h )
	emitSignal( 'device.resize', self.width, self.height )
end

function Game:getDeviceResolution( )
	return self.deviceWidth, self.deviceHeight
end

function Game:getViewportRect()
	local viewWidth, viewHeight = MOAIGfxDevice.getViewSize()
	local mode = self.viewportMode or 'fit'
	if mode == 'fit' then
		local aspect = self.width / self.height
		local w = math.min( viewWidth, viewHeight * aspect )
		local h = math.min( viewWidth / aspect, viewHeight )
		local x0,y0,x1,y1
		x0 = ( viewWidth - w ) / 2
		y0 = ( viewHeight - h ) / 2
		x1 = x0 + w
		y1 = y0 + h
		return x0,y0,x1,y1
	end
	return 0, 0, viewWidth, viewHeight
end

function Game:onResize( w, h )
	if not self.graphicsInitialized then
		self.pendingResize = { w, h }
		return
	end	
	self:setDeviceSize( w, h )
end


--------------------------------------------------------------------
------Scene control
--------------------------------------------------------------------
function Game:openEntryScene()
	if self.entryScene then
		self:openSceneByPath( self.entryScene )
		self:start()
	end
end

function Game:openScene( id, additive, arguments )
	local scnPath = self.scenes[ id ]
	if not scnPath then
		return _error( 'scene not defined', id )
	end
	return self:openSceneByPath( scnPath, additive, arguments )
end

function Game:openSceneByPath( scnPath, additive, arguments )
	_stat( 'openning scene:', scnPath )
	local mainScene = self.mainScene
	
	if not additive then
		mainScene:clear( true )
		collectAssetGarbage()
	end
	
	local runningState = mainScene.running
	mainScene.running = false --start entity in batch
	local scn, node = loadAsset( scnPath, { scene = mainScene } )
	if not node then 
		return _error('scene not found', id, scnPath )
	end
	if node.type ~= 'scene' then
		return _error('invalid type of entry scene:', tostring( node.type ), scnPath )
	end
	mainScene.running = runningState
	emitSignal( 'mainscene.open', scn, arguments )
	local args = scn.arguments or {}
	if not additive then args = {} end
	if arguments then
		for k,v in pairs( arguments ) do
			args[ k ] = v
		end
	end
	mainScene.assetPath = scnPath
	--todo: previous scene
	scn.arguments = args
	return scn:flushPendingStart()
end

function Game:scheduleOpenSceneByPath( scnPath, additive, arguments )
	self.pendingLoading = { scnPath, additive, arguments }
end

function Game:onSceneExit( scn )
	assert( scn == self.mainScene )
	local pendingScene = self.pendingScene
	self.mainScene = false
	emitSignal( 'mainscene.close', scn )
	if pendingScene then
		self.pendingScene = false
		return self:openSceneByPath( pendingScene )
	end
end

function Game:getMainScene()
	return self.mainScene
end

--------------------------------------------------------------------
------Layer Control
--------------------------------------------------------------------
function Game:addLayer( name, addPos )
	addPos = addPos or 'last'
	local l = Layer( name )
	
	if addPos == 'last' then
		local s = #self.layers
		local last = s > 0 and self.layers[ s ]
		if last and last.name == '_GII_EDITOR_LAYER' then
			table.insert( self.layers, s, l )
		else
			table.insert( self.layers, l )
		end
	else
		table.insert( self.layers, 1, l )
	end
	return l
end

function Game:removeLayer( layer )
	local i = table.index( self.layers, layer )
	if not i then return end
	table.remove( self.layers, i )
end

function Game:getLayer( name )
	for i, l in ipairs( self.layers ) do
		if l.name == name then return l end
	end
	return nil
end

function Game:getLayers()
	return self.layers
end

--------------------------------------------------------------------
------Action related
--------------------------------------------------------------------
function Game:getTime()
	return self.time
end

function Game:newSubClock()
	return newClock(function()
		return self.time
	end)
end

function Game:onRootUpdate( delta )
	self.time = self.time + delta
	emitSignal( 'game.update', delta )
	if self.pendingLoading then
		local loadingParams = self.pendingLoading
		self.pendingLoading = false
		self:openSceneByPath( unpack( loadingParams ) )
	end
end

function Game:resetClock()
	self.time = 0
end

function Game:setStep(step,stepMul)
	if step then MOAISim.setStep(step) end
	if stepMul then MOAISim.setStepMultiplier(stepMul) end
end

function Game:pause()
	if self.paused then return end 
	self.paused = true
	self.mainScene:pause()
	emitSignal( 'game.pause', self )
end

function Game:stop()
	-- self.actionRoot:stop()
	self.mainScene:stop()
	self.mainScene:clear( true )
	self:resetClock()
	emitSignal( 'game.stop', self )
end

function Game:start()
	_stat( 'game start' )
	self.paused = false
	-- self.actionRoot:start()
	self.mainScene:start()
	
	if self.paused then
		emitSignal( 'game.resume', self )
	else
		emitSignal( 'game.start', self )
	end
end

function Game:isPaused()
	return self.paused
end

function Game:pushActionRoot( action )
	action.prev = self.actionRoot
	self.actionRoot = action
	MOAIActionMgr.setRoot( self.actionRoot )
end

function Game:popActionRoot()
	local current = self.actionRoot
	local r = self.actionRoot.prev
	if r then 
		self.actionRoot = r 
		MOAIActionMgr.setRoot( self.actionRoot )
	end
	return current
end

function Game:getActionRoot()
	return self.actionRoot
end

function Game:setThrottle(v)
	self.throttle=v
	return self.actionRoot:throttle(v*1)
end




--------------------------------------------------------------------
---------Global object( config? )
--------------------------------------------------------------------

function Game:getGlobalObjectLibrary()
	return self.globalObjectLibrary
end

function Game:getGlobalObject( path )
	return self.globalObjectLibrary:get( path )
end

--------------------------------------------------------------------
---------Data settings
--------------------------------------------------------------------
function Game:updateSetting( key, data, persistLater )
	self.settingData[key]=data
	if not persistLater then
		self:saveSettingData( self.settingData, self.settingFileName )
	end
end

function Game:getSetting(key)
	return self.settingData[key]
end

function Game:getUserDataPath( path )
	if not path then return self.userDataPath end
	return self.userDataPath .. '/' ..path
end

function Game:checkSettingFileExists( path )
	local fullPath = self:getUserDataPath( path )
	return MOAIFileSystem.checkFileExists( fullPath )
end

function Game:saveSettingData( data, filename )
	local str  = encodeJSON( data )
	local raw  = MOAIDataBuffer.deflate( str, 0 )
	local file = io.open( self.userDataPath..'/'..filename, 'wb' )
	file:write( raw )
	file:close()
	--todo: exceptions?
	return true
end

function Game:loadSettingData( filename )
	_stat( '...reading setting data from:', filename )
	local file = io.open( self.userDataPath..'/'..filename, 'rb' )
	if file then
		local raw = file:read('*a')
		local str = MOAIDataBuffer.inflate( raw )
		return MOAIJsonParser.decode( str )
	else
		return nil
	end
end

local function _getHash( raw, key )
	local hashWriter = MOAIHashWriter.new()
	hashWriter:openWhirlpool()
	hashWriter:write( raw )
	if key then hashWriter:write( key ) end
	hashWriter:close()
	local hash = hashWriter:getHash()
	return hash
end

function Game:saveSafeSettingData( data, filename, key )
	local str  = encodeJSON( data )
	local raw  = MOAIDataBuffer.deflate( str )
	local file = io.open( self.userDataPath..'/'..filename, 'wb' )
	file:write( _getHash( raw, key ) )
	file:write( raw )
	file:close()
	return true
end

function Game:loadSafeSettingData( filename, key )
	_stat( '...reading setting data from:', filename )
	local stream = MOAIFileStream.new()
	local path = self.userDataPath..'/'..filename
	if stream:open( path, MOAIFileStream.READ ) then
		local hash = stream:read( 64 )
		local raw  = stream:read()
		local str  = MOAIDataBuffer.inflate( raw )
		stream:close()
		if not str then
			_warn( 'cannot extract data', path )
			return nil
		end
		local hash1 = _getHash( raw, key )
		local match = hash == hash1
		local data = MOAIJsonParser.decode( str )
		return data, match
	else
		_warn( 'no file to open', path )
		return nil
	end
end 
-------------------------

function Game:setDebugEnabled( enabled )
	--todo
end

function Game:setClearDepth( clear )
	return MOAIGfxDevice.getFrameBuffer():setClearDepth(clear)
end

function Game:setClearColor( r,g,b,a )
	self.clearColor = r and {r,g,b,a}	 or false
	if gii then
		local renderContext = gii.getRenderContext( 'game' )
		renderContext.clearColor = self.clearColor
	end
	return MOAIGfxDevice.getFrameBuffer():setClearColor( r,g,b,a )
end

--------------------------------------------------------------------
--PHYSICS
--------------------------------------------------------------------
local defaultWorldSettings = {
	gravity               = { 0, -10 },
	unitsToMeters         = 0.01,
	velocityIterations    = 6,
	positionIterations    = 8,

	angularSleepTolerance = 0,
	linearSleepTolerance  = 0,
	timeToSleep           = 0,

	autoClearForces       = true,

}

function Game:setupBox2DWorld( settings )
	settings = settings or defaultWorldSettings 

	local world = MOAIBox2DWorld.new()

	if settings.gravity then
		world:setGravity ( unpack(settings.gravity) )
	end
	
	if settings.unitsToMeters then
		world:setUnitsToMeters ( settings.unitsToMeters )
	end
	
	local velocityIterations, positionIterations = settings.velocityIterations, settings.positionIterations
	velocityIterations = velocityIterations or defaultWorldSettings.velocityIterations
	positionIterations = positionIterations or defaultWorldSettings.positionIterations
	world:setIterations ( velocityIterations, positionIterations )

	world:setAutoClearForces       ( settings.autoClearForces )
	world:setTimeToSleep           ( settings.timeToSleep )
	world:setAngularSleepTolerance ( settings.angularSleepTolerance )
	world:setLinearSleepTolerance  ( settings.linearSleepTolerance )
	world:start()
	self.b2world = world
	local ground = world:addBody( MOAIBox2DBody.STATIC )
	self.b2ground = ground
	return world
end

function Game:getBox2DWorld()
	return self.b2world
end

function Game:startBox2DWorld()
	self.b2world:start()
end

function Game:pauseBox2DWorld( paused )
	self.b2world:pause( paused )
end

--------------------------------------------------------------------
--Context Related
--------------------------------------------------------------------
function Game:setRenderStack( context, deviceRenderTable, bufferTable, renderTableMap )

	if gii then
		local renderContext = gii.getRenderContext( context )
		assert( renderContext, 'render context not found:' .. context )
		-- local renderTableMap1 = {}
		-- for fb, rt in pairs( renderTableMap ) do --copy
		-- 	renderTableMap1[ fb ] = rt
		-- end
		renderContext.renderTableMap    = renderTableMap
		renderContext.bufferTable       = bufferTable
		renderContext.deviceRenderTable = deviceRenderTable
	elseif context ~= 'game' then
		_error( 'no gii module found for render context functions')
	end

	if context == self.currentRenderContext then
		for framebuffer, renderTable in pairs( renderTableMap ) do
			framebuffer:setRenderTable( renderTable )		
		end
		if deviceRenderTable then
			MOAIGfxDevice.getFrameBuffer():setRenderTable( deviceRenderTable )	
		end
		MOAIRenderMgr.setBufferTable( bufferTable )		
	end
end

function Game:setCurrentRenderContext( key )
	self.currentRenderContext = key or 'game'
end

function Game:getCurrentRenderContext()
	return self.currentRenderContext or 'game'
end

function Game:isEditorMode()
	return self.editorMode
end

function Game:collectgarbage( ... )
	collectgarbage( ... )
end

game = Game()

