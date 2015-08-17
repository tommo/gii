module 'mock_edit'

CLASS: CanvasItemManager ( EditorEntity )
	:MODEL{}

function CanvasItemManager:__init()
	self.items = {}	
	self.activeItem = false
	self.hoverItem  = false
	self.focusItem  = false
	self.activeMouseButton = false
	self.factorZoom = 1
end

function CanvasItemManager:onLoad()
	local view = self:getView()
	assert( isInstance( view, CanvasView ) )

	self.inputScript = self:attachInternal( 
		mock.InputScript{ device = view:getInputDevice() }
	)

	local cameraListenerNode = MOAIScriptNode.new()
	cameraListenerNode:setCallback( function() self:updateAllItemScale() end )

	local cameraCom = view:getCameraComponent()
	cameraListenerNode:setNodeLink( cameraCom.zoomControlNode )
	if cameraCom:isPerspective() then
		cameraListenerNode:setNodeLink( cameraCom:getMoaiCamera() )
	end
	self.cameraListenerNode = cameraListenerNode
	self.factorZoom = 1/cameraCom:getZoom()
	self:setLocZ( -1000 )
end

function CanvasItemManager:getView()
	return self.parent
end

function CanvasItemManager:addItem( item )
	table.insert( self.items, 1, item )
	self:addChild( item )
	self:updateItemScale( item )
end

function CanvasItemManager:_attachChildEntity( child )
	inheritVisible( child:getProp(), self:getProp() )
end

function CanvasItemManager:removeItem( item )
	item:destroyWithChildrenNow()
end

function CanvasItemManager:updateItemScale( item )
	local cameraCom = self:getView():getCameraComponent()
	if cameraCom:isPerspective() then		
		--TODO:consider distance to camera into scale calc
		if item:isConstantSize() then
			local factorDistance = 1
			local scl = self.factorZoom * factorDistance
			item:setScl( scl, scl, scl )
		end
	else
		if item:isConstantSize() then
			local scl = self.factorZoom
			item:setScl( scl, scl, scl )
		end
	end
end

function CanvasItemManager:updateAllItemScale()
	local view = self:getView()
	local cameraCom = view:getCameraComponent()
	local zoom = cameraCom:getZoom()
	local factorZoom = 1/zoom
	self.factorZoom = factorZoom
	for i, item in ipairs( self.items ) do
			self:updateItemScale( item )
	end		
	view:updateCanvas()
end

function CanvasItemManager:onItemDestroyed( item )
	if self.activeItem == item then
		self.activeMouseButton = false
		self.activeItem = false
	end
	if self.hoverItem == item then
		self.hoverItem = false
	end
	if self.focusItem == item then
		self.focusItem = false
	end
	local idx = self:getItemIndex( item )
	if idx then
		table.remove( self.items, idx )
	end
end

function CanvasItemManager:getItemIndex( item )
	return table.index( self.items, item )
end

function CanvasItemManager:bringToFront( item )
	local idx = self:getItemIndex( item )
	if not idx then return end
	table.remove( self.items, idx )
	table.insert( self.items, 1, item )
	self:updateItemsProrities()
end

function CanvasItemManager:sendToBack( item )
	local idx = self:getItemIndex( item )
	if not idx then return end
	table.remove( self.items, idx )
	table.insert( self.items, item )
	self:updateItemsProrities()
end

function CanvasItemManager:focus( item )
	if self.focusItem then
		self.focusItem:onBlur()
	end
	self.focusItem = item
	if item then
		item.focused = true
		item:onFocus()
	end
end

function CanvasItemManager:getFocusItem()
	return self.focusItem
end

function CanvasItemManager:getHoverItem()
	return self.hoverItem
end

function CanvasItemManager:getActiveItem()
	return self.activeItem
end

function CanvasItemManager:updateItemsProrities()
	for i, item in ipairs( self.items ) do
		item:setPriority( i )
	end
end

function CanvasItemManager:findTopItem( x, y, pad )
	for i, item in ipairs( self.items ) do
		if item:inside( x, y, 0, pad ) then
			return item
		end
	end
	return false
end

function CanvasItemManager:onMouseMove( x, y )	
	if not self:isActive() then return end
	if self.activeMouseButton then
		self.activeItem:onDrag( self.activeMouseButton, x, y )
		return
	end

	local item = self:findTopItem( x, y )
	if item ~= self.hoverItem then
		if self.hoverItem then
			self.hoverItem:onMouseEnter()
		end
		self.hoverItem = item
		if item then
			item:onMouseLeave()
		end
	end

	if self.hoverItem then
		self.hoverItem:onMouseMove( x, y )
	end

end

function CanvasItemManager:onMouseDown( btn, x, y )
	if not self:isActive() then return end
	if self.activeItem then return end
	local item = self:findTopItem( x, y )
	if item then
		self.activeItem = item
		self.activeItem:onMouseDown( btn, x, y )
		self.activeMouseButton = btn	
	end
	self:focus( item )
	
end

function CanvasItemManager:onMouseUp( btn, x, y )
	if not self:isActive() then return end
	if self.activeMouseButton == btn then
		self.activeItem:onMouseUp( btn, x, y )
		self.activeMouseButton = false
		self.activeItem = false
	end
end

function CanvasItemManager:onKeyEvent( key, down )
	if not self:isActive() then return end
end


--------------------------------------------------------------------
CLASS: CanvasItem ( EditorEntity )
	:MODEL{}

function CanvasItem:__init()
	self.hovered = false
	self.pressed = false
	self.focused = false
	self.index = 0
end

function CanvasItem:getView()
	return self.parent:getView()
end

function CanvasItem:onDestroy()
	if self.parent then
		self.parent:onItemDestroyed( self )
	end
end

function CanvasItem:bringToFront()
	if self.parent then self.parent:bringToFront( self ) end
end

function CanvasItem:sendToBack()
	if self.parent then self.parent:sendToBack( self ) end
end

function CanvasItem:onMouseUp( btn, x, y )
end

function CanvasItem:onMouseDown( btn, x, y )
end

function CanvasItem:onMouseMove( x, y )
end

function CanvasItem:onMouseEnter()
end

function CanvasItem:onMouseLeave()
end

function CanvasItem:onFocus()
end

function CanvasItem:onBlur()
end

function CanvasItem:onDrag( btn, x, y )
end

function CanvasItem:isConstantSize()
	return true
end
--------------------------------------------------------------------
CLASS: CanvasBackgroundItem ( CanvasItem )
	:MODEL{}
