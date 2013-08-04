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

CLASS: InputDevice()
function InputDevice:__init( deviceName )
	self.inputDeviceName = assert( deviceName )
	_inputDevices[ deviceName ] = self
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
		--button states
		left      = false,
		right     = false,
		middle    = false,
		leftHit   = 0,
		rightHit  = 0,
		middleHit = 0,
	}

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
		return dev[name]
	else
		_error( 'no input device found:', self.inputDeviceName )
		return nil
	end
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
		s = {
			id   = id,
			down = false,
			x = 0,
			y = 0
		}
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

local function sendTouchEvent( evtype, id, x, y, mockup )
	for func in pairs( self.touchListeners ) do
		func( evtype, id, x, y, mockup )
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
		local touchState = self:getTouchState( idx )
		touchState.x = x
		touchState.y = y

		if eventType == TOUCH_DOWN then
			touchState.down = true
			self:sendTouchEvent( 'down', idx, x, y, false )
		elseif eventType == TOUCH_UP then
			touchState.down = false
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
	for func in pairs( self.mouseListeners ) do
		func( evtype, x, y, btn, mockup )
	end
	if allowTouchSimulation then
		local down = self.mouseState.left
		local simTouchId = 1
		if evtype == 'move' then
			if down then
				return sendTouchEvent( 'move', simTouchId, x, y, mockup )
			end
		elseif evtype == 'down' and btn == 'left' then
			return sendTouchEvent( 'down', simTouchId, x, y, mockup )
		elseif evtype == 'up' and btn == 'left' then
			return sendTouchEvent( 'up'  , simTouchId, x, y, mockup )
		end
	end
end

function InputDevice:initMouseEventHandler()
	local pointerSensor = self:getSensor( 'pointer' )
	if pointerSensor then
		pointerSensor:setCallback(
			function( x, y )
				if not self.enabled then return end
				local mouseState = self.mouseState
				mouseState.x, mouseState.y = x, y
				return self:sendMouseEvent( 'move', x, y, false, false)
			end)
	end

	local function setupMouseButtonCallback( sensorName, btnName )
		local buttonSensor = self:getSensor( sensorName )
		if buttonSensor then
			buttonSensor:setCallback ( 
				function( down )
					local mouseState = self.mouseState
					if not self.enabled then return end
					mouseState[ btnName ] = down
					local x, y = mouseState.x, mouseState.y
					local ev = down and 'down' or 'up'
					return self:sendMouseEvent( ev, x, y, btnName, false )
				end 
			)
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
	if state then 
		state.down = down
		state.hit  = state.hit + 1
	end
	for func in pairs( self.keyboardListeners ) do
		func( key, down, mockup )
	end
end

function InputDevice:initKeyboardEventHandler()
	local keyStates = self.keyStates
	local keyCodeMap = getKeyMap()
	local keyNames   = {}
	for k,v in pairs( keyCodeMap ) do
		keyNames[ v ] = k
		keyStates[ k ] = { down = false, hit = 0 }
	end
	local sensor = self:getSensor( 'keyboard' )
	if not sensor then return end
	local function onKeyboardEvent ( key, down )
		if not self.enabled then return end
		local name = keyNames[key] or key
		return sendKeyEvent( name, down, false )
	end
	
	sensor:setCallback( onKeyboardEvent )
end

-------JOYSTICK Event Listener
function InputDevice:sendJoystickEvent( ev, x, y, z )
	--TODO:
end

function InputDevice:initJoystickEventHandler()
	--TODO:
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

---Gyrosopce
function InputDevice:getLevelData()
	if level then
		return level:getLevel()
	end
end	
-- 
function InputDevice:initLevelEventHandler()
	--TODO
	local level = self:getSensor( 'level' )
	if level then
		MOAIInputMgr.device.level:setCallback( onMotionEvent )
	end
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
	sensor:setCallBack( function( heading )
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
_sendTouchEvent  = sendTouchEvent
_sendMouseEvent  = sendMouseEvent
_sendKeyEvent    = sendKeyEvent
_sendMotionEvent = sendMotionEvent
_sendLevelEvent  = sendLevelEvent


-----------ENTRY
function InputDevice:init()
	self:initTouchEventHandler    ()
	self:initKeyboardEventHandler ()
	self:initMouseEventHandler    ()
	-- TODO: implement belows
	self:initJoystickEventHandler ()
	-- self:initMotionEventHandler   ()
	self:initLevelEventHandler    ()
	self:initCompassEventHandler  ()
end

--------------------------------------------------------------------
---default input manager
--------------------------------------------------------------------

_defaultInputManger = InputDevice( 'device' )

function initDefaultInputEventHandlers()
	return _defaultInputManger:init()
end


function disableUserInput()
	_defaultInputManger:disable()
end

function enableUserInput()
	_defaultInputManger:enable()	
end

function isUserInputEnabled()
	return _defaultInputManger:isEnabled()
end

---touch
function getTouchState(id)
	return _defaultInputManger:getTouchState( id )
end

function addTouchListener( func )
	_defaultInputManger:addTouchListener( func )
end

function removeTouchListener( func )
	_defaultInputManger:removeTouchListener( func )
end

--mouse
function isMouseDown( btn )
	return _defaultInputManger:isMouseDown( btn )
end

function isMouseUp( btn )
	return _defaultInputManger:isMouseUp( btn )
end

function pollMouseHit( btn )
	return _defaultInputManger:pollMouseHit( btn )
end

function getMouseLoc()
	return _defaultInputManger:getMouseLoc()
end

function addMouseListener( func )
	return _defaultInputManger:addMouseListener( func )
end

function removeMouseListener( func )
	return _defaultInputManger:removeMouseListener( func )
end

function setMouseRandomness( f )
	return _defaultInputManger:setMouseRandomness( f )
end

---KEY

function isKeyDown(key)
	return _defaultInputManger:isKeyDown(key)	
end

function isKeyUp(key)
	return _defaultInputManger:isKeyUp(key)	
end

function pollKeyHit(key) --get key hit counts since last polling
	return _defaultInputManger:pollKeyHit(key)	
end

function addKeyboardListener( func )
	return _defaultInputManger:addKeyboardListener( func )
end

function removeKeyboardListener( func )
	return _defaultInputManger:removeKeyboardListener( func )
end

--JOYSTICK

--MOTION
--GYROSCOPE

--COMPASS
function addCompassListener( func )
	return _defaultInputManger:addCompassListener( func )
end

function removeCompassListener( func )
	return _defaultInputManger:removeCompassListener( func )
end

function getCompassHeading()
	return _defaultInputManger:getCompassHeading()
end

--LOCATION
function getLocation()
	return _defaultInputManger:getLocation()
end

----FAKE INPUT
function _sendTouchEvent( ... )
	return _defaultInputManger:sendTouchEvent( ... )
end
function _sendMouseEvent( ... )
	return _defaultInputManger:sendMouseEvent( ... )
end
function _sendKeyEvent( ... )
	return _defaultInputManger:sendKeyEvent( ... )
end
function _sendJoystickEvent( ... )
	return _defaultInputManger:sendJoystickEvent( ... )
end
function _sendMotionEvent( ... )
	return _defaultInputManger:sendMotionEvent( ... )
end
function _sendLevelEvent( ... )
	return _defaultInputManger:sendLevelEvent( ... )
end
