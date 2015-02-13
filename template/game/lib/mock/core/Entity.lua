module 'mock'

--------------------------------------------------------------------
local insert, remove = table.insert, table.remove
local pairs, ipairs  = pairs, ipairs
local unpack = unpack

--------------------------------------------------------------------
----- ENTITY CLASS
--------------------------------------------------------------------
CLASS: Entity ( Actor )
	:MODEL{
		Field '__prefabId':string() :no_edit();
		Field '_priority' :int() :no_edit()  :set('setPriority');
		----
		Field 'name'      :string()  :getset('Name');
		'----';
		Field 'tags'      :string()  :getset('Tags');
		'----';
		Field 'visible'   :boolean() :get('isLocalVisible') :set('setVisible');
		Field 'active'    :boolean() :get('isLocalActive')  :set('setActive');		
		Field 'layer'     :type('layer')  :getset( 'Layer' ) :no_nil();
		'----';
		Field 'loc'       :type('vec3') :getset('Loc') :label('Loc'); 
		Field 'rot'       :type('vec3') :getset('Rot') :label('Rot');
		Field 'scl'       :type('vec3') :getset('Scl') :label('Scl');
		Field 'piv'       :type('vec3') :getset('Piv') :label('Piv');
		'----';
		Field 'color'    :type('color')  :getset('Color') ;
	}

wrapWithMoaiPropMethods( Entity, '_prop' )
local setupMoaiTransform = setupMoaiTransform

--------------------------------------------------------------------
-------init
--------------------------------------------------------------------
--change this to use other MOAIProp subclass as entity prop
local newProp = MOAIProp.new
function Entity:_createEntityProp()
	return newProp()
end

local _PRIORITY = 1
function Entity:__init( data )
	local _prop = self:_createEntityProp()
	self._prop       = _prop

	_PRIORITY = _PRIORITY + 1
	self._priority   = _PRIORITY
	_prop:setPriority( _PRIORITY )

	self.scene       = false --not loaded yet
	self.components  = {}
	self.children    = {}
	-- self.timers      = false
	self.name        = false
	self.active      = true
	self.localActive = true
	self.started     = false
	if type(data) == 'table' then
		local trans = data.transform
		if trans then return setupMoaiTransform( _prop, trans ) end
	end
end

function Entity:_insertIntoScene( scene, layer )
	self.scene = assert( scene )
	local layer = layer or self.layer
	if type(layer) == 'string' then
		layer = scene:getLayer( layer )
	end
	local entityListener = scene.entityListener

	self.layer = layer
	scene.entities[ self ] = true

	local copy = {} --there might be new components attached inside component starting
	for com in pairs( self.components ) do
		copy[ com ] = true
	end 
	for com in pairs( copy ) do
		if not com._entity then
			com._entity = self
			local onAttach = com.onAttach
			if onAttach then onAttach( com, self ) end
			if entityListener then
				entityListener( 'attach', self, com )
			end
		end
	end

	if self.onLoad then
		self:onLoad()
	end

	if self.onUpdate then
		scene:addUpdateListener( self )
	end
	
	local name = self.name
	if name then
		scene:changeEntityName( self, false, name )
	end

	--pre-added children
	for child in pairs( self.children ) do
		if not child.scene then
			child:_insertIntoScene( scene, child.layer or layer )
		end
	end
	scene.pendingStart[ self ] = true
	
	--callback
	if entityListener then entityListener( 'add', self, nil ) end
end

function Entity:getProp()
	return self._prop
end

--------------------------------------------------------------------
------ Destructor
--------------------------------------------------------------------
function Entity:tryDestroy()
	if not self.scene then return end
	return self:destroy()
end

function Entity:destroy()
	assert( self.scene )
	local scene = self.scene
	scene.pendingDestroy[ self ] = true
	scene.pendingStart[ self ] = nil
	
	for child in pairs( self.children ) do
		child:destroy()
	end

	if self.name then
		local entitiesByName = scene.entitiesByName
		if entitiesByName[ self.name ] == self then
			entitiesByName[ self.name ] = nil
		end
	end
