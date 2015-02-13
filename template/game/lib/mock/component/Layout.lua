module 'mock'

EnumLayoutAlignment  = _ENUM_V{
	'left',
	'center',
	'right',
}

EnumLayoutAlignmentV = _ENUM_V{
	'top',
	'center',
	'bottom',
}


EnumLayoutRelativeOriginH = _ENUM_V{
	'left',
	'right',
	'center'
}

EnumLayoutRelativeOriginV = _ENUM_V{
	'top',
	'right',
	'center'
}

EnumLayoutRelativeOrigin = _ENUM_V{
	'center';
	'top-left';
	'top-right';
	'top-center';
	'bottom-left';
	'bottom-right';
	'bottom-center';
	'middle-left';
	'middle-right';
}

EnumSizePolicy = _ENUM_V{
	'normal',
	'expand',
	'fit',
}

local function _sortLayoutItem( i1, i2 )

	local o1 = i1.order
	local o2 = i2.order
	if o1 == o2 then
		local e1, e2  = i1._entity, i2._entity
		return e1 and e2 and e1.name < e2.name or false
	else
		return o1 < o2
	end
end

--------------------------------------------------------------------
--------------------------------------------------------------------
local function _getOrigin( origin, x0,y0,x1,y1 )
	if y0>y1 then y0,y1 = y1,y0 end
	if x0>x1 then x0,x1 = x1,x0 end
	local xc = (x0+x1)/2
	local yc = (y0+y1)/2
	if origin=='center' then 
		return xc, yc
	elseif origin=='top-left' then
		return x0, y1
	elseif origin=='top-right' then
		return x1, y1
	elseif origin=='top-center' then
		return xc, y1
	elseif origin=='bottom-left' then
		return x0, y0	
	elseif origin=='bottom-right' then
		return x1, y0
	elseif origin=='bottom-center' then
		return xc, y0
	elseif origin=='middle-left' then
		return x0, yc
	elseif origin=='middle-right' then
		return x1, yc
	end
	return xc,0
end
---------------------------------------------------------------------
CLASS: LayoutItem ( mock.Component )
	:MODEL{
		Field 'order' :int();
		'----';
		Field 'offset' :type('vec2') :getset( 'Offset' );
		Field 'size'   :type('vec2') :getset( 'Size' );
		Field 'margin' ;
		Field 'policyH' :enum( EnumSizePolicy );
		Field 'policyV' :enum( EnumSizePolicy );
	}

function LayoutItem:__init()
	self.w,  self.h  = 100, 100
	self.ox, self.oy = 0, 0
	self.order   = 1
	self.margin  = 5
	self.policyH = 'normal'
	self.policyV = 'normal'
end

function LayoutItem:getSize()
	return self.w, self.h
end

function LayoutItem:setSize( w, h )
	self.w, self.h = w, h
end

function LayoutItem:getOffset()
	return self.ox, self.oy
end

function LayoutItem:onStart()
	self:updateLayout()
end

function LayoutItem:setOffset( ox, oy )
	self.ox, self.oy = ox, oy
end

function LayoutItem:getLayoutSize()
	local w,h = self:getSize()
	return w + self.margin*2, h + self.margin*2
end

-- function LayoutItem:getLayoutRect()
-- 	local w,h = self:getLayoutSize()
-- 	return self.ox, self.oy, w, h
-- end

function LayoutItem:setLayoutLoc( x, y )
	local ent = self._entity
	ent:setLocX( x + self.ox + self.margin )
	ent:setLocY( y + self.oy + self.margin )
end

function LayoutItem:getChildrenList()
	local l = {}
	local i = 1 	
	local ent = self._entity
	for c in pairs( ent.children ) do
		local item = c:getComponent( LayoutItem )
		if item then
			l[i] = item
			i = i + 1
		end
	end
	table.sort( l, _sortLayoutItem )
	return l
end

function LayoutItem:updateLayoutTree()
	for i, ch in ipairs( self:getChildrenList() ) do
		ch:updateLayoutTree()
	end
	self:updateLayout()
end

function LayoutItem:updateLayout()
end

