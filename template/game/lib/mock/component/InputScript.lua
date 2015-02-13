module 'mock'
CLASS: InputScript ()

--[[
	each InputScript will hold a listener to responding input sensor
	filter [ mouse, keyboard, touch, joystick ]
]]

function InputScript:__init( option )
	self.option = option
end

function InputScript:onAttach( entity )
	installInputListener( entity, self.option )
end

function InputScript:onDetach( entity )
	uninstallInputListener( entity )
end

function InputScript:getInputDevice()
	return self.inputDevice
end
