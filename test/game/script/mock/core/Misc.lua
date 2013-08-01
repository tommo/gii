module 'mock'


---------Layer
local moaiLayers={}

local function sortLayer(a,b)	
	local pa = a.priority or 0
	local pb = b.priority or 0
	if pa  < pb then return true end
	if pa == pb then return a.__id < b.__id end
end

local function updateRenderTable()
	table.sort( moaiLayers, sortLayer )
	local renderBuffer = MOAIGfxDevice.getFrameBuffer()
	renderBuffer:setRenderTable( moaiLayers )
end

local function addMoaiLayer( layer )
	table.insert( moaiLayers, layer )
	updateRenderTable()
	return l
end

local function removeMoaiLayer( toRemove )
		for i, layer in pairs( moaiLayers ) do
			if layer == toRemove then 
				table.remove( moaiLayers, i )		
				break 
			end
		end
end