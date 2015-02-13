module 'mock'

--------------------------------------------------------------------
--SCENE
--------------------------------------------------------------------
CLASS: 
	Scene (Actor)
	:MODEL{
		
	}


function Scene:__init( option )
	self.active = false
	
	self.running = false
	self.arguments       = false
	self.layers          = {}
	self.entities        = {}
	self.entitiesByName  = {}

	self.pendingStart    = {}
	self.pendingDestroy  = {}
	self.laterDestroy    = {}
	self.pendingCall     = {}

	self.updateListeners = {}
	self.metaData        = {} 

	self.defaultCamera   = false
	self.option          = option

	self.throttle        = 1

	return self
end


--------------------------------------------------------------------
--COMMON
--------------------------------------------------------------------
function Scene:init()
	if self.initialized then return end 
	self.initialized  = true
	self.exiting = false
	self.active  = true

	-- self.mainLayer = self:addLayer( 'main' )
	self:initLayers()

	if self.onLoad then self:onLoad() end

	_stat( 'Initialize Scene' )

	self.timer   = MOAITimer.new()
	self.timer:setMode( MOAITimer.CONTINUE )
	self.timer:attach( self:getActionRoot() )

end

function Scene:initLayers()
	local layers = {}
	local defaultLayer
	
	for i, l in ipairs( game.layers ) do
		local layer = l:makeMoaiLayer()
		layers[i] = layer
		if l.default then
			defaultLayer = layer
		end
	end

	if defaultLayer then
		self.defaultLayer = defaultLayer
	else
		self.defaultLayer = layers[1]
	end
	assert( self.defaultLayer )
	self.layers = layers
end

function Scene:getActionRoot()
	return game:getActionRoot()
end

function Scene:getTime()
	return game:getTime()
end

function Scene:flushPendingStart()
	if not self.running then return self end
	local pendingStart = self.pendingStart
	self.pendingStart = {}
	for entity in pairs( pendingStart ) do
		entity:start()
	end
	return self
end

function Scene:threadMain( dt )
	-- runProfiler( 5 )
	dt = 0
	local lastTime = self:getTime()
	while true do	
		local nowTime = self:getTime()

		if self.active then
			-- local dt = nowTime - lastTime
			lastTime = nowTime

			--callNextFrame
			local pendingCall = self.pendingCall
			self.pendingCall = {}
			for i, t in ipairs( pendingCall ) do
				local func = t.func
				if type( func ) == 'string' then --method call
					local entity = t.object
					func = entity[ func ]
					func( entity, unpack(t) )
				else
					func( unpack(t) )
				end
			end

			--onUpdate
			for obj in pairs( self.updateListeners ) do
				local isActive = obj.isActive
				if not isActive or isActive( obj ) then
					obj:onUpdate( dt )
				end
			end
			
			--destroy later
			local laterDestroy = self.laterDestroy
			for entity, time in pairs( laterDestroy ) do
				if nowTime >= time then
					entity:destroy()
					laterDestroy[ entity ] = nil
				end
			end

			self:flushPendingStart()

		--end of step update
		end
		
		--executeDestroyQueue()
		local pendingDestroy = self.pendingDestroy
		self.pendingDestroy = {}
		for entity in pairs( pendingDestroy ) do
			if entity.scene then
				entity:destroyNow()
			end
		end

		dt = coroutine.yield()
		if self.exiting then 
			self:exitNow() 
		elseif self.exitingTime and self.exitingTime <= self:getTime() then
			self.exitingTime = false
			self:exitNow()
		end
	--end of main loop
	end
end

--obj with onUpdate( dt ) interface
function Scene:addUpdateListener( obj )
	--assert ( type( obj.onUpdate ) == 'function' )
	self.updateListeners[ obj ] = true
end

function Scene:removeUpdateListener( obj )
	self.updateListeners[ obj ] = nil
end

function Scene:getPath()
	return self.path or false
end

function Scene:getArguments()
	return self.arguments
end

--------------------------------------------------------------------
--TIMER
--------------------------------------------------------------------
function Scene:getTime()
	--TODO: allow scene to have independent clock
	return self.timer:getTime()
end