end

function Entity:destroyLater( delay )
	assert( self.scene )
	self.scene.laterDestroy[ self ]= self:getTime() + delay
end

function Entity:destroyWithChildrenNow()
	for child in pairs( self.children ) do
		child:destroyWithChildrenNow()
	end
	self:destroyNow()
end

function Entity:destroyNow()
	local scene     = self.scene
	local onDestroy = self.onDestroy
	if not scene then return end

	self:disconnectAll()
	self:clearCoroutines()
	local entityListener = scene.entityListener
	
	--timers
	local timers = self.timers
	if timers then
		for timer in pairs( timers ) do
			timer:stop()
		end
	end

	if onDestroy then onDestroy( self )	end

	local components = self.components
	while true do
		local com = next( components )
		if not com then break end
		components[ com ] = nil
		local onDetach = com.onDetach
		if entityListener then
			entityListener( 'detach', self, com )
		end
		if onDetach then
			onDetach( com, self )
		end		
	end
	-- for com in pairs( components ) do
	-- 	components[ com ] = nil
	-- 	local onDetach = com.onDetach
	-- 	if onDetach then
	-- 		onDetach( com, self )
	-- 	end
	-- end
	
	if self.parent then
		self.parent.children[self] = nil
		self.parent = nil
	end

	scene:removeUpdateListener( self )
	scene.entities[ self ] = nil
	
	--callback
	if entityListener then entityListener( 'remove', self, scene, layer ) end

	self.scene      = false
	self.components = false	
end

--------------------------------------------------------------------
------- Component Attach/Detach
--------------------------------------------------------------------
function Entity:attach( com )
	if not self.components then 
		_error('attempt to attach component to a dead entity')
		return com
	end
	assert( not self.components[ com ], 'component already attached!!!!'  )
	self.components[ com ] = com:getClass()
	if self.scene then
		com._entity = self
		local onAttach = com.onAttach
		if onAttach then onAttach( com, self ) end
		local entityListener = self.scene.entityListener
		if entityListener then
			entityListener( 'attach', self, com )
		end
		if self.started then
			local onStart = com.onStart
			if onStart then onStart( com, self ) end
		end
	end
	return com
end

function Entity:attachInternal( com )
	com.FLAG_INTERNAL = true
	return self:attach( com )
end

function Entity:attachList( l )
	for i, com in ipairs( l ) do
		self:attach( com )
	end
end

function Entity:detach( com, fromAll )
	local components = self.components
	if not components[ com ] then return end
	components[ com ] = nil
	if self.scene then
		local entityListener = self.scene.entityListener
		if entityListener then
			entityListener( 'detach', self, com )
		end
		local onDetach = com.onDetach
		if not fromAll then
			self:disconnectAllForObject( com )
		end
		if onDetach then onDetach( com, self ) end
	end
	com._entity = nil
	return com
end

function Entity:detachAll()
	local components = self.components
	while true do
		local com = next( components )
		if not com then break end
		self:detach( com, true )
	end
end

function Entity:getComponents()
	return self.components
end

function Entity:getComponent( clas )
	if not self.components then return nil end
	for com, comType in pairs( self.components ) do
		if comType == clas then return com end
		if isClass( comType ) and comType:isSubclass( clas ) then return com end
	end
end

function Entity:getComponentByName( name )
	if not self.components then return nil end
	for com, comType in pairs( self.components ) do
		while comType do
			if comType.__name == name then return com end		
			comType = comType.__super
		end
	end
end

function Entity:com( id )
	if not self.components then return nil end
	local tt = type(id)
	if tt == 'string' then
		return self:getComponentByName( id )
	elseif tt == 'table' then
		return self:getComponentByName()
	elseif tt == 'nil' then
		local com = next( self.components )
		return com
	else
		_error( 'invalid component id', tostring(id) )
	end