function LayoutItem:_updateLayoutParent()
	local p  = self:getEntity()
	local li = self
	while true do
		local p1 = p.parent
		if not p1 then break end
		local li1 = p1:getComponent( LayoutItem )
		if not li1 then break end		
		p = p1
		li = li1
	end
	return li:updateLayoutTree()
end

--------------------------------------------------------------------
CLASS: LayoutFloatPin ( LayoutItem )
	:MODEL {
		Field 'relative' :enum( EnumLayoutRelativeOrigin );
}

function LayoutFloatPin:__init()
	self.relative = 'top-left'
	self.ox = 0
	self.oy = 0
end

function LayoutFloatPin:getLayoutSize() --not in layout calculation
	return false
end

function LayoutFloatPin:updateLayout()
end

function LayoutFloatPin:setRelativeTo( relative )
	self.relative = relative
end

--------------------------------------------------------------------
CLASS: LayoutScreenPin ( LayoutFloatPin )
	:MODEL{
		Field 'refCamera' :type( Camera );
	}

function LayoutScreenPin:__init()
	self.refCamera = false	
end

function LayoutScreenPin:onAttach( ent )
	self:connect( 'camera.viewport_update', 'onViewportUpdate' )
end

function LayoutScreenPin:onViewportUpdate( camera )
	if camera == self.refCamera then
		self:updateLayout()
	end
end

function LayoutScreenPin:setRefCamera( cam )
	self.refCamera = cam
end

function LayoutScreenPin:updateLayout()
	if not self.refCamera then return end
	local vx0,vy0,vx1,vy1 = self.refCamera:getViewportRect()
	local w, h = vx1-vx0, vy1-vy0
	local x, y = _getOrigin( self.relative, vx0, vy0, vx1, vy1 )
	local parent = self:getParent()
	if parent then
		parent:getProp():forceUpdate()
		local x1, y1 = parent:worldToModel( x, y )
		x, y = x1, y1
	end
	self:setLayoutLoc( x, y )
end


--------------------------------------------------------------------
CLASS: LayoutGroup ( LayoutItem )

LayoutGroup:MODEL{
	'----';
	Field 'spacing';
	Field 'refreshLayout' :action('refreshLayout');
}
function LayoutGroup:__init()
	self.spacing = 5
	self.policyH = 'expand'
	self.policyV = 'expand'
end


function LayoutGroup:refreshLayout()
	self:updateLayout()
end

--------------------------------------------------------------------
CLASS: LayoutHorizontalGroup ( LayoutGroup )
	:MODEL{
		Field 'alignment' :enum( EnumLayoutAlignmentV );
}

function LayoutHorizontalGroup:updateLayout()
	local children = self:getChildrenList()
	local spacing = self.spacing
	local x = 0
	local y = 0 --TODO
	for i, ch in ipairs( children ) do
		x = x + spacing
		ch:setLayoutLoc( x,y )
		local w, h = ch:getLayoutSize()
		x = x + w
		x = x + spacing
	end
end

--------------------------------------------------------------------
CLASS: LayoutVerticalGroup ( LayoutGroup )
	:MODEL{
		Field 'alignment' :enum( EnumLayoutAlignment );
}

function LayoutVerticalGroup:updateLayout()
	local children = self:getChildrenList()
	local spacing = self.spacing
	local x = 0 --TODO
	local y = 0 
	for i, ch in ipairs( children ) do
		local itemCom = ch:getComponent( LayoutItem )
		if itemCom then
			y = y + spacing
			local w, h = itemCom:getLayoutSize()
			itemCom:setLayoutLoc( x,y )
			y = y + h
			y = y + spacing
		end
	end
end

--------------------------------------------------------------------
-- CLASS: LayoutGridGroup ( LayoutGroup )
-- 	:MODEL{}
-- --TODO


registerComponent( 'LayoutItem', LayoutItem )
registerComponent( 'LayoutScreenPin', LayoutScreenPin )
registerComponent( 'LayoutHorizontalGroup', LayoutHorizontalGroup )
registerComponent( 'LayoutVerticalGroup', LayoutVerticalGroup )
-- registerComponent( 'LayoutGridGroup', LayoutGridGroup )
