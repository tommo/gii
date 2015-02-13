module 'mock'

CLASS: JoystickConfig ()
	:MODEL{}

function JoystickConfig:__init( data )
	local buttonIdToName = {}
	local buttonNameToId = {}
	for name, id in pairs( data.buttons ) do
		buttonIdToName[ id ] = name
		buttonNameToId[ name ] = id
	end
	self.buttonIdToName = buttonIdToName
	self.buttonNameToId = buttonNameToId
end

function JoystickConfig:getBtnName( id )
	return self.buttonIdToName[ id ] or nil
end

function JoystickConfig:getBtnId( name )
	return self.buttonNameToId[ name ] or nil
end

--------------------------------------------------------------------
JoystickConfigPS3 = JoystickConfig {
	buttons = {
		['select']   = 0   ;
		['L3'    ]   = 1   ;
		['R3'    ]   = 2   ;
		['start' ]   = 3   ;
		['up'    ]   = 4   ;
		['right' ]   = 5   ;
		['down'  ]   = 6   ;
		['left'  ]   = 7   ;
		['a'     ]   = 14  ;
		['b'     ]   = 13  ;
		['x'     ]   = 15  ;
		['y'     ]   = 12  ;
		['L1'    ]   = 10  ;
		['R1'    ]   = 11  ;
		['L2'    ]   = 8   ;
		['R2'    ]   = 9   ;
	}
}