end

function Entity:hasComponent( clas )
	if self:getComponent( clas ) then return true end
	return false
end

--------------------------------------------------------------------
------- Attributes Links
--------------------------------------------------------------------
local inheritTransformColor = inheritTransformColor
local inheritTransform      = inheritTransform
local inheritLoc            = inheritLoc
local inheritAllPropAttributes = inheritAllPropAttributes

function Entity:_linkSubProp( p )
	inheritAllPropAttributes( p, self._prop )
	if self.scissorRect then p:setScissorRect( self.scissorRect ) end
	return p
end

function Entity:_attachProp( p )
	local _prop = self._prop
	inheritTransformColorVisible( p, _prop )
	self.layer:insertProp( p )
	--TODO: better solution on scissor?
	if self.scissorRect then p:setScissorRect( self.scissorRect ) end
	return p
end

function Entity:_attachTransform( t )
	local _prop = self._prop
	inheritTransform( t, _prop )
	return t
end

function Entity:_attachLoc( t )
	local _prop = self._prop
	inheritLoc( t, _prop )
	return t
end

function Entity:_attachColor( t )
	inheritColor( t, self._prop )
	return t
end

function Entity:_insertPropToLayer( p )
	self.layer:insertProp( p )
	return p
end

function Entity:_detachProp( p )
	self.layer:removeProp( p )
end

--------------------------------------------------------------------
------ Child Entity
--------------------------------------------------------------------
function Entity:addSibling( entity, layerName )	
	if self.parent then
		return self.parent:addChild( entity, layerName )
	else
		local scene = self.scene
		local layer = layerName and scene:getLayer(layerName) or self.layer
		entity:_insertIntoScene( scene, layer )
	end
	return entity
end

function Entity:_attachChildEntity( child )
	local _prop = self._prop
	local _p1   = child._prop
	inheritTransformColorVisible( _p1, _prop )
end

function Entity:addChild( entity, layerName )
	self.children[ entity ] = true
	entity.parent = self
		
	--TODO: better solution on scissor?
	if self.scissorRect then entity:_setScissorRect( self.scissorRect ) end
	--attach transform/color
	self:_attachChildEntity( entity )

	local scene = self.scene

	if scene then
		local targetLayer
		if layerName then 
			targetLayer = scene:getLayer( layerName )
		else
			targetLayer = entity.layer or self.layer
		end
		entity:_insertIntoScene( scene, targetLayer )
	else
		entity.layer = layerName or entity.layer or self.layer
	end
	return entity
end

function Entity:addInternalChild( e, layer )
	e.FLAG_INTERNAL = true
	return self:addChild( e, layer )
end

function Entity:getChildren()
	return self.children
end

function Entity:clearChildren()
	local children = self.children
	while true do
		local child = next( children )
		if not child then return end
		children[ child ] = nil
		child:destroy()
	end
end

function Entity:clearChildrenNow()
	local children = self.children
	while true do
		local child = next( children )
		if not child then return end
		children[ child ] = nil
		child:destroyWithChildrenNow()
	end
end

function Entity:getParent()
	return self.parent
end

function Entity:findEntity( name )
	return self.scene:findEntity( name )
end

function Entity:findEntityCom( entName, comId )
	local ent = self:findEntity( entName )
	return ent and ent:com( comId )
end

-- function Entity:findSibling( name )
-- 	if self.parent then
-- 		return
-- 	else
-- 	end
-- end

function Entity:findChild( name, deep )
	for child in pairs( self.children ) do
		if child.name == name then return child end
		if deep then
			local c = child:findChild( name, deep )
			if c then return c end
		end
	end
	return nil
end

function Entity:findChildByPath( path )
	local e = self
	for part in string.gsplit( path, '/' ) do
		e = e:findChild( part, false )
		if not e then return nil end
	end
	return e
end


--------------------------------------------------------------------
------ Meta
--------------------------------------------------------------------
function Entity:getPriority()
	return self._priority
end

function Entity:setPriority( p )
	self._priority = p
	self._prop:setPriority( p )
end

function Entity:getTime()
	return self.scene:getTime()
end

function Entity:setName( name )
	if self.scene then
		self.scene:changeEntityName(self, entity, name)
		self.name = name
	else
		self.name = name
	end
	return self
end

function Entity:getName()
	return self.name
end

function Entity:getScene()
	return self.scene
end

function Entity:getFullName()
	if not self.name then return false end
	local output = self.name
	local n = self.parent
	while n do
		output = (n.name or '<noname>')..'/'..output
		n = n.parent
	end
	return output
end

function Entity:getLayer()
	if not self.layer then return nil end
	if type( self.layer ) == 'string' then return self.layer end
	return self.layer.name
end

function Entity:setLayer( layerName )
	if self.scene then
		local layer = self.scene:getLayer( layerName )
		assert( layer, 'layer not found:' .. layerName )
		self.layer = layer
		for com in pairs( self.components ) do
			local setLayer = com.setLayer
			if setLayer then
				setLayer( com, layer )
			end
		end
	else
		self.layer = layerName --insert later
	end
end

function Entity:setTags( t )
	self._tags = t
end

function Entity:getTags()
	return self._tags
end

function Entity:hasTag( t )
	if not self._tags then return false end
	return self._tags:find( t )
end

--------------------------------------------------------------------
---------Visibility Control
--------------------------------------------------------------------
function Entity:isVisible()
	return self._prop:getAttr( MOAIProp.ATTR_VISIBLE ) == 1
end

function Entity:isLocalVisible()
	local vis = self._prop:getAttr( MOAIProp.ATTR_LOCAL_VISIBLE )
	return vis == 1
end

function Entity:setVisible( visible )
	self._prop:setVisible( visible )
end

function Entity:show()
	self:setVisible( true )
end

function Entity:hide()
	self:setVisible( false )
end

function Entity:hideChildren()
	for child in pairs( self.children ) do
		child:hide()
	end
end

function Entity:showChildren()
	for child in pairs( self.children ) do
		child:show()
	end
end

--------------------------------------------------------------------
------Active control
--------------------------------------------------------------------
function Entity:start()
	if self.started then return end
	if not self.scene then return end
	
	if self.onStart then
		self:onStart()
	end
	self.started = true

	local copy = {} --there might be new components attached inside component starting
	for com in pairs( self.components ) do
		copy[ com ] = true
	end 
	for com, clas in pairs( copy ) do
		local onStart = com.onStart
		if onStart then onStart( com, self ) end
	end

	for child in pairs( self.children ) do
		child:start()
	end

	if self.onThread then
		self:addCoroutine('onThread')		
	end
	
end

function Entity:setActive( active )	
	active = active or false
	if active == self.localActive then return end
	self.localActive = active
	self:_updateGlobalActive()
end

function Entity:_updateGlobalActive()
	local active = self.localActive
	local p = self.parent
	if p then
		active = p.active and active
		self.active = active
	else
		self.active = active
	end

	--inform components
	for com in pairs(self.components) do
		local setActive = com.setActive
		if setActive then
			setActive( com, active )
		end
	end

	--inform children
	for o in pairs(self.children) do
		o:_updateGlobalActive()
	end

	local onSetActive = self.onSetActive
	if onSetActive then
		return onSetActive( self, active )
	end
end

function Entity:isActive()
	return self.active
end	

function Entity:isLocalActive()
	return self.localActive
end
	

--------------------------------------------------------------------
------ Child/Component Method invoker
--------------------------------------------------------------------
function Entity:createTimer()
	local timers = self.timers
	if not timers then
		timers = table.weak()
		self.timers = timers
	end
	
	local timer = self.scene:createTimer()
	timers[timer] = true

	return timer
