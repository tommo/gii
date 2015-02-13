module 'mock'

EnumScreenAnchorTypeV = _ENUM_V {
	'top',
	'center',
	'bottom',
}

EnumScreenAnchorTypeH = _ENUM_V {
	'left',
	'center',
	'right',
}

CLASS: ScreenAnchor ( Component )
	:MODEL{
		Field 'targetCamera' :type( Camera );
		Field 'alignH' :enum( EnumScreenAnchorTypeV );
		Field 'alignV' :enum( EnumScreenAnchorTypeH );
		Field 'offset' :type('vec2') :tuple_getset() :onset( 'updateLoc' );
	}

function ScreenAnchor:__init()
	self.targetCamera = false
	self.alignH = 'center'
	self.alignV = 'center'
	self.offset = { 0, 0 }
end

function ScreenAnchor:onAttach( ent )
	self:updateLoc()
end

function ScreenAnchor:updateLoc()
	local ent = self._entity
	local camera = self:getTargetCamera()
	local w, h = camera:getViewportSize()
	local ah, av = self.alignH, self.alignV
	local x, y
	x =  ( ah == 'left'  and -w/2 )
		or ( ah == 'right' and  w/2 )
		or 0
	y =  ( av == 'top'    and  h/2 )
		or ( av == 'bottom' and -h/2 )
		or 0
	local ox, oy = unpack( self.offset )
	ent:setWorldLoc( x + ox, y + oy )
	print( x, y, w,h, av, ah )
end

function ScreenAnchor:getTargetCamera()
	if self.targetCamera then return self.targetCamera end
end

function ScreenAnchor:drawGizmo()
end