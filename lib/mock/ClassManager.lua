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

end


local function onModuleReleased( path, m )
	_stat( 'release game module', path, m )
	--release classes
	local released = releaseClassesFromEnv( m )
	for key, clas in pairs( released ) do
		_stat( 'clas released:', clas.__fullname )
		--todo: release registered component		
	end

	unloadRegistredObject( mock.getEntityRegistry(), m, 'entity' )
	unloadRegistredObject( mock.getComponentRegistry(), m, 'component' )

	local editor = 	gii.app:getModule('scenegraph_editor')
	if editor then
		editor:scheduleRefreshScene()
	end

	--reload GlobalObject

end

local function onModuleLoaded( path, m )
	-- print( 'load', path, m )
end


GameModule.addGameModuleReleaseListener( onModuleReleased )
GameModule.addGameModuleLoadListener( onModuleLoaded )