end

function Entity:invokeUpward( methodname, ... )
	local parent=self.parent
	
	if parent then
		local m=parent[methodname]
		if m and type(m)=='function' then return m( parent, ... ) end
		return parent:invokeUpward( methodname, ... )
	end

end

function Entity:invokeChildren( methodname, ... )
	for o in pairs(self.children) do
		o:invokeChildren( methodname, ... )
		local m=o[methodname]
		if m and type(m)=='function' then m( o, ... ) end
	end
end


function Entity:invokeComponents( methodname, ... )
	for com in pairs(self.components) do
		local m=com[methodname]
		if m and type(m)=='function' then m( com, ... ) end
	end
end

function Entity:invokeOneComponent( methodname, ... )
	for com in pairs(self.components) do
		local m=com[methodname]
		if m and type(m)=='function' then return m( com, ... ) end
	end
end

--------------------------------------------------------------------
--Function caller
--------------------------------------------------------------------
function Entity:callNextFrame(f, ... )
	if not self.scene then return end
	local t = { func = f, object = self, ... }
	insert( self.scene.pendingCall, t )
end

function Entity:callInterval( interval, func, ... )

	local timer = self:createTimer()
	local args

	if type( func ) == 'string' then
		func = self[func]
		args = { self, ... }
	else
		args = {...}
	end

	timer:setListener( MOAITimer.EVENT_TIMER_END_SPAN, 
		function() return func( unpack(args) ) end
		)
	timer:setMode( MOAITimer.LOOP )
	timer:setSpan( interval )
	return timer
end

function Entity:callLater( time, func, ... )
	local timer = self:createTimer()
	local args

	if type( func ) == 'string' then
		func = self[func]
		args = { self, ... }
	else
		args = {...}
	end

	timer:setListener( MOAITimer.EVENT_TIMER_END_SPAN, 
		function() return func( unpack(args) ) end
		)
	timer:setMode( MOAITimer.NORMAL )
	timer:setSpan( time )
	return timer
end

--------------------------------------------------------------------
--Color
--------------------------------------------------------------------
function Entity:getColor()
	return extractColor( self._prop )
end

-- function Entity:setColor( r,g,b,a )
-- 	return self._prop:setColor( r,g,b,a )
-- end

--------------------------------------------------------------------
----------Transform Conversion
--------------------------------------------------------------------
function Entity:setWorldLoc( x,y,z )
	if self.parent then
		return self:setLoc( self.parent:worldToModel( x,y,z ) )
	else
		return self:setLoc( x,y,z )
	end
end

function Entity:wndToWorld( x, y, z )
	return self.layer:wndToWorld( x, y, z )
end

function Entity:worldToWnd( x, y ,z )
	return self.layer:worldToWnd( x, y ,z )
end

function Entity:worldToModel( x, y ,z )
	return self._prop:worldToModel( x, y ,z )
end

function Entity:modelToWorld( x, y ,z )
	return self._prop:modelToWorld( x, y ,z )
end

function Entity:wndToModel( x, y, z )
	return self._prop:worldToModel( self.layer:wndToWorld( x, y, z ) )
end

function Entity:modelToWnd( x, y ,z )
	return self.layer:worldToWnd( self._prop:modelToWorld( x, y ,z ) )
end

function Entity:modelRectToWorld(x0,y0,x1,y1)
	x0,y0 = self:modelToWorld(x0,y0)
	x1,y1 = self:modelToWorld(x1,y1)
	return x0,y0,x1,y1
end

function Entity:worldRectToModel(x0,y0,x1,y1)
	x0,y0 = self:worldToModel(x0,y0)
	x1,y1 = self:worldToModel(x1,y1)
	return x0,y0,x1,y1
end

