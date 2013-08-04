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


local pairs,ipairs,setmetatable,unpack=pairs,ipairs,setmetatable,unpack


registerSignals{
	'msg',
	'app.start',
	'app.resume',
	'app.end',

	'game.init',
	'game.update',
	'gfx.resize',

	'scene.update',
	'scene.enter',
	'scene.exit'
}



CLASS: Game () 
	:MEMBER{

		__init={
			version = "",

			scenes        = {},
			gfx           = { w = 640, h = 480, viewportRect = {0,0,640,480} },
			time          = 0,

			developing    = false,

			currentRenderContext = 'game',    -- for editor integration

		}

	}

------Init
local defaultGameOption={
	title            = 'Hatrix Game',

	settingFileName  = '_settings',
	debugEnabled     = false,

	virtualDevice    = 'iphone',
	screenSize       = 'full',
	screenKeepAspect = true,

	globalFrameBuffer= false,
	forceResolution  = false
}


function Game:init( option )
	option = table.vextend( defaultGameOption, option or {} )
	self.option = option
	---load virtual device configuration
	local virtualDevice = option.virtualDevice
	if virtualDevice then
		local vtype
		local orient, zoom = option.orient or 'portrait', 1

		if type( virtualDevice ) == 'table' then
			orient = virtualDevice.orient or orient or 'portrait'
			zoom   = virtualDevice.zoom or 1
			vtype  = virtualDevice.type
		elseif type( virtualDevice ) == 'string' then
			vtype = virtualDevice
		end

		if orient == 'auto' then orient = 'portrait' end

		local w,h = getResolutionByDevice( vtype, orient )
		assert( w*h > 0, 'Unknown device.' )

		self.virturalDeviceResolution = { w, h }
		self.virturalDeviceZoom       = zoom
		self.virtualDeviceOrient      = orient
	end

	if option.forceResolution then
		self.virturalDeviceResolution = { unpack(option.forceResolution) }
	end

	---determine screen size
	local screenSize = option.screenSize or 'full'
	local screenWidth, screenHeight

	if screenSize == 'full' then
		local dw, dh = getDeviceResolution()
		
		if dw * dh == 0 then --no desktop, use virtual device
			dw, dh = unpack(self.virturalDeviceResolution)
		end

		local zoom   = option.screenZoom or 1
		local orient = option.orient
		screenWidth, screenHeight = dw * zoom, dh * zoom
		-- swap w/h to match orientation
		if 
			( orient == 'landscape' and screenWidth < screenHeight )
			or
			( orient == 'portrait'  and screenWidth > screenHeight ) 
		then
			screenWidth, screenHeight = screenHeight, screenWidth
		end
	else
		assert( type(screenSize)=='table' )
		screenWidth, screenHeight = unpack(option.screenSize)
	end
	
	----initialize graphics
	self:openWindow( 
		option.title,
		screenWidth, screenHeight, option.screenKeepAspect
		)
	
	-----data setting
	self.settingFileName = option.settingFileName
	self.userDataPath    = MOAIEnvironment.documentDirectory or '.'

	-------Setup Action Root
	self.time     = 0
	self.throttle = 1
	self.isPaused = false

	local actionRoot=MOAICoroutine.new()
	actionRoot:run( function()
			while true do
				self:onRootUpdate( coroutine.yield() ) --delta time get passed in
			end
		end
	)
	MOAIActionMgr.setRoot( actionRoot )
	MOAISim.setLoopFlags( MOAISim.SIM_LOOP_ALLOW_SPIN )
	self.actionRoot = actionRoot
	self:setThrottle( 1 )

	-------Setup Callbacks
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

	

	collectgarbage('setpause',80)
	collectgarbage('setstepmul',200)
	
	----ask other systems to initialize
	emitSignal( 'game.init' )

	-----preload
	for n,s in pairs( self.scenes ) do
		if s.onPreload then s:onPreload() end
	end
	
	local data=self:loadSettingData( self.settingFileName )
	self.settingData = data or {}

	----if resize event occurs before game init
	if self.pendingResize then
		self:onResize( unpack(self.pendingResize) )
		self.pendingResize = false
	end

	----make inputs work
	initDefaultInputEventHandlers()

	----audio
	initFmodDesigner()
	--initUntz()

	----physics
	self.b2world = MOAIBox2DWorld.new()
	self:setupBox2DWorld()
	self.b2world:start()
end


------Scene control
function Game:addScene( name, scn, initNow )
	assert( not self.scenes[ name ], 'Duplicated scene:'..name )

	self.scenes[ name ] = scn
	scn.name = name
	scn.game = self
	
	if initNow then	return scn:init() end
end

function Game:getScene( name )
	return self.scenes[ name ]
