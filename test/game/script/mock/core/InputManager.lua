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

----------States
local inputDeviceName = 'device'

local allowTouchSimulation = true

local touchCount  = 16
local touches     = {}
local touchStates    = {}

local keyStates   = {}

local mouseState  = {
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

-----Common Control
local userInputEnabled = true

function disableUserInput()
	userInputEnabled=false
end

function enableUserInput()
	userInputEnabled=true
end

function isUserInputEnabled()
	return userInputEnabled
end

-------Touch Event Listener

function getTouchState(id)
	local s = touchStates[ id ]
	if not s then
		s = {
			id   = id,
			down = false,
			x = 0,
			y = 0
		}
		touchStates[ id ] = s
	end
	return s
end

for i = 0, 16 do
	getTouchState( i )
end

local touchListeners={}
function addTouchListener( func )
	touchListeners[ func ] = true
end

function removeTouchListener( func )
	touchListeners[ func ] = nil
end

local function sendTouchEvent( evtype, id, x, y, mockup )
	for func in pairs( touchListeners ) do
		func( evtype, id, x, y, mockup )
	end
end

function initTouchEventHandler()
	local sensor = MOAIInputMgr[ inputDeviceName ][ 'touch' ]
	if not sensor then return end

	local TOUCH_DOWN   = MOAITouchSensor. TOUCH_DOWN
	local TOUCH_UP     = MOAITouchSensor. TOUCH_UP
	local TOUCH_MOVE   = MOAITouchSensor. TOUCH_MOVE
	local TOUCH_CANCEL = MOAITouchSensor. TOUCH_CANCEL

	local function onTouchEvent ( eventType, idx, x, y, tapCount )
		if not userInputEnabled then return end
		local touchState = getTouchState( idx )
		touchState.x = x
		touchState.y = y

		if eventType == TOUCH_DOWN then
			touchState.down = true
			sendTouchEvent( 'down', idx, x, y, false )
		elseif eventType == TOUCH_UP then
			touchState.down = false
			sendTouchEvent( 'up',   idx, x, y, false )
		elseif eventType == TOUCH_MOVE then				
			sendTouchEvent( 'move', idx, x, y, false )
		elseif eventType == TOUCH_CANCEL then
			sendTouchEvent( 'cancel' )
		end
	end

	sensor:setCallback( onTouchEvent )

end

-------Mouse Event Listener
function isMouseDown( btn )
	return mouseState[ btn ]
end

function isMouseUp( btn )
	return not mouseState[ btn ]
end

function pollMouseHit( btn )
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


function getMouseLoc()
	return mouseState.x, mouseState.y
end

local mouseListeners={}
function addMouseListener( func )
	mouseListeners[func] = true
end

function removeMouseListener( func )
	mouseListeners[func] = nil
end

local mouseRandomness = false
function setMouseRandomness( func )
	mouseRandomness = func or false
end

local function sendMouseEvent( evtype, x, y, btn, mockup )
	for func in pairs(mouseListeners) do
		func( evtype, x, y, btn, mockup )
	end
	if allowTouchSimulation then
		local down = mouseState.left		
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

function initMouseEventHandler()
	local pointerSensor = MOAIInputMgr[ inputDeviceName ][ 'pointer' ]
	if pointerSensor then
		pointerSensor:setCallback(
			function( x, y )
				if not userInputEnabled then return end
				mouseState.x, mouseState.y = x, y
				return sendMouseEvent( 'move', x, y, false, false)
			end)
	end

	local function setupMouseButtonCallback( sensorName, btnName )
		local buttonSensor = MOAIInputMgr[ inputDeviceName ][ sensorName ]
		if buttonSensor then
			buttonSensor:setCallback ( 
				function( down ) 
					if not userInputEnabled then return end
					mouseState[ btnName ] = down
					local x, y = mouseState.x, mouseState.y
					local ev = down and 'down' or 'up'
					return sendMouseEvent( ev, x, y, btnName, false )
				end 
			)
		end
	end

	setupMouseButtonCallback( 'mouseLeft',   'left' )
	setupMouseButtonCallback( 'mouseRight',  'right' )
	setupMouseButtonCallback( 'mouseMiddle', 'middle' )

end


-------Keyboard Event Listener
local keyCodeMap = getKeyMap()
local keyNames   = {}
for k,v in pairs( keyCodeMap ) do
	keyNames[ v ] = k
	keyStates[ k ] = { down = false, hit = 0 }
end

function isKeyDown(key)
	local state = keyStates[ key ]
	return state and state.down
end

function isKeyUp(key)
	local state = keyStates[ key ]
	return state and ( not state.down )
end


function pollKeyHit(key) --get key hit counts since last polling
	local state = keyStates[ key ]
	if not state then return 0 end

	local count = keyStates[ key ].hit
	keyStates[ key ].hit = 0
	return count
end

local keyboardListeners={}

function addKeyboardListener( func )
	keyboardListeners[ func ] = true
end

function removeKeyboardListener( func )
	keyboardListeners[ func ] = nil
end

local function sendKeyEvent( key, down, mockup )
	local state = keyStates[ key ]
	if state then 
		state.down = down
		state.hit  = state.hit + 1
	end
	for func in pairs(keyboardListeners) do
		func( key, down, mockup )
	end
end

function initKeyboardEventHandler()
	local sensor = MOAIInputMgr[ inputDeviceName ][ 'keyboard' ]
	if not sensor then return end

	local function onKeyboardEvent ( key, down )
		if not userInputEnabled then return end
		local name= keyNames[key] or key
		return sendKeyEvent( name, down, false )
	end
	
	sensor:setCallback( onKeyboardEvent )
end

-------JOYSTICK Event Listener
function initJoystickEventHandler()
	--TODO
end

-------Acceleratemeter Event Listener
local motionAccuracy=1
local lx,ly,lz

local floor=math.floor
local function reduceAccuracy(v)
	return floor(v*1000000*motionAccuracy)/motionAccuracy/1000000
end

function setMotionAccuracy(f)
	motionAccuracy=10^(-f)
end


local motionListeners={}
function addMotionListener(func)
	motionListeners[func]=true
end

function removeMotionListener(func)
	motionListeners[func]=nil
end

local function sendMotionEvent(x,y,z)
	x,y,z=reduceAccuracy(x),reduceAccuracy(y),reduceAccuracy(z)
	if lx~=x or ly~=y or lz~=z then
		lx=x
		ly=y
		lz=z
		for listener in pairs(motionListeners) do
			listener(x,y,z)
		end
	end
end

local function onMotionEvent(...)
	return sendMotionEvent(...)
end

function initMotionEventHandler()
	setMotionAccuracy(2)
	--TODO
end

-------Level Event Listener
function getLevelData()
	if level then
		return level:getLevel()
	end
end	

function initLevelEventHandler()
	--TODO
	local level = MOAIInputMgr.device.level

	if level then
		MOAIInputMgr.device.level:setCallback(onMotionEvent)
	end

end


------------Expose Event Sender for input mockup
_sendTouchEvent  = sendTouchEvent
_sendMouseEvent  = sendMouseEvent
_sendKeyEvent    = sendKeyEvent
_sendMotionEvent = sendMotionEvent
_sendLevelEvent  = sendLevelEvent


-----------ENTRY
function initInputEventHandlers()
	initTouchEventHandler    ()
	initKeyboardEventHandler ()
	initMouseEventHandler    ()
	-- TODO: implement belows
	initJoystickEventHandler ()
	initMotionEventHandler   ()
	initLevelEventHandler    ()
end
