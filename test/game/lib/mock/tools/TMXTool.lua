local function trynumber(v)
	return tonumber(v) or v
end

local function copyNode(s,x)
	local attr=x.attributes
	if attr then
		for k,v in pairs(attr) do
			s[k]=trynumber(v)
		end
	end
end

local function parseTileSet(node)
	local set={}
	copyNode(set,node)
	local image=node.children['image'][1]
	assert(image, 'not support tsx')
	set.source=image.attributes['source']
	--todo:property
	return set
end

local function parseProperties(node)
	local l={}
	for i,n in ipairs(node.children['property']) do
		local attr=n.attributes
		l[n['name']]=trynumber(n['value'])
	end
	return l
end

local function parseObject(node)
	local obj={}
	copyNode(obj,node)

	if obj.children and obj.children['properties'] then
		obj.properties=parseProperties(obj.children['properties'][1])
	end
	return obj
end

local function parseObjectGroup(node)
	local group={}
	copyNode(group, node)
	for i,n in ipairs(node.children['object']) do
		group[i]=parseObject(n)
	end
	return group
end

local function parseTileLayer(node)
	local layer={}
	copyNode(layer,node)
	local data=node.children['data'][1]
	local encoding=data.attributes['encoding']
	if encoding=='csv' then
		layer.tiles=loadstring('return {'..data.value..'}')()
	elseif encoding=='base64' then
		--reference: TMXMapLoader from Hanappe 
		local decoded=MOAIDataBuffer.base64Decode(data.value)
		if data.attributes['compression'] then
			decoded=MOAIDataBuffer.inflate(decoded,47)
		end
		local tileCount=#decoded/4
		local t={}
		for i=1, tileCount do
			local start=(i-1)*4 + 1
			local a0,a1,a2,a3 = string.byte(decoded, start, start+3)
			t[i] = a0 + a1 * 2^8 + a2 * 2^16 + a3 * 2^32
		end
		layer.tiles=t
	else
		error('unknown encoding')
	end
	return layer
end

local function parseMap(node)
	assert(node.type=='map')
	local map={}
	copyNode(map,node)
	
	local tileSets={}
	local objectGroups={}
	local tileLayers={}

	if node.children['tileset'] then
		for i, n in ipairs(node.children['tileset']) do
		   tileSets[i]=parseTileSet(n)
		end
	end
	if node.children['objectgroup'] then
		for i, n in ipairs(node.children['objectgroup']) do
			objectGroups[i]=parseObjectGroup(n)
		end
	end
	if node.children['layer'] then
		for i, n in ipairs(node.children['layer']) do
		   tileLayers[i]=parseTileLayer(n)
		end
	end
	map.tileSets=tileSets
	map.tileLayers=tileLayers
	map.objectGroups=objectGroups
	return map
end


local function tmx2lua(file)
	local xml=MOAIXmlParser.parseFile(file)
	return parseMap(xml)
end

CLASS: TMXTool ()
function TMXTool:load(tmxfile)
	local data=tmx2lua(tmxfile)
	self.data=data or false
end

function TMXTool:getObjectLayers()
	return self.data.objectGroups
end

function TMXTool:getTileLayers()
	return self.data.tileLayers
end

function TMXTool:findObject(layerId, objId)
	local layer=self:findObjectLayer(layerId)
	if not layer then return nil end
	for i, obj in ipairs(layer) do
		if obj.name==objId then
			return obj
		end
	end
	return nil
end

function TMXTool:getObjectLayerCount()
	assert(self.data,'not loaded')
	if not self.data then return 0 end
	return #self.data.objectGroups
end

function TMXTool:getTileLayerCount()
	assert(self.data,'not loaded')
	if not self.data then return 0 end
	return #self.data.tileLayers
end

function TMXTool:findTileLayer(id)
	if type(id)=='number' then
		return self.data.tileLayers[id]
	elseif type(id)=='string' then
		for i,l in ipairs(self.data.tileLayers) do
			if l.name==id then return l end
		end
		return nil
	else
		error('layer id unknown')
	end
end

function TMXTool:findObjectLayer(id)
	if type(id)=='number' then
		return self.data.objectGroups[id]
	elseif type(id)=='string' then
		for i,l in ipairs(self.data.objectGroups) do
			if l.name==id then return l end
		end
		return nil
	else
		error('layer id unknown')
	end
end

function TMXTool:buildGrid(tileLayerId)
	assert(self.data,'not loaded')
	local layer=assert(self:findTileLayer(tileLayerId), 'layer not found')
	local tiles=layer.tiles
	if not tiles then return nil end
	local grid=MOAIGrid.new()
	local w,h=self.data.width, self.data.height
	grid:setSize(w,h, self.data.tilewidth,self.data.tileheight)
	local ptr=1
	for y=h,1 ,-1 do
		for x=1,w do
			grid:setTile(x,y,tiles[ptr]) --TODO: multiple tileset support ?
			ptr=ptr+1
		end
	end
	return grid
end

function TMXTool:getMapSize()
	assert(self.data,'not loaded')
	return self.data.width, self.data.height
end

function TMXTool:getMapPixelSize()
	assert(self.data,'not loaded')
	return self.data.width*self.data.tilewidth, self.data.height*self.data.tileheight
end


function TMXTool:getTileSize()
	assert(self.data,'not loaded')
	return self.data.tilewidth, self.data.tileheight
end