end

function Game:enterScene(name,option)
	local scn=self.scenes[ name ]
	assert( scn, 'scene not found:'..name )
	if scn.active then return end
	return scn:enter( option or {} )
end

function Game:getActiveScenes()
	local l = {}
	for k, scn in pairs( self.scenes ) do
		if scn.active then l[k] = scn end
	end
	return l
end



------Action related
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
	emitSignal('game.update', delta)
end


function Game:setStep(step,stepMul)
	if step then MOAISim.setStep(step) end
	if stepMul then MOAISim.setStepMultiplier(stepMul) end
end

function Game:pause()
	self.paused = true
	return self.actionRoot:pause()
end

function Game:stop()
	os.exit() --TODO:  ????
end

function Game:start()
	self.paused = false
	return self.actionRoot:stop()
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
	local r=self.actionRoot.prev
	if r then 
		self.actionRoot=r 
		MOAIActionMgr.setRoot(self.actionRoot)
	end
end

function Game:setThrottle(v)
	self.throttle=v
	return self.actionRoot:throttle(v*1)
end

-------------------------------
--------Graphics related

function Game:openWindow(name, w, h, keepAspect)
	local virturalDeviceResolution = self.virturalDeviceResolution or {640,480}
	local vw, vh = getDeviceResolution()
	if vw * vh == 0 then --no desktop, use virtual device
		vw, vh = unpack(virturalDeviceResolution)
		vw = vw* self.virturalDeviceZoom
		vh = vh* self.virturalDeviceZoom
	end

	MOAISim.openWindow(name, vw, vh)
	
	local mainViewport = MOAIViewport.new ()

	local deviceWidth, deviceHeight = vw, vh
	if vw > vh then --
		deviceWidth, deviceHeight = vh, vw
	else
		deviceWidth, deviceHeight = vw, vh
	end
	local gfx = {
		mainViewport = mainViewport,
		w = w,
		h = h,
		screenWidth  = w,
		screenHeight = h,
		screenRatio  = w/h,
		
		deviceWidth  = deviceWidth,
		deviceHeight = deviceHeight,
		deviceRatio  = deviceWidth/deviceHeight,

		viewWidth   = vw,
		viewHeight  = vh,
		viewRatio   = vw/vh,

		keepAspect = keepAspect or true,
	}
	
	self.gfx = gfx
	self:updateViewport()

end

function Game:getPos( name, ox, oy )
	local gfx=self.gfx
	ox,oy=ox or 0, oy or 0
	if name=='top' then
		return gfx.h/2+oy
	elseif name=='bottom' then
		return -gfx.h/2+oy
	elseif name=='left' then
		return -gfx.w/2+ox
	elseif name=='right' then
		return gfx.w/2+ox
	elseif name=='left-top' then
		return -gfx.w/2+ox,gfx.h/2+oy
	elseif name=='left-bottom' then
		return -gfx.w/2+ox,-gfx.h/2+oy
	elseif name=='right-top' then
		return gfx.w/2+ox,gfx.h/2+oy
	elseif name=='right-bottom' then
		return gfx.w/2+ox,-gfx.h/2+oy
	elseif name=='center' then
		return ox,oy
	elseif name=='center-top' then
		return ox,gfx.h/2+oy
	elseif name=='center-bottom' then
		return ox,-gfx.h/2+oy
	elseif name=='left-center' then
		return -gfx.w/2+ox,oy
	elseif name=='right-center' then
		return gfx.w/2+ox,oy
	else
		return error('what position?'..name)
	end
end

function Game:getWorldSize( scale )
	local gfx = self.gfx
	scale = scale or 1
	return gfx.w*scale, gfx.h*scale
end

function Game:getViewSize( scale )
	local gfx = self.gfx
	scale = scale or 1
	return gfx.viewWidth*scale, gfx.viewHeight*scale
end

function Game:updateViewport()
	local gfx = self.gfx

	local w, h       = gfx.w, gfx.h
	local vw,vh      = gfx.viewWidth, gfx.viewHeight
	local viewport   = gfx.mainViewport
	local keepAspect = gfx.keepAspect
	-- vw,vh
	if keepAspect then
		local viewportRect

		local aspect = w/h
		local tw, th = vh*aspect, vw/aspect

		if tw>vw then
			tw=vw
			th=th
		else
			th=vh
			tw=tw
		end
		local tl,tt = (vw-tw)/2, (vh-th)/2
		viewportRect = { tl, tt, tl+tw, tt+th }
		viewport:setSize( unpack(viewportRect) )
		viewport:setScale( gfx.w, gfx.h )

		gfx.ox = tl
		gfx.oy = tt		
		gfx.sx = tw/w
		gfx.sy = th/h

		gfx.viewportRect = viewportRect
		
	else
		viewport:setSize( 0, 0, vw, vh )
		viewport:setScale( w, h )
		gfx.ox = 0
		gfx.oy = 0
		gfx.sx = vw/w
		gfx.sy = vh/h
		gfx.viewportRect = { 0, 0, vw, vh }

	end

