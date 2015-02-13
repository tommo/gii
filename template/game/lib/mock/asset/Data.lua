module 'mock'

local function clearNullUserdata( t )
	for k,v in pairs( t ) do
		local tt = type( v )
		if tt == 'table' then
			clearNullUserdata( v )
		elseif tt == 'userdata' then
			t[ k ] = nil
		end
	end	
end

local function JSONDataLoader( node )
	local path = node:getObjectFile( 'data' )
	local data = loadAssetDataTable( path )

	local f = io.open( path, 'r' )
	if not f then
		_error( 'data file not found:' .. tostring( path ),2  )
		return nil
	end
	local text=f:read('*a')
	f:close()
	
	local data =  MOAIJsonParser.decode(text)
	if not data then 
		_error( 'json file not parsed: '..path )
		return nil
	end

	-- local dataGetterMT = {
	-- 	__index   = function( t, k )
	-- 		local v = data[ k ]
	-- 		print( k, type(v) )
	-- 		if type( v ) == 'userdata' then return nil end
	-- 		return v
	-- 	end;

	-- 	__newindex = function()
	-- 		error( 'attempt to write readonly data asset', 2 )
	-- 	end;

	-- 	__call = function( t, k, defaultValue )
	-- 		local v = data[ k ]
	-- 		if type( v ) == 'userdata' or v == nil then
	-- 			return defaultValue
	-- 		end
	-- 		return v
	-- 	end
	-- }
	-- return setmetatable( {}, dataGetterMT )
	clearNullUserdata( data )
	return data
end

registerAssetLoader( 'data_json',  JSONDataLoader )
registerAssetLoader( 'data_xls',   JSONDataLoader )