function Scene:getSceneTimer()
	return self.timer
end

function Scene:createTimer( )
	local timer = MOAITimer.new()
	timer:attach( self.timer )
	return timer
end

function Scene:pause( paused )
	self.timer:pause( paused~=false )
	self.mainThread:pause( paused )
end

function Scene:resume( )
	return self:pause( false )
end

function Scene:setThrottle( t )
	self.throttle = t
	self.timer:throttle( t or 1 )
end

function Scene:getThrottle()
	return self.throttle
end

--------------------------------------------------------------------
--Flow Control
--------------------------------------------------------------------
function Scene:start()
	if self.running then return end
	if not self.initialized then self:init() end
	self.running = true
	local onStart = self.onStart
	if onStart then onStart( self ) end

	self.mainThread = MOAICoroutine.new()
	self.mainThread:setDefaultParent( true )
	self.mainThread:run(
		function()
			return self:threadMain()
		end
	)

	for ent in pairs( self.entities ) do
		if not ent.parent then
			ent:start()
		end
	end
	self.timer:start()	
end


function Scene:stop()
	if not self.running then return end
	self.running = false
	self.mainThread:stop()
	self.timer:stop()
	self.mainThread = false
end

function Scene:exitLater(time)
	self.exitingTime = game:getTime() + time
end

function Scene:exit()
	_stat( 'scene exit' )
	self.exiting = true	
end

function Scene:exitNow()
	_codemark('Exit Scene: %s',self.name)
	self:stop()
	self.active  = false
	self.exiting = false
	if self.onExit then self.onExit() end
	self:clear()	
	emitSignal( 'scene.exit', self )	
end


--------------------------------------------------------------------
--Layer control
--------------------------------------------------------------------
--[[
	Layer in scene is only for placeholder/ viewport transform
	Real layers for render is inside Camera, which supports multiple viewport render
]]


function Scene:getLayer( name )
	if not name then return self.defaultLayer end
	for i,l in pairs( self.layers ) do
		if l.name == name then return l end
	end
	return nil
end


--------------------------------------------------------------------
--Entity Control
--------------------------------------------------------------------
function Scene:setEntityListener( func )
	self.entityListener = func or false
end

function Scene:addEntity( entity, layer )
	assert( entity )
	layer = layer or entity.layer or self.defaultLayer
	
	if type(layer) == 'string' then 
		local layerName = layer
		layer = self:getLayer( layerName )
		if not layer then 
			_error( 'layer not found:', layerName )			
			layer = self.defaultLayer
		end 
	end
	assert( layer )
	entity:_insertIntoScene( self, layer )
	
	return entity
end

function Scene:addEntities( list, layer )
	for k, entity in pairs( list ) do
		self:addEntity( entity, layer )
		if type( k ) == 'string' then
			entity:setName( k )
		end
	end
end

function Scene:findEntity( name )
	return self.entitiesByName[ name ]
end

function Scene:changeEntityName( entity, oldName, newName )
	if oldName then
		if entity == self.entitiesByName[ oldName ] then
			self.entitiesByName[ oldName ]=nil
		end
	end
	if not self.entitiesByName[ newName ] then
		self.entitiesByName[ newName ] = entity
	end
end

function Scene:clear( keepEditorEntity )
	local entityListener = self.entityListener
	if entityListener then
		self.entityListener = false
		entityListener( 'clear', keepEditorEntity )
	end
	local toRemove = {}
	_stat( 'pre clear', table.len( self.entities) )
	for e in pairs( self.entities ) do
		if not e.parent then
			if not ( keepEditorEntity and e.FLAG_EDITOR_OBJECT ) then
				toRemove[ e ] = true				
			end
		end
	end
	for e in pairs( toRemove ) do
		e:destroyWithChildrenNow()
	end
	_stat( 'post clear', table.len( self.entities) )
	
	--layers in Scene is not in render stack, just let it go
	self.laterDestroy    = {}
	self.pendDestroy     = {}
	self.pendingCall     = {}
	self.entitiesByName  = {}
	self.pendingStart    = {}

	self.defaultCamera   = false
	self.entityListener = entityListener
	self.arguments = false
end

Scene.add = Scene.addEntity