end

function Game:onResize(w,h)
	local gfx = self.gfx
	-- _stat('resize', w, h )
	
	if not gfx then
		self.pendingResize = {w,h}
		return
	end	

	gfx.viewWidth  = w
	gfx.viewHeight = h

	self:updateViewport()
	emitSignal('gfx.resize', w, h)

end

function Game:grabNextFrame( filepath )
	return grabNextFrame( filePath, MOAIGfxDevice.getFrameBuffer() )
end


---------Data settings
function Game:updateSetting(key,data, persistLater)
	self.settingData[key]=data
	if not persistLater then
		self:saveData(self.settingFileName,self.settingData)
	end
end

function Game:getSetting(key)
	return self.settingData[key]
end

function Game:saveSettingData( filename, data )
	local str  = MOAIJsonParser.encode( data )
	local raw  = MOAIDataBuffer.deflate( str, 0 )
	local file = io.open( self.userDataPath..'/'..filename, 'wb' )
	file:write( raw )
	file:close()
	--todo: exceptions?
	return true
end

function Game:loadSettingData(filename)
	local file=io.open( self.userDataPath..'/'..filename, 'rb' )
	if file then
		local raw = file:read('*a')
		local str = MOAIDataBuffer.inflate( raw )
		return MOAIJsonParser.decode( str )
	else
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
	return MOAIGfxDevice.getFrameBuffer():setClearColor( r,g,b,a )
end

--------------------------------------------------------------------
--PHYSICS
local defaultWorldSettings = {
	gravity               = { 0, -100 },
	unitsToMeters         = 1,
	velocityIterations    = 4,
	positionIterations    = 6,

	angularSleepTolerance = 0,
	linearSleepTolerance  = 0,
	timeToSleep           = 0,

	autoClearForces       = true,

}

function Game:setupBox2DWorld( settings )
	settings = settings or defaultWorldSettings 
	local world = self.b2world
	
	if settings.unitsToMeters then
		world:setUnitsToMeters ( settings.unitsToMeters )
	end
	
	if settings.gravity then
		world:setGravity ( unpack(settings.gravity) )
	end
	
	local velocityIterations, positionIterations = settings.velocityIterations, settings.positionIterations
	velocityIterations = velocityIterations or defaultWorldSettings.velocityIterations
	positionIterations = positionIterations or defaultWorldSettings.positionIterations
	world:setIterations ( velocityIterations, positionIterations )

	world:setAutoClearForces ( settings.autoClearForces )

	-- world:setTimeToSleep           ( settings.timeToSleep )
	-- world:setAngularSleepTolerance ( settings.angularSleepTolerance )
	-- world:setLinearSleepTolerance  ( settings.linearSleepTolerance )

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
----
function Game:setRenderStack( context, deviceRenderTable, bufferTable, renderTableMap )
	--render context helper for GII
	local gii = rawget( _G, 'gii' )
	if gii then
		local renderContext = gii.getRenderContext( context )
		assert( renderContext, 'render context not found:' .. context )
		local renderTableMap1 = {}
		for fb, rt in pairs( renderTableMap ) do
			table.insert( renderTableMap1, { fb, rt } )
		end
		renderContext.renderTableMap    = renderTableMap1
		renderContext.bufferTable       = bufferTable
		renderContext.deviceRenderTable = deviceRenderTable
	elseif context ~= 'game' then
		_error( 'no gii module found for render context functions')
	end

	if context == self.currentRenderContext then
		for framebuffer, renderTable in pairs( renderTableMap ) do
			framebuffer:setRenderTable( renderTable )
		end
		MOAIGfxDevice.getFrameBuffer():setRenderTable( deviceRenderTable )	
		MOAIRenderMgr.setBufferTable( bufferTable )
	end
end

function Game:setCurrentRenderContext( key )
	self.currentRenderContext = key or 'game'
end

function Game:getCurrentRenderContext()
	return self.currentRenderContext or 'game'
end


-- CLASS: RenderContext()

-- function RenderContext:__init( name )
-- 	self.name = name
-- 	self.frameBufferTable = setmetatable( {}, { __mode = 'k' } )
-- end

-- function RenderContext:setFrameBufferRenderTable( fb, t )
-- 	self.fb:getRenderTable[ fb ] = t
-- end

-- function RenderContext:setBufferTable( t )
	
-- end



game = Game()
