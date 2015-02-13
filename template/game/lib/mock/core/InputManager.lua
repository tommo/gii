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

require 'mock.core.keymaps'

local _inputDevices = {}

function getInputDevice( name )
	return _inputDevices[ name ]
end


--------------------------------------------------------------------
CLASS: TouchState ()
	:MODEL{}

function TouchState:__init( id )
	self.id = id
	self.down = false
	self.x    = 0
	self.y    = 0
	self.x_b  = 0
	self.y_b  = 0
	self.x0   = 0
	self.y0   = 0

	self.t0   = 0
	self.t1   = 0
	self.t1_b = 0

end

function TouchState:getLoc()
	return self.x, self.y
end

function TouchState:getDeltaStep()
	return self.x - self.x_b, self.y - self.y_b
end

function TouchState:getDelta()
	return self.x-self.x0, self.y-self.y0
end

function TouchState:getDeltaDistance()
	local dx, dy = self.x-self.x0, self.y-self.y0
	return math.sqrt( dx*dx, dy*dy )
end

function TouchState:isDown()
	return self.down
end

function TouchState:getDistance()
	return distance( self.x, self.y, self.x0, self.y0 )
end

function TouchState:getDeltaTime()
	return self.t1 - self.t0
end

function TouchState:getEventDeltaTime()
	return self.t1 - self.t1_b
end

function TouchState:getAverageSpeed()
	local dt = self:getDeltaTime()
	if dt<=0 then return 0 end
	return self:getDistance() / dt
end


--------------------------------------------------------------------
CLASS: JoystickState ()
	:MODEL{}

--------------------------------------------------------------------
CLASS: InputDevice()
function InputDevice:__init( deviceName, virtual )
	self.inputDeviceName = assert( deviceName )
	self._getTime = false
	_inputDevices[ deviceName ] = self
	self.virtual = virtual
	self.allowTouchSimulation = true
	self.enabled = true
	---TOUCH
	self.touchListeners = {}
	self.touchCount  = 16
	self.touches     = {}
	self.touchStates = {}

	---KEY
	self.keyboardListeners = {}
	self.keyStates   = {}

	---MOUSE
	self.mouseListeners  = {}
	self.mouseRandomness = false
	self.mouseState  = {
		x       = 0,
		y       = 0,
		scrollX = 0,
		scrollY = 0,
		dx      = 0,
		dy      = 0,
		--button states
		left      = false,
		right     = false,
		middle    = false,
		leftHit   = 0,
		rightHit  = 0,
		middleHit = 0,
	}

	--JOYSTICKS
	self.joystickListeners = {}

	--MOTION
	self.motionAccuracy  = 1
	self.motionListeners = {}
	self.motionState = {
			x = 0,
			y = 0,
			z = 0,
		}

	--LEVEL
	self.levelState = {
		x = 0,
		y = 0,
		z = 0,
	}

	--COMPASS
	self.compassHeading = 0
	self.compassListeners = {}

end

function InputDevice:getSensor( name )
	local dev = MOAIInputMgr[ self.inputDeviceName ]
	if dev then
		local sensor = dev[name]
		if not sensor then
			_stat( 'no input sensor found:', self.inputDeviceName, name  )
			-- _warn( 'no input sensor found:', self.inputDeviceName, name  )
		end
		return sensor
	else
		_error( 'no input device found:', self.inputDeviceName )
		return nil
	end
end

local clock = os.clock
function InputDevice:getTime()
	if self._getTime then
		return self._getTime()
	end
	return clock()
end



-----Common Control

function InputDevice:disable()
	self.enabled=false
end

function InputDevice:enable()
	self.enabled=true
end

function InputDevice:isEnabled()
	return self.enabled
end



-------Touch Event Listener
function InputDevice:getTouchState( id )
	local s = self.touchStates[ id ]
	if not s then
		s = TouchState()		
		self.touchStates[ id ] = s
	end
	return s
end

function InputDevice:addTouchListener( func )
	self.touchListeners[ func ] = true
end

function InputDevice:removeTouchListener( func )
	self.touchListeners[ func ] = nil
end

function InputDevice:sendTouchEvent( evtype, idx, x, y, mockup )
	local touchState = self:getTouchState( idx )
	local t = self:getTime()

	if evtype == 'down' then
		touchState.down = true
		touchState.t0   = t
		touchState.x0   = x
		touchState.y0   = y
		touchState.x_b  = x
		touchState.y_b  = y
	elseif evtype == 'up' then
		touchState.down = false
		touchState.t1_b = touchState.t1
	else
		touchState.t1_b = touchState.t1
		touchState.x_b  = touchState.x
		touchState.y_b  = touchState.y
	end
	
	touchState.t1 = t
	touchState.x = x
	touchState.y = y
	for func in pairs( self.touchListeners ) do
		func( evtype, touchState, x, y, mockup )
	end
end

function InputDevice:initTouchEventHandler()
	for i = 0, 16 do
		self:getTouchState( i ) --prebuild touch states
	end

	local sensor = self:getSensor( 'touch' )
	if not sensor then return end

	local TOUCH_DOWN   = MOAITouchSensor. TOUCH_DOWN
	local TOUCH_UP     = MOAITouchSensor. TOUCH_UP
	local TOUCH_MOVE   = MOAITouchSensor. TOUCH_MOVE
	local TOUCH_CANCEL = MOAITouchSensor. TOUCH_CANCEL

	local function onTouchEvent ( eventType, idx, x, y, tapCount )
		if not self.enabled then return end
		if eventType == TOUCH_DOWN then
			self:sendTouchEvent( 'down', idx, x, y, false )
		elseif eventType == TOUCH_UP then
			self:sendTouchEvent( 'up',   idx, x, y, false )
		elseif eventType == TOUCH_MOVE then				
			self:sendTouchEvent( 'move', idx, x, y, false )
		elseif eventType == TOUCH_CANCEL then
			self:sendTouchEvent( 'cancel' )
		end
	end

	sensor:setCallback( onTouchEvent )

end


-------Mouse Event Listener
function InputDevice:isMouseDown( btn )
	return self.mouseState[ btn ]
end

function InputDevice:isMouseUp( btn )
	return not self.mouseState[ btn ]
end

function InputDevice:pollMouseHit( btn )
	local mouseState = self.mouseState
	if btn == 'left' then
		local count = mouseState.leftHit
		mouseState.leftHit = 0
		return count
	elseif btn == 'right' then
		local count = mouseState.rightHit
		mouseState.leftHit = 0
		return count
	elseif btn == 'middle' then
		local count = mouseState.middleHit
		mouseState.leftHit = 0
		return count
	end
	return 0 
end

function InputDevice:getMouseLoc()
	local mouseState = self.mouseState
	return mouseState.x, mouseState.y
end

function InputDevice:getMouseDelta()
	local mouseState = self.mouseState
	return mouseState.dx, mouseState.dy
end

function InputDevice:addMouseListener( func )
	self.mouseListeners[func] = true
end

function InputDevice:removeMouseListener( func )
	self.mouseListeners[func] = nil
end

function InputDevice:setMouseRandomness( func )
	self.mouseRandomness = func or false
end

function InputDevice:sendMouseEvent( evtype, x, y, btn, mockup )
	local mouseState = self.mouseState
	if evtype == 'down' then
		mouseState[ btn ] = true
	elseif evtype == 'up' then
		mouseState[ btn ] = false
	elseif evtype == 'move' then
		mouseState.dx = x - mouseState.x
		mouseState.dy = y - mouseState.y
		mouseState.x = x
		mouseState.y = y
	end

	for func in pairs( self.mouseListeners ) do
		func( evtype, x, y, btn, mockup )
	end

	if self.allowTouchSimulation then
		local simTouchIdLeft  = 1
		local simTouchIdRight = 2
		if evtype == 'move' then
			if self.mouseState.left then				
				self:sendTouchEvent( 'move', simTouchIdLeft, x, y, mockup )
			end
			if self.mouseState.right then				
				return self:sendTouchEvent( 'move', simTouchIdRight, x, y, mockup )
			end
		else
			if btn == 'left' then
				return self:sendTouchEvent( evtype, simTouchIdLeft,  x, y, mockup )
			elseif btn == 'right' then
				return self:sendTouchEvent( evtype, simTouchIdRight, x, y, mockup )
			end
		end
	end
