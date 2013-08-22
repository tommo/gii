module 'gii'


local GameModules = {}

local callbackModuleRelease = {}
local callbackModuleLoad    = {}

function addGameModuleReleaseListener( func )
	table.insert( callbackModuleRelease, func )
end

function addGameModuleLoadListener( func )
	table.insert( callbackModuleLoad, func )
end

function registerGameModule( name, m )
	GameModules[ name ] = m
end

function findGameModule( name )
	return GameModules[ name ]
end

function hasGameModule( name )
	return GameModules[ name ] ~= nil
end
--[[
	create a envrionment
]]

local gameScriptPaths = {
	GII_PROJECT_SCRIPT_PATH .. '/?.lua',
	-- GII_PROJECT_SCRIPT_PATH .. '/?/init.lua',
	GII_PROJECT_ASSET_PATH .. '/?.lua',
	-- GII_PROJECT_ASSET_PATH .. '/?/init.lua'
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
local _createEmptyModule, _loadGameModule, _requireGameModule

local _errorInfos = {}
local function flushErrorInfo()
	local infos = _errorInfos
	_errorInfos = {}
	return infos
end

local function pushErrorInfo( data )
	table.insert( _errorInfos, data )
end

local _require = require
function _createEmptyModule( path, fullpath )
	local m = {
		_NAME   = path,
		_PATH   = path,
		_SOURCE = fullpath,
		__REQUIRES    = {},
		__REQUIREDBY  = {}
	}

	m.require = function( path, ... )
		local loaded, errType, errMsg, tracebackMsg = _requireGameModule( path )
		if loaded then 
			m.__REQUIRES[ path ] = true
			loaded.__REQUIREDBY[ m._PATH ] = true
			return loaded
		end
		if errType ~= 'notfound' then
			-- print( errMsg )
			-- if tracebackMsg then print( tracebackMsg ) end
			error( 'error loading game module', 2 )
		end
		return _require( path, ... )
	end

	return setmetatable( m, GameModuleMT )
end

--------------------------------------------------------------------
function _requireGameModule( path )
	local m = GameModules[ path ]
	if m then return m end
	return _loadGameModule( path )	
end

--------------------------------------------------------------------

function _loadGameModule( path )
	local fullpath = searchFile( path )
	if not fullpath then
		return nil, 'notfound'
	end
	_stat( 'loading module from', fullpath )
	local chunk, compileErr = loadfile( fullpath )
	if not chunk then
		pushErrorInfo{
			path = path,
			fullpath = fullpath,
			errtype =	'compile',
			msg     = compileErr
		}
		return nil, 'failtocompile', compileErr
	end
	local m = _createEmptyModule( path, fullpath )
	setfenv( chunk, m )

	local errMsg, tracebackMsg
	local function _onError( msg )
		errMsg = msg
		tracebackMsg = debug.traceback(2)
	end

	local ok = xpcall( chunk, _onError )
	if ok then
		registerGameModule( path, m )
		for i, func in ipairs( callbackModuleLoad ) do
			func( path, m )
		end
		return m
	else
		pushErrorInfo{
			path      = path,
			fullpath  = fullpath,
			errtype   =	'load',
			msg       = errMsg,
			traceback = tracebackMsg
		}
		return nil, 'failtoload', errMsg, tracebackMsg
	end
end

--------------------------------------------------------------------
function loadGameModule( path, flushError )
	local loaded, errType, errMsg, tracebackMsg = _requireGameModule( path )
	
	if loaded then return loaded, {} end

	if flushError then
		return false, flushErrorInfo()
	else
		return false, _errorInfos
	end

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
	for i, func in ipairs( callbackModuleRelease ) do
		func( path, oldModule )
	end
	GameModules[ path ] = nil
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
	flushErrorInfo()
	--release
	local releasedModules = {}
	releaseGameModule( path, releasedModules )
	--reload
	for path1 in pairs( releasedModules ) do
		loadGameModule( path1 )
	end
	local m = findGameModule( path )
	return m, flushErrorInfo()
end

---------------------------------------------------------------------
function unloadGameModule( path )
	flushErrorInfo()
	local released = {}
	releaseGameModule( path, released )
	for path1 in pairs( released ) do
		if path1 ~= path then
			loadGameModule( path1 )
		end
	end
	return flushErrorInfo()
end

