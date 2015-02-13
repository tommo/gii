module 'mock'

EnumOrientation = _ENUM_V {
	'portrait' ,
	'landscape',
}

--------------------------------------------------------------------
CLASS: ScreenProfile ()
	:MODEL{
		Field 'name' :string();
		'----';
		Field 'width'  :int();
		Field 'height' :int();
		Field 'dpi'    :int();
		Field 'orientation' :enum( EnumOrientation );
	}

function ScreenProfile:__init()
	self.name   = 'screen-profile'
	self.width  = 960
	self.height = 640
	self.orientation = 'portrait'
	self.dpi    = 96
end

function ScreenProfile:toString()
	return string.format( '<%s> %d*%d@%s dpi:%d', 
		self.name, 
		self.width, self.height, self.orientation, 
		self.dpi
	)
end

function ScreenProfile:getDimString()
	return string.format( '%d*%d', self.width, self.height )
end

--------------------------------------------------------------------
--registery
--------------------------------------------------------------------
local _screenProfileRegistry = {}
function getScreenProfileRegistry()
	return _screenProfileRegistry
end

function registerScreenProfile( p )	
	table.insert( _screenProfileRegistry, p )
end

function unregisterScreenProfile( p )
	local idx = table.index( _screenProfileRegistry, p )
	if idx then table.remove( _screenProfileRegistry, idx ) end
end

--------------------------------------------------------------------
--Builtin profiles
--------------------------------------------------------------------
registerScreenProfile( ScreenProfile:rawInstance{
		name   = 'iPhone',
		width  = 640;
		height = 960;
		dpi    = 120;
		orientation = 'portrait'
	} )