end

function InputDevice:initMouseEventHandler()
	local pointerSensor = self:getSensor( 'pointer' )
	if pointerSensor then		
		pointerSensor:setCallback(
			function( x, y )
				if not self.enabled then return end
				return self:sendMouseEvent( 'move', x, y, false, false)
			end)
		_stat( 'pointer sensor callback ready' )
	end

	local function setupMouseButtonCallback( sensorName, btnName )
		local buttonSensor = self:getSensor( sensorName )
		if buttonSensor then
			buttonSensor:setCallback ( 
				function( down )
					local mouseState = self.mouseState
					if not self.enabled then return end
					local x, y = mouseState.x, mouseState.y
					local ev = down and 'down' or 'up'
					return self:sendMouseEvent( ev, x, y, btnName, false )
				end 
			)
			_stat( 'mouse button sensor callback ready' )
		end
	end

	setupMouseButtonCallback( 'mouseLeft',   'left' )
	setupMouseButtonCallback( 'mouseRight',  'right' )
	setupMouseButtonCallback( 'mouseMiddle', 'middle' )

end



-------Keyboard Event Listener

function InputDevice:isKeyDown(key)
	local state = self.keyStates[ key ]
	return state and state.down
end

function InputDevice:isKeyUp(key)
	local state = self.keyStates[ key ]
	return state and ( not state.down )
end


function InputDevice:pollKeyHit(key) --get key hit counts since last polling
	local keyStates = self.keyStates

	local state = keyStates[ key ]
	if not state then return 0 end
	local count = keyStates[ key ].hit
	keyStates[ key ].hit = 0
	return count
end


function InputDevice:addKeyboardListener( func )
	self.keyboardListeners[ func ] = true
end

function InputDevice:removeKeyboardListener( func )
	self.keyboardListeners[ func ] = nil
end

function InputDevice:sendKeyEvent( key, down, mockup )
	local state = self.keyStates[ key ]
	if not state then
		state = { down = false, hit = 0 }
		self.keyStates[ key ] = state
	end
	state.down = down
	state.hit  = state.hit + 1
	for func in pairs( self.keyboardListeners ) do
		func( key, down, mockup )
	end
end

function InputDevice:initKeyboardEventHandler()
	local keyStates = self.keyStates
	local keyCodeMap = getKeyMap()
	local keyNames   = {}
	for k,v in pairs( keyCodeMap ) do --precreate key states
		keyNames[ v ] = k
		keyStates[ k ] = { down = false, hit = 0 }
	end
	local sensor = self:getSensor( 'keyboard' )
	if not sensor then return end
	local function onKeyboardEvent ( key, down )
		if not self.enabled then return end
		local name = keyNames[key] or key
		return self:sendKeyEvent( name, down, false )
	end
	
	sensor:setCallback( onKeyboardEvent )
end



-------JOYSTICK Event Listener

function InputDevice:addJoystickListener( func )
	self.joystickListeners[func] = true
end

function InputDevice:removeJoystickListener( func )
	self.joystickListeners[func] = nil
end

local maxJoystickCount       = 4
local maxJoystickAxisCount   = 6
function InputDevice:sendJoystickEvent( evtype, joyId, btn, axisId, value, mockup )
	for func in pairs( self.joystickListeners ) do
		func( evtype, joyId, btn, axisId, value, mockup )
	end
end

