module 'mock'

local insert,remove=table.insert,table.remove


--------------------------------------------------------------------
CLASS: GUIPointer ()
function GUIPointer:__init()
	self.state        = 'up'
	self.activeWidget = false
	self.hoverWidget  = false
	self.touch        = false
end

function GUIPointer:getTouch()
	return self.touch
end

--------------------------------------------------------------------
CLASS: GUIRootWidget ( GUIWidget )
function GUIRootWidget:__init()
	self.inputEnabled = true
	self.modalWidget  = false
	self.__rootWidget = self
end

function GUIRootWidget:onLoad()
	self.inputScript = self:attachInternal( mock.InputScript() )
	self.pointers = {}
end

function GUIRootWidget:getPointer( touch, create )
	local p = self.pointers[touch]
	if (not p) and create then 
		p  =  GUIPointer()
		p.touch = touch
		self.pointers[touch] = p
	end
	return p
end

function GUIRootWidget:setModalWidget( w )
	if self.modalWidget and self.modalWidget ~= w then
		self.modalWidget.__modal = false
	end
	self.modalWidget = w
	if w then
		w.__modal = true
	end
end

function GUIRootWidget:getModalWidget()
	return self.modalWidget
end

local function _findTopWidget( parent, x, y, padding )	
	local childId = 0
	local children = parent.childWidgets
	local count = #children
	for k = count , 1, -1 do
		local child = children[ k ]
		if child:isVisible() and child:isActive() and child.inputEnabled then 
			local px,py,pz = child:getWorldLoc()
			local pad = padding or child:getPadding()
			local inside = child:inside( x, y, pz, pad )
			if inside == 'group' then
				local found = _findTopWidget( child, x, y, padding )
				if found then	return found end
			elseif inside then
				local result = _findTopWidget( child, x, y, padding ) or child
				return result
			end
		end
	end
	return nil
end

function GUIRootWidget:findTopWidget( x, y, pad )
	local start = self.modalWidget or self 
	return _findTopWidget( start, x, y, pad )
end

function GUIRootWidget:onTouchEvent( ev, touch, x, y )
	if ev == 'down' then
		if not self.inputEnabled then return end
		local p = self:getPointer( touch, true )
		p.state = 'down'
		x, y    = self:wndToWorld( x, y )
		local widget = self:findTopWidget( x, y )
		if widget then 
			p.activeWidget = widget
			widget:_onPress( touch, x,y )
			if not widget.__multiTouch then
				if not widget.__activeTouch then widget.__activeTouch=touch end
			end
		end

	elseif ev == 'up' then
		local p = self.pointers[ touch ]
		if not p then return end
		p.state = 'up'
		if p.activeWidget then
			x, y = self:wndToWorld(x,y)
			local widget = p.activeWidget
			widget:_onRelease( touch, x, y )
			if not widget.__multiTouch then	widget.__activeTouch=false		end
		end
		p.activeWidget = false
		p.touch = false
		self.pointers[ touch ] = nil
		
	elseif ev == 'move' then
		local p = self.pointers[touch]
		if not p then return end
		-- p.state='drag'
		if p.activeWidget then
			x, y = self:wndToWorld( x, y )
			p.activeWidget:_onDrag( touch, x, y )
		end

	end
end
