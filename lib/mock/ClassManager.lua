registerSignals{	
}

local function onModuleReleased( path, m )
	-- print( 'release', path, m )
	--release classes
	local released = releaseClassesFromEnv( m )
	for clas in pairs( released ) do
		print('clas released:', clas.__name )
	end
	local editor = 	gii.app:getModule('scenegraph_editor')
	if editor then
		editor:scheduleRefreshScene()
	end
end

local function onModuleLoaded( path, m )
	-- print( 'load', path, m )
end


gii.addGameModuleReleaseListener( onModuleReleased )
gii.addGameModuleLoadListener( onModuleLoaded )