function InputDevice:initJoystickEventHandler()
	--create listener for each set of joystick sensors( button + axis )
	for joyId = 1, maxJoystickCount do

		local joyName = 'joy-'..joyId
		
		--buttons
		local buttonSensorName = joyName..'.button'
		local joyButtonSensor = self:getSensor( buttonSensorName )
		if joyButtonSensor then
			-- print( 'foundJoyButtonSensor', buttonSensorName )
			local function onJoyButtonEvent( key, down )
				if not self.enabled then return end
				if down then
					return self:sendJoystickEvent( 'down', joyId, key )
				else
					return self:sendJoystickEvent( 'up', joyId, key )
				end
			end
			joyButtonSensor:setCallback( onJoyButtonEvent )
		end
		
		--axis
		for axisId = 1, maxJoystickAxisCount do
			local axisSensorName = joyName .. '.axis-'..axisId
			local joyAxisSensor = self:getSensor( axisSensorName )
			if joyAxisSensor then
				local function onJoyAxisEvent( value )
					if not self.enabled then return end
					return self:sendJoystickEvent( 'axis', joyId, nil, axisId, value )
				end
				joyAxisSensor:setCallback( onJoyAxisEvent )
			end
		end

	end

end

-------Acceleratemeter Event Listener
function InputDevice:setMotionAccuracy(f)
	self.motionAccuracy = 10^(-f)
end

function InputDevice:addMotionListener(func)
	self.motionListeners[func] = true
end

function InputDevice:removeMotionListener(func)
	self.motionListeners[func] = nil
end

local floor=math.floor
local function reduceAccuracy( v ,motionAccuracy )
	return floor(v*1000000*motionAccuracy)/motionAccuracy/1000000
end

function InputDevice:sendMotionEvent(x,y,z)
	local acc = self.motionAccuracy
	local x, y, z = 
		reduceAccuracy( x, acc ), reduceAccuracy( y, acc ), reduceAccuracy( z, acc )
	local state = self.motionState
	for listener in pairs( self.motionListeners ) do
		listener( x, y, z )
	end
	if state.x~=x or state.y~=y or state.z~=z then
		state.x = x
		state.y = y
		state.z = z
	end
end

function InputDevice:initMotionEventHandler()
	self:setMotionAccuracy(2)
	--TODO
end


---Accelerometer
function InputDevice:getAccelerometerData()
	if self.level then
		return self.level:getLevel()
	end
	return 0,0,0
end	
-- 
function InputDevice:initAccelerometerEventHandler()
	--TODO
	self.level = self:getSensor( 'level' )
	-- if self.level then
	-- 	self.level:setCallback( onMotionEvent )
	-- end
end

---Accelerometer
function InputDevice:getGyroscopeData()
	if self.gyroscope then
		return self.gyroscope:getLevel()
	end
	return 0,0,0
end	
-- 
function InputDevice:initGyroscopeEventHandler()
	--TODO
	self.gyroscope = self:getSensor( 'gyroscope' )
	-- if self.gyroscope then
	-- 	self.gyroscope:setCallback( onMotionEvent )
	-- end
end


----Compass
function InputDevice:addCompassListener( func )
	self.compassListeners[ func ] = true
end

function InputDevice:removeCompassListener( func )
	self.compassListeners[ func ] = nil
end

function InputDevice:sendCompassEvent( heading, mockup )
	self.compassHeading = compassHeading
	for func in pairs( self.compassListeners ) do
		func( heading, mockup )
	end
end

function InputDevice:getCompassHeading()
	return self.compassHeading
end

function InputDevice:initCompassEventHandler()
	local sensor = self:getSensor('compass')
	if not sensor then return end
	sensor:setCallback( function( heading )
		return self:sendCompassEvent( heading )
	end)
end 



----Location
function InputDevice:getLocation()
	local sensor = self:getSensor('location')
	if not sensor then return nil end
	local lng, lat, ha, alt, va, speed = sensor:getLocation()
	return {
		longitude = lng,
		latitude  = lat,
		haccuracy = ha,
		altitude  = alt,
		vaccuracy = va,
		speed     = speed
	}
end



------------Expose Event Sender for input mockup
_sendTouchEvent     = sendTouchEvent
_sendMouseEvent     = sendMouseEvent
_sendKeyEvent       = sendKeyEvent
_sendMotionEvent    = sendMotionEvent
_sendJoystickEvent  = sendJoystickEvent
_sendLevelEvent     = sendLevelEvent


