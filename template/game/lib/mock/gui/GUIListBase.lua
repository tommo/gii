module 'mock'

registerSignals{
	'ui.list.select',	
}

--------------------------------------------------------------------
CLASS: GUIListBase     ( GUIScrollArea )
CLASS: GUIListItemBase ( GUIButtonBase )
--------------------------------------------------------------------

EnumListGrowDirection = _ENUM_V {
	'+x','+y','-x','-y'
}

--------------------------------------------------------------------
---List
--------------------------------------------------------------------	
GUIListBase: MODEL{
	Field 'layoutRow' :int() :label('row');
	Field 'layoutCol' :int() :label('column');
	Field 'tileSize' :type( 'vec2' ) :getset( 'TileSize' );
	Field 'offset'   :type( 'vec2' ) :getset( 'Offset' );
	Field 'growDirection'	 :enum( EnumListGrowDirection );
}

function GUIListBase:__init()
	self.selection  = false
	self.items      = {}
	self.layoutRow  = 0
	self.layoutCol  = 4
	self.tileWidth  = 100
	self.tileHeight = 100
	self.offsetX    = 100
	self.offsetY    = -60
	self.growDirection = '-y'
end

function GUIListBase:onLoad()
end

function GUIListBase:setOffset( x, y )
	self.offsetX = x
	self.offsetY = y
	self:resetLayout()
end

function GUIListBase:getOffset()
	return self.offsetX, self.offsetY
end

function GUIListBase:setTileSize( w, h )
	self.tileWidth = w
	self.tileHeight = h
	self:resetLayout()
end

function GUIListBase:getTileSize()
	return self.tileWidth, self.tileHeight
end

function GUIListBase:selectItem( item )
	local pitem = self.selection
	if pitem == item then return end
	self.selection = item
	if pitem then
		pitem.selected = false
		pitem:onDeselect()
	end
	if item then
		item.selected = true
		item:onSelect()
	end	
	self:onSelectionChanged( self.selection )
end

function GUIListBase:getSelection()
	return self.selection
end

function GUIListBase:clear()
	self:selectItem( false )
	for i, item in ipairs( self.items ) do
		item:destroy()		
	end
	self.items = {}
end

function GUIListBase:getItemCount()
	return #self.items
end

function GUIListBase:removeItem( item )
	for i, it in ipairs( self.items ) do
		if it == item then
			table.remove( self.items, i )
			item:destroy()
		end
	end
	self:resetItemLoc()
end

function GUIListBase:sortItems( cmpFunc )
	table.sort( self.items, cmpFunc )
	self:resetItemLoc()
end

function GUIListBase:addItem( option )
	local item = self:createItem( option )
	table.insert( self.items, item )
	local id = #self.items
	-- item.itemId = id
	local x,y = self:calcItemLoc( id )
	item:setLoc( x, y, 1 )
	return item
end

function GUIListBase:createItem( option )
	local i = self:addInternalChild( GUIListItemBase() )
	return i
end

function GUIListBase:getItemId( item )
	for i, it in ipairs( self.items ) do
		if it == item then return i end
	end
	return nil
end

function GUIListBase:calcItemLoc( id )
	id = id - 1
	local row = math.max( self.layoutRow, 1 )
	local col = math.max( self.layoutCol, 1 )
	local dir = self.growDirection
	local tileWidth = self.tileWidth
	local tileHeight = self.tileHeight
	if dir == '-y' then		
		local y = math.floor( id/col )
		local x = id % col
		return x * tileWidth + self.offsetX, - y*tileHeight + self.offsetY
	elseif dir == '+y' then
		local y = math.floor( id/col )
		local x = id % col
		return x * tileWidth + self.offsetX, y*tileHeight + self.offsetY
	elseif dir == '-x' then
		local x = math.floor( id/row )
		local y = id % row 
		return -x * tileWidth + self.offsetX, y*tileHeight + self.offsetY
	elseif dir == '+x' then
		local x = math.floor( id/row )
		local y = id % row 
		return x * tileWidth + self.offsetX, y*tileHeight + self.offsetY
	end
end

function GUIListBase:resetLayout()
	self:resetItemLoc()
end

function GUIListBase:resetItemLoc()
	for i, item in ipairs( self.items ) do
		item:setLoc( self:calcItemLoc( i ) )
	end
end

function GUIListBase:onSelectionChanged()
end
--TODO: multiple selection?
-- function GUIListBase:clearSelection()
-- 	--todo
-- end

--------------------------------------------------------------------
---ITEM
--------------------------------------------------------------------
function GUIListItemBase:__init()
	self.selected = false
end

function GUIListItemBase:onPress( pointer, x, y )
	self.dragX0 = x
	self.dragY0 = y
	self.dragDiffX = 0
	self.dragDiffY = 0
	
	local sx, sy = self.parent:getScrollSpeed()
	local ss = sx*sx + sy*sy
	self.slowScrollTapping = ss<10
	self.pressTime = os.clock()
	if self.parent:isScrolling() then
		self.parent:grabScroll( true )
	else
		self.parent:grabScroll( false )
	end
end

function GUIListItemBase:onDrag( pointer, x, y )
	local dx = x - self.dragX0
	local dy = y - self.dragY0
	self.dragX0 = x
	self.dragY0 = y
	self.dragDiffY = self.dragDiffY + dy
	self.dragDiffX = self.dragDiffX + dx
	if not self.parent:isScrollGrabbed() then
		if math.magnitude( self.dragDiffX, self.dragDiffY ) > 10 then
			self.slowScrollTapping = false
			self.parent:grabScroll( true )
		else
			return
		end
	end
	self.parent:addTargetScrollX( dx )
	self.parent:addTargetScrollY( dy )
end

function GUIListItemBase:onRelease( pointer, x, y )
	local timeDelta = os.clock() - self.pressTime
	if self.parent:isScrollGrabbed() then
		self.parent:grabScroll( false )
		if timeDelta > 0.5 then return end
		if not self.slowScrollTapping then return end
	end
	self:emit( 'ui.list.select', self.parent, self )
	self.parent:selectItem( self )
end

function GUIListItemBase:onSelect()
end

function GUIListItemBase:onDeselect()
end

function GUIListItemBase:getSize()
	local parent = self.parent
	if parent then
		return self.parent:getTileSize()
	else
		return 0, 0
	end
end
