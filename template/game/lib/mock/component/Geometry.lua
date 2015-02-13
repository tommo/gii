module 'mock'

local draw = MOAIDraw
local gfx  = MOAIGfxDevice

--------------------------------------------------------------------
CLASS: GeometryComponent( DrawScript )
	:MODEL{
		Field 'blend'  :enum( EnumBlendMode ) :getset('Blend');		
	}
function GeometryComponent:__init()
	self.color = {1,1,1,1}
end

function GeometryComponent:applyColor()
	local ent = self._entity
	if ent then
		-- gfx.setPenColor( ent:getColor() )
	end
end

function GeometryComponent:getBlend()
	return self.blend
end

function GeometryComponent:setBlend( b )
	self.blend = b	
	setPropBlend( self.prop, b )
end


--------------------------------------------------------------------

CLASS: GeometryRect ( GeometryComponent )
	:MODEL{
		Field 'w';
		Field 'h';
		Field 'fill'  :boolean()
	}
registerComponent( 'GeometryRect', GeometryRect )

function GeometryRect:__init()
	self.w = 100
	self.h = 100
	self.fill = false
end

function GeometryRect:onDraw()
	self:applyColor()
	local w,h = self.w, self.h
	if self.fill then
		draw.fillRect( -w/2,-h/2, w/2,h/2 )
	else
		draw.drawRect( -w/2,-h/2, w/2,h/2 )
	end
end

function GeometryRect:onGetRect()
	local w,h = self.w, self.h
	return -w/2,-h/2, w/2,h/2
end

--------------------------------------------------------------------
CLASS: GeometryCircle ( GeometryComponent )
	:MODEL{
		Field 'radius';
		Field 'fill' :boolean()
	}
registerComponent( 'GeometryCircle', GeometryCircle )

function GeometryCircle:__init()
	self.radius = 100
	self.fill = false
end

function GeometryCircle:onDraw()
	self:applyColor()
	if self.fill then
		draw.fillCircle( 0,0, self.radius )
	else
		draw.drawCircle( 0,0, self.radius )
	end
end

function GeometryCircle:onGetRect()
	local r = self.radius
	return -r,-r, r,r
end
--------------------------------------------------------------------
CLASS: GeometryRay ( GeometryComponent )
	:MODEL{
		Field 'length';		
	}
registerComponent( 'GeometryRay', GeometryRay )

function GeometryRay:__init()
	self.length = 100
end

function GeometryRay:onDraw()
	self:applyColor()
	draw.fillRect( -2,-2, 2,2 )
	draw.drawLine( 0, 0, self.length, 0 )
end

function GeometryRay:onGetRect()
	local l = self.length
	return 0,0, l,1
end
