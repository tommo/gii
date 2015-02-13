module 'mock'

--------------------------------------------------------------------

local DEFAULT_TOUCH_PADDING = 20
function setDefaultTouchPadding( pad )
	DEFAULT_TOUCH_PADDING = pad or 20
end

function getDefaultTouchPadding()
	return DEFAULT_TOUCH_PADDING or 20
end

--------------------------------------------------------------------
CLASS: GUIWidget ( Entity )
	:MODEL{}

function GUIWidget:__init()
	self.__WIDGET     = true
	self.__rootWidget = false
	self.__modal      = false

	self.childWidgets = {}
	self.inputEnabled = true
	self:setSize( self:getDefaultSize() ) --default

end

function GUIWidget:_setRootWidget( root )
	if self.__rootWidget == root then return end
	self.__rootWidget = root	
	for i, child in ipairs( self.childWidgets ) do
		child:_setRootWidget( root )
	end
	if self.__modal then
		self.__rootWidget:setModalWidget( self )
	end
end

------Public API

function GUIWidget:addChild( entity, layerName )
	if entity.__WIDGET then		
		table.insert( self.childWidgets, entity )
		if self.__rootWidget then
			entity:_setRootWidget( self.__rootWidget )
		end
		self:sortChildren()
	end	
	return Entity.addChild( self, entity, layerName )	
end

local function widgetZSortFunc( w1, w2 )
	local z1 = w1:getLocZ()
	local z2 = w2:getLocZ()
	return z1 < z2
end

function GUIWidget:sortChildren()
	table.sort( self.childWidgets, widgetZSortFunc )	
end

function GUIWidget:destroyNow()
	local parent = self.parent
	local childWidgets = parent and parent.childWidgets
	if childWidgets then
		for i, child in ipairs( childWidgets ) do
			if child == self then
				table.remove( childWidgets, i )
				break
			end
		end
	end
	if self.__modal then
		self:setModal( false )		
	end
	return Entity.destroyNow( self )
end

function GUIWidget:setModal( modal )
	modal = modal~=false
	if self.__modal == modal then return end
	self.__modal = modal
	if self.__rootWidget then
		if modal then 
			self.__rootWidget:setModalWidget( self )
		else
			if self.__rootWidget:getModalWidget() == self then
				self.__rootWidget:setModalWidget( nil )
			end
		end
	end
end

--geometry
function GUIWidget:inside( x, y, z, pad )
	x,y = self:worldToModel( x, y )
	local x0,y0,x1,y1 = self:getRect()
	if x0 > x1 then x1,x0 = x0,x1 end
	if y0 > y1 then y1,y0 = y0,y1 end
	if pad then
		return x >= x0-pad and x <= x1+pad and y >= y0-pad and y<=y1+pad
	else
		return x>=x0 and x<=x1 and y>=y0 and y<=y1
	end
end


function GUIWidget:setSize( w, h )
	if not w then
		w, h = self:getDefaultSize()
	end
	self.width, self.height = w, h
	--todo: update layout in the root widget
	-- self:updateLayout()
end

function GUIWidget:getDefaultSize()
	return 0,0
end

function GUIWidget:getSize()
	return self.width, self.height
end

function GUIWidget:setRect( x, y, w, h )
	self.x = x
	self.y = y
end

function GUIWidget:getRect()
	local w, h = self:getSize()
	return 0,0,w,h
end

function GUIWidget:getPadding()
	return DEFAULT_TOUCH_PADDING
end

function GUIWidget:getRootWidget()
	return self.__rootWidget
end

--layout
function GUIWidget:setLayout( l )
	if l then
		assert( not l.widget )
		self.layout = l
		l.widget = self
		self:updateLayout()
		return l
	else
		self.layout = false
	end
end

function GUIWidget:updateLayout()
	if self.layout then
		self.layout:onLayout( self )
	end
end

--Virtual Interfaces
function GUIWidget:_onPress( pointer, x, y )
	self:setState( 'press' )
	return self:onPress( pointer, x, y )
end

function GUIWidget:_onRelease( pointer, x, y )
	self:setState( 'normal' )
	return self:onRelease( pointer, x, y )
end

function GUIWidget:_onDrag( pointer, x, y, dx, dy )
	return self:onDrag( pointer, x, y, dx, dy )
end

--user callback
function GUIWidget:onPress( pointer, x, y )
end

function GUIWidget:onRelease( pointer, x, y )
end

function GUIWidget:onDrag( pointer, x, y, dx, dy )
end

function GUIWidget:onSizeHint()
	return 0, 0
end

function GUIWidget:onSetActive( active )
	self:setState( active and 'normal' or 'disabled' )	
end

function GUIWidget:setInputEnabled( enabled )
	self.inputEnabled = enabled ~= false
end

--------------------------------------------------------------------
CLASS: GUILayout ()
	:MODEL{}
function GUILayout:__init()
	self.widget = false
end

function GUILayout:onLayout( widget )
end

--------------------------------------------------------------------
CLASS: GUIWidgetGroup ( GUIWidget )
	:MODEL{}

function GUIWidgetGroup:inside()
	return 'group'
end

--------------------------------------------------------------------
function registerGUIWidget( name, class )
	registerEntity( '[UI]'..name, class )
end

--------------------------------------------------------------------
registerGUIWidget( 'Group', GUIWidgetGroup )