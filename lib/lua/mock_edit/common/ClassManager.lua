module 'mock_edit'

registerSignals{	
}

local function unloadRegistredObject( registry, m, info )
	local toRemove = {}
	for k, c in pairs( registry ) do
		local tt = type( c )
		if tt == 'function' then
			local env = getfenv( c )
			if env == m then
				toRemove[ k ] = true
			end
		elseif tt == 'table' then
			if c.__env == m then
				toRemove[ k ] = true
			end
		end
	end
	for k in pairs( toRemove ) do
		_statf( 'unload registered %s: %s', info, k )
		registry[ k ] = nil
	end
	return toRemove
end


local function onModuleReleased( path, m )
	_stat( 'release game module', path, m )
	--release classes
	local released = releaseClassesFromEnv( m )
	for key, clas in pairs( released ) do
		_stat( 'clas released:', clas.__fullname )
		--todo: release registered component		
	end

	local removedEntityClasses = 
		unloadRegistredObject( mock.getEntityRegistry(), m, 'entity' )

	local removedComClasses = 
	unloadRegistredObject( mock.getComponentRegistry(), m, 'component' )

	local removedGlobalClasses = 
	unloadRegistredObject( mock.getGlobalObjectClassRegistry(), m, 'global object' )

	--reload Scene Graph
	if next( removedEntityClasses ) or next( removedComClasses ) then
		local editor = 	gii.app:getModule( 'scenegraph_editor' )
		if editor then
			editor:scheduleRefreshScene()
		end
	end

	--reload GlobalObject
	if next( removedGlobalClasses ) then
		local globalObjectManager = gii.app:getModule( 'global_object_manager' )
		if globalObjectManager then
			globalObjectManager:scheduleRefreshObject()
		end
	end
end

local function onModuleLoaded( path, m )
	-- print( 'load', path, m )
end


GameModule.addGameModuleReleaseListener( onModuleReleased )
GameModule.addGameModuleLoadListener( onModuleLoaded )
