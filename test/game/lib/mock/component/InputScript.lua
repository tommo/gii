module 'mock'
CLASS: InputScript ()

--[[
	each InputScript will hold a listener to responding input sensor
	filter [ mouse, keyboard, touch, joystick ]
]]

function InputScript:__init( option )
	--todo:Active control
	self.acceptMockUpInput = true
	if option then
		if option.acceptMockUpInput == false then
			self.acceptMockUpInput = false
		end
	end
end

function InputScript:onAttach( entity )
	local refuseMockUpInput = not self.acceptMockUpInput
	local option = self.option
	----link callbacks
	self.mouseCallback    = false
	self.keyboardCallback = false
	self.touchCallback    = false
	self.joystickCallback = false

	----MouseEvent
	local onMouseEvent = entity.onMouseEvent
	local onMouseDown  = entity.onMouseDown
	local onMouseUp    = entity.onMouseUp
	local onMouseMove  = entity.onMouseMove
	if onMouseDown or onMouseUp or onMouseMove or onMouseEvent then
		self.mouseCallback = function( ev, x, y, btn, mock )
			if mock and refuseMockUpInput then return end
			if ev == 'move' then
				if onMouseMove then onMouseMove( entity, x, y, mock ) end
			elseif ev == 'down' then
				if onMouseDown then onMouseDown( entity, btn, x, y, mock ) end
			elseif ev == 'up' then
				if onMouseUp   then onMouseUp  ( entity, btn, x, y, mock ) end
			end
			if onMouseEvent then
				return onMouseEvent( entity, ev, x, y, btn, mock )
			end
		end
		addMouseListener( self.mouseCallback )
	end

	----TouchEvent
	local onTouchEvent  = entity.onTouchEvent  
	local onTouchDown   = entity.onTouchDown
	local onTouchUp     = entity.onTouchUp
	local onTouchMove   = entity.onTouchMove
	local onTouchCancel = entity.onTouchCancel
	if onTouchDown or onTouchUp or onTouchMove or onTouchEvent then
		self.TouchCallback = function( ev, id, x, y, mock )
			if mock and refuseMockUpInput then return end
			if ev == 'drag' then
				if onTouchMove   then onTouchMove( entity, x, y, mock ) end
			elseif ev == 'down' then
				if onTouchDown   then onTouchDown( entity, id, x, y, mock ) end
			elseif ev == 'up' then
				if onTouchUp     then onTouchUp  ( entity, id, x, y, mock ) end
			elseif ev == 'cancel' then
				if onTouchCancel then onTouchCancel( entity ) end
			end
			if onTouchEvent then
				return onTouchEvent( entity, ev, id, x, y, mock )
			end
		end
		addTouchListener( self.TouchCallback )
	end

	----KeyEvent
	local onKeyEvent = entity.onKeyEvent
	local onKeyDown  = entity.onKeyDown
	local onKeyUp    = entity.onKeyUp
	if onKeyDown or onKeyUp or onKeyEvent then
		self.keyboardCallback = function( key, down, mock )
			if mock and refuseMockUpInput then return end
			if down then
				if onKeyDown then onKeyDown( entity, key, mock ) end
			else
				if onKeyUp   then onKeyUp  ( entity, key, mock ) end
			end
			if onKeyEvent then
				return onKeyEvent( entity, key, down, mock )
			end
		end
		addKeyboardListener( self.keyboardCallback )
	end
	
	---JOYSTICK EVNET
	--TODO:...
end

function InputScript:onDetach( entity )
	if self.mouseCallback then
		removeMouseListener( self.mouseCallback )
	end

	if self.keyboardCallback then
		removeKeyboardListener( self.keyboardCallback )
	end

	if self.touchCallback then
		removeTouchListener( self.touchCallback )
	end

	if self.joystickCallback then
		removeJoystickListener( self.joystickCallback )
	end

	self.mouseCallback    = false
	self.keyboardCallback = false
	self.touchCallback    = false
	self.joystickCallback = false
end



--[[
	input event format:
		KeyDown     ( keyname )
		KeyUp       ( keyname )

		MouseMove   ( x, y )
		MouseDown   ( btn, x, y )
		MouseUp     ( btn, x, y )

		RawMouseMove   ( id, x, y )        ---many mouse (??)
		RawMouseDown   ( id, btn, x, y )   ---many mouse (??)
		RawMouseUp     ( id, btn, x, y )   ---many mouse (??)
		
		TouchDown   ( id, x, y )
		TouchUp     ( id, x, y )
		TouchMove   ( id, x, y )
		TouchCancel (          )
		
		JoystickMove( id, x, y )
		JoystickDown( btn )
		JoystickUp  ( btn )

		LEVEL:   get from service
		COMPASS: get from service
]]
