module 'mock'
--------------------------------------------------------------------
--Atlas conversion
--------------------------------------------------------------------
local gsplit, trim = string.gsplit, string.trim

local function parseTuple( s )
	local t = {}
	for part in gsplit( s, ',' ) do
		part = trim( part )
		local v = tonumber( part )
		if not v then
			if part == 'true' then
				v = true
			elseif part == 'false' then
				v = false
			else
				v = part
			end
		end
		table.insert( t, v )
	end
	if #t > 1 then return t else return t[1] end
end

local function parseLine( l )
	local indent, tag, data = l:match( '( ?)(%w+): (.+)')
	if not tag then
		return 'line', l
	else
		return 'value', #indent > 0, tag, parseTuple( data )
	end
end

local function parseAtlas( data )
	local pack = {
		pages = {}
	}
	local currentRegion = false
	local currentPage   = false
	for line in string.gsplit( data ) do
		local ltype, sub, tag, data = parseLine( line )
		if ltype == 'line' then
			if line == '' then --clear current page
				currentPage = false
			else 
				if not currentPage then --new pag3
					currentPage = {
						texture = line;
						regions = {}
					}
					table.insert( pack.pages, currentPage )
				else --new region
					currentRegion = {}
					currentPage.regions[ line ] = currentRegion
				end
			end
		else
			if sub then --region
				currentRegion[ tag ] = data
			else
				currentPage[ tag ] = data
			end
		end
	end
	return pack
end

function convertSpineAtlasToPrebuiltAtlas( atlasName )
	local f = io.open( atlasName, 'r' )
	local data = f:read( '*a' )
	f:close()
	local pack = parseAtlas( data )
	local atlas = PrebuiltAtlas()
	for i, pageData in ipairs( pack.pages ) do
		local page = atlas:addPage()
		page.texture   = pageData.texture
		page.source    = pageData.texture
		if pageData.size then
			page.w, page.h = unpack( pageData.size )
		else
			page.w, page.h = -1, -1
		end
		for name, itemData in pairs( pageData.regions ) do
			local item = page:addItem()
			item.name    = name
			item.rotated = itemData.rotate
			item.w,  item.h  = unpack( itemData.size )
			item.ow, item.oh = unpack( itemData.orig )
			item.x,  item.y  = unpack( itemData.xy )
			item.ox, item.oy = unpack( itemData.offset )
		end
	end
	return atlas
end

--------------------------------------------------------------------
--LOADERS
--------------------------------------------------------------------
function loadSpineAtlas( node )
	local atlasNodePath = node:getChildPath( node:getBaseName() .. '_spine_atlas' )
	local atlasTexture, atlasNode = loadAsset( atlasNodePath, { skip_parent = true } )
	local atlas      = atlasTexture:getPrebuiltAtlas()
	local spineAtlas = MOAISpineAtlas.new()
	--load atlas items
	local scale = atlasTexture:getScale()	
	for i, page in ipairs( atlas.pages ) do
		if #page.items > 0 then
			local texture = page:getMoaiTexture()
			for j, item in ipairs( page.items ) do
				spineAtlas:addRegion( 
					item.name,
					texture,
					item.w/scale, item.h/scale,
					item.ow, item.oh,
					item.ox, item.oy,
					item.x/scale, item.y/scale,
					-1,
					item.rotated,
					page.w/scale, page.h/scale
				)
			end
		end
	end
	spineAtlas._texture = atlasTexture
	return spineAtlas
end


function SpineJSONLoader( node )
	local jsonPath  = node:getAbsObjectFile( 'skel' )
	local atlas     = loadSpineAtlas( node ) --test	
	local skeletonData = MOAISpineSkeletonData.new()
	skeletonData:loadWithAtlas( jsonPath, atlas )
	skeletonData.atlas = atlas	
	skeletonData._animationTable = skeletonData:getAnimationNames()
	skeletonData._slotTable      = skeletonData:getSlotNames()
	skeletonData._skinTable      = skeletonData:getSkinNames()
	skeletonData._boneTable      = skeletonData:getBoneNames()

	skeletonData._jsonPath = jsonPath
	
	return skeletonData
end

function findSpineEventFrame( data, animName, eventName )
	local found = {}
	local jsonData = data._jsonData
	local animations = jsonData['animations']
	local anim = animations[ animName ]
	if not anim then return nil end
	local events = anim['events']
	if not events then return nil end
	for i, f in ipairs( events ) do
		if f['name'] == eventName then
			table.insert( found, f )
		end
	end
	return unpack( found )
end

registerAssetLoader( 'spine', SpineJSONLoader )
--------------------------------------------------------------------