-----------ENTRY
function InputDevice:init()
	if self.virtual then return end

	local device = MOAIInputMgr[ self.inputDeviceName ]
	if not device then
		_error( 'no input device:', self.inputDeviceName )
	end
	self:initTouchEventHandler    ()
	self:initKeyboardEventHandler ()
	self:initMouseEventHandler    ()
	-- TODO: implement belows
	self:initJoystickEventHandler ()
	-- self:initMotionEventHandler   ()
	self:initAccelerometerEventHandler    ()
	self:initGyroscopeEventHandler    ()
	self:initCompassEventHandler  ()
end



--------------------------------------------------------------------
---default input manager
--------------------------------------------------------------------

local _defaultInputDevice = InputDevice( 'device' )

function getDefaultInputDevice()
	return _defaultInputDevice
end

function initDefaultInputEventHandlers()
	return _defaultInputDevice:init()
end


function disableUserInput()
	_defaultInputDevice:disable()
end

function enableUserInput()
	_defaultInputDevice:enable()	
end

function isUserInputEnabled()
	return _defaultInputDevice:isEnabled()
end

---touch
function getTouchState(id)
	return _defaultInputDevice:getTouchState( id )
end

function addTouchListener( func )
	_defaultInputDevice:addTouchListener( func )
end

function removeTouchListener( func )
	_defaultInputDevice:removeTouchListener( func )
end

--mouse
function isMouseDown( btn )
	return _defaultInputDevice:isMouseDown( btn )
end

function isMouseUp( btn )
	return _defaultInputDevice:isMouseUp( btn )
end

function pollMouseHit( btn )
	return _defaultInputDevice:pollMouseHit( btn )
end

function getMouseLoc()
	return _defaultInputDevice:getMouseLoc()
end

function getMouseDelta()
	return _defaultInputDevice:getMouseDelta()
end

function addMouseListener( func )
	return _defaultInputDevice:addMouseListener( func )
end

function removeMouseListener( func )
	return _defaultInputDevice:removeMouseListener( func )
end

function setMouseRandomness( f )
	return _defaultInputDevice:setMouseRandomness( f )
end

---KEY

function isKeyDown(key)
	return _defaultInputDevice:isKeyDown(key)	
end

function isKeyUp(key)
	return _defaultInputDevice:isKeyUp(key)	
end

function pollKeyHit(key) --get key hit counts since last polling
	return _defaultInputDevice:pollKeyHit(key)	
end

function addKeyboardListener( func )
	return _defaultInputDevice:addKeyboardListener( func )
end

function removeKeyboardListener( func )
	return _defaultInputDevice:removeKeyboardListener( func )
end

--JOYSTICK

--ACCELEROMETER
function getAccelerometerData()
	return _defaultInputDevice:getAccelerometerData()
end

--GYROSCOPE
function getGyroscopeData()
	return _defaultInputDevice:getGyroscopeData()
end


--COMPASS
function addCompassListener( func )
	return _defaultInputDevice:addCompassListener( func )
end

function removeCompassListener( func )
	return _defaultInputDevice:removeCompassListener( func )
end

function getCompassHeading()
	return _defaultInputDevice:getCompassHeading()
end

--LOCATION
function getLocation()
	return _defaultInputDevice:getLocation()
end

----FAKE INPUT
function _sendTouchEvent( ... )
	return _defaultInputDevice:sendTouchEvent( ... )
end
function _sendMouseEvent( ... )
	return _defaultInputDevice:sendMouseEvent( ... )
end
function _sendKeyEvent( ... )
	return _defaultInputDevice:sendKeyEvent( ... )
end
function _sendJoystickEvent( ... )
	return _defaultInputDevice:sendJoystickEvent( ... )
end
function _sendMotionEvent( ... )
	return _defaultInputDevice:sendMotionEvent( ... )
end
function _sendLevelEvent( ... )
	return _defaultInputDevice:sendLevelEvent( ... )
end
