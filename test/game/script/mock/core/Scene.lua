module 'mock'

--------------------------------------------------------------------
--SCENE
--------------------------------------------------------------------
CLASS: 
	Scene (Actor)
	:MODEL{
		Field 'throttle' :getset('Throttle')
	}


function Scene:__init( option )
	self.active = false
	
	self.layers          = {}
	self.entities        = {}
	self.entitiesByName  = {}

	self.pendingDestroy  = {}
	self.laterDestroy    = {}
	self.pendingCall     = {}

	self.updateListeners = {} 

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

	self.timer   = MOAITimer.new()
	self.timer:setMode( MOAITimer.CONTINUE )
	
	self.mainLayer = self:addLayer( 'main' )

	if self.onLoad then self:onLoad() end

	self.mainThread=MOAICoroutine.new()
	self.mainThread:run(function()
		return self:threadMain()
	end
	)
	self.timer:attach( game.actionRoot )
	self.timer:start()

end

function Scene:threadMain( dt )
	local lastTime = game:getTime()
	while true do	
		local nowTime = game:getTime()

		if self.active then
			local dt = nowTime -lastTime
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
			for entity in pairs( self.updateListeners ) do
				if entity:isActive() then
					entity:onUpdate( dt )
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

		--end of step update
		end

		--executeDestroyQueue()
		local pendingDestroy = self.pendingDestroy
		self.pendingDestroy = {}
		for entity in pairs( pendingDestroy ) do
			entity:destroyNow()
		end
		coroutine.yield()

		if self.exiting then 
			self:exitNow() 
		elseif self.exitingTime and self.exitingTime <= game:getTime() then
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
function Scene:enter(option)
	_codemark( 'Entering Scene: %s', self.name )
	self:init()
	self:addLayer( 'main', self.option and self.option.layer )
	self.active = true
	--callback onenter
	local onEnter = self.onEnter
	if onEnter then onEnter( self, option ) end
	emitSignal( 'scene.enter', self )	
end

function Scene:exitLater(time)
	self.exitingTime = game:getTime() + time
end

function Scene:exit(nextScene)
	self.exiting = true	
end

function Scene:exitNow()
	_codemark('Exit Scene: %s',self.name)
	self.active=false
	self.exiting=false
	emitSignal('scene.exit',self)
	if self.onExit then self.onExit() end
	self:clear()
	self.timer:stop()
end


--------------------------------------------------------------------
--Layer control
--------------------------------------------------------------------
--[[
	Layer in scene is only for placeholder/ viewport transform
	Real layers for render is inside Camera, which supports multiple viewport render
]]


local sortModeName={
	iso          = MOAILayer.SORT_ISO,
	
	priorityAsc  = MOAILayer.SORT_PRIORITY_ASCENDING,
	priorityDesc = MOAILayer.SORT_PRIORITY_DESCENDING,

	xAsc         = MOAILayer.SORT_X_ASCENDING,
	xDesc        = MOAILayer.SORT_X_DESCENDING,

	yAsc         = MOAILayer.SORT_Y_ASCENDING,
	yDesc        = MOAILayer.SORT_Y_DESCENDING,

	zAsc         = MOAILayer.SORT_Z_ASCENDING,
	zDesc        = MOAILayer.SORT_Z_DESCENDING,

	vectorAsc    = MOAILayer.SORT_VECTOR_ASCENDING,
	vectorDesc   = MOAILayer.SORT_VECTOR_DESCENDING,

	none         = false
}


function Scene:addLayer( name, option )
	local partition = MOAIPartition.new()
	local layer     = MOAILayer.new()
	layer:setPartition( partition )
	layer.name     = name
	self.layers[ name ] = layer

	option = option or {}
	layer.priority = option.priority or 0

	if option.sort then
		local s = sortModeName[ option.sort ]
		if s == false then
			s = MOAILayer.SORT_NONE
		else
			s = s or MOAILayer.SORT_PRIORITY_ASCENDING
		end
		layer:setSortMode(s)
		layer.sortMode = s
	end

	return layer
end

function Scene:getLayer( name )
	return self.layers[ name ]
end

function Scene:setDefaultViewport( viewport )
	self.defaultViewport = viewport
	for k, layer in pairs( self.layers ) do
		layer:setViewport( viewport )
	end
end

function Scene:setDefaultCamera( camera )
	self.defaultCamera = camera
	for k, layer in pairs( self.layers ) do
		layer:setCamera( camera )
	end
end


--------------------------------------------------------------------
--Entity Control
--------------------------------------------------------------------
function Scene:setEntityListener( func )
	self.entityListener = func or false
end

function Scene:addEntity( entity, layer )
	layer = layer or entity.defaultLayer
	
	if not layer then 
		layer=self.layers['main']
	elseif type(layer)=='string' then 
		local layername=layer
		layer=self.layers[layername]
		if not layer then return error('layer not found:'..layername) end 
	end

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

function Scene:clear()
	for e in pairs( self.entities ) do
		e:destroyNow()
	end

	--layers in Scene is not in render stack, just let it go
	self.layers          = {}
		
	self.laterDestroy    = {}
	self.pendDestroy     = {}
	self.pendingCall     = {}

	self.updateListeners = {}
	self.defaultCamera   = false
end

