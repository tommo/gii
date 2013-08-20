local GameModules = {}

local _require = require
--[[
	create a envrionment
]]

local gameScriptPaths = {
	GII_PROJECT_SCRIPT_PATH .. '/?.lua',
	GII_PROJECT_SCRIPT_PATH .. '/?/init.lua'
}

local function searchFile( path )
	path = path:gsub( '%.','/' )
	for i, pattern in ipairs( gameScriptPaths ) do
		local f = pattern:gsub( '?', path )
		local fp = io.open(f,'r')
		if fp then fp:close() return f end		
	end
	return nil
end

--------------------------------------------------------------------
local GameModuleMT = { __index = _G }
function createEmptyModule( path, fullpath )
	local m = {
		_NAME   = path,
		_PATH   = path,
		_SOURCE = fullpath,
		__REQUIRES    = {},
		__REQUIREDBY  = {}
	}

	m.require = function( path, ... )
		local loaded, errType, errMsg, tracebackMsg = requireGameModule( path )
		if loaded then 
			m.__REQUIRES[ path ] = true
			loaded.__REQUIREDBY[ m._PATH ] = true
			return loaded
		end
		if errType ~= 'notfound' then
			print( errMsg )
			if tracebackMsg then print( tracebackMsg ) end
			error( 'error loading game module', 2 )
		end
		return _require( path, ... )
	end

	return setmetatable( m, GameModuleMT )
end
--------------------------------------------------------------------

function loadGameModule( path )
	local fullpath = searchFile( path )
	if not fullpath then
		return nil, 'notfound'
	end
	_stat( 'loading module from', fullpath )
	local chunk, compileErr = loadfile( fullpath )
	if not chunk then
		return nil, 'failtocompile', compileErr
	end
	local m = createEmptyModule( path, fullpath )
	setfenv( chunk, m )

	local errMsg, tracebackMsg
	local function _onError( msg )
		errMsg = msg
		tracebackMsg = debug.traceback(2)
	end

	local ok = xpcall( chunk, _onError )
	if ok then
		GameModules[ path ] = m
		return m
	else
		return nil, 'failtoload', errMsg, tracebackMsg
	end
end

--------------------------------------------------------------------
function requireGameModule( path )
	--todo: error handle
	local m = GameModules[ path ]
	if m then return m end
	return loadGameModule( path )	
end

--------------------------------------------------------------------
function releaseGameModule( path, releasedModules )
	releasedModules = releasedModules or {}
	_stat( 'release game module', path )
	local oldModule = GameModules[ path ]
	if not oldModule then
		_warn( 'can not release module', path )
		return nil
	end
	releasedModules[ path ] = true
	GameModules[ path ] = nil
	--TODO: emitSignal( 'module.released', path, oldModule )
	for requiredBy in pairs( oldModule.__REQUIREDBY ) do
		releaseGameModule( requiredBy, releasedModules )
	end
	return oldModule
end

--------------------------------------------------------------------
function getGameModule( path )
	return GameModules[ path ]
end

--------------------------------------------------------------------
function reloadGameModule( path )
	local released = {}
	releaseGameModule( path, released )
	for path in pairs( released ) do
		requireGameModule( path )
	end
end