---------Scissor Rect?????
function Entity:_setScissorRect( rect )
	self.scissorRect = rect
	for com in pairs( self.components ) do
		local setScissorRect = com.setScissorRect
		if setScissorRect then
			setScissorRect( com, rect )
		end
	end
	for child in pairs( self.children ) do
		child:_setScissorRect( rect )
	end
	return rect
end

function Entity:setScissorRect( x1,y1,x2,y2, noFollow )
	local rect = nil
	if x1 then
		rect = self:makeScissorRect( x1,y1,x2,y2, noFollow )
	end
	return self:_setScissorRect( rect )
end

function Entity:makeScissorRect( x1, y1, x2, y2, noFollow )
	local rect = MOAIScissorRect.new()
	rect:setRect( x1, y2, x2, y1 )
	if not noFollow then self:_attachTransform( rect ) end
	return rect
end

--------------------------------------------------------------------
----------other prop wrapper
--------------------------------------------------------------------
function Entity:setupTransform( transform )
	return setupMoaiTransform( self._prop, transform )
end

function Entity:inside( x, y, z, pad, checkChildren )
	for com in pairs(self.components) do
		local inside = com.inside
		if inside then
			if inside( com, x, y, z, pad ) then return true end
		end
	end

	if checkChildren~=false then
		for child in pairs(self.children) do
			if child:inside(x,y,z,pad) then
				return true
			end
		end
	end
	
	return false
end

function Entity:pick( x, y, z, pad )
	for child in pairs(self.children) do
		local e = child:pick(x,y,z,pad)
		if e then return e end
	end

	for com in pairs(self.components) do
		local inside = com.inside
		if inside then
			if inside( com, x, y, z, pad ) then return self end
		end
	end
	
	return nil
end


function Entity:resetTransform()
	self:setLoc( 0, 0, 0 )
	self:setRot( 0, 0, 0 )
	self:setScl( 1, 1, 1 )
	self:setPiv( 0, 0, 0 )
end

-- function Entity:onEditorPick( x, y, z, pad )
-- 	for child in pairs(self.children) do
-- 		local e = child:onEditorPick(x,y,z,pad)
-- 		if e then return e end
-- 	end

-- 	for com in pairs(self.components) do
-- 		local inside = com.inside
-- 		if inside then
-- 			if inside( com, x, y, z, pad ) then return self end
-- 		end
-- 	end
-- 	return nil
-- end


--------------------------------------------------------------------
--- Registry
--------------------------------------------------------------------

local entityTypeRegistry = {}
function registerEntity( name, creator )
	if not creator then
		return _error( 'no entity to register', name )
	end

	if not name then
		return _error( 'no entity name specified' )
	end
	-- assert( name and creator, 'nil name or entity creator' )
	-- assert( not entityTypeRegistry[ name ], 'duplicated entity type:'..name )
	_stat( 'register entity type', name )
	entityTypeRegistry[ name ] = creator

end

function getEntityRegistry()
	return entityTypeRegistry
end

function getEntityType( name )
	return entityTypeRegistry[ name ]
end

--------------------------------------------------------------------
registerEntity( 'Entity', Entity )


--------------------------------------------------------------------
--Serializer Related
--------------------------------------------------------------------
local function _cloneEntity( src, cloneComponents, cloneChildren, objMap )
	local objMap = {}
	local dst = clone( src, nil, objMap )
	dst.layer = src.layer
	if cloneComponents ~= false then
		for com in pairs( src.components ) do
			if not com.FLAG_INTERNAL then
				local com1 = clone( com, nil, objMap )
				dst:attach( com1 )
			end
		end
	end
	if cloneChildren ~= false then
		for child in pairs( src.children ) do
			if not child.FLAG_INTERNAL then
				local child1 = _cloneEntity( child, cloneComponents, cloneChildren, objMap )
				dst:addChild( child1 )
			end
		end
	end
	return dst
end

function cloneEntity( src )
	return _cloneEntity( src, true, true )
end
