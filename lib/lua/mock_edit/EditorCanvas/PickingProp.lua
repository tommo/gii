module 'mock_edit'

--------------------------------------------------------------------

CLASS: PickingManager ()
	:MODEL{}

function PickingManager:__init()
	self.pickingPropToEntity = {}
	self.entityToPickingProps = {} 
end

function PickingManager:addPickingProp( srcEntity, prop )
	self.pickingPropToEntity[ prop ] = srcEntity
	local props = self.entityToPickingProps[ srcEntity ]
	if not props then
		props = {}
		self.entityToPickingProps[ srcEntity ] = props
	end
	props[ prop ] = true
end

function PickingManager:removePickingProp( prop )
	local src = self.pickingPropToEntity[ prop ]
	self.pickingPropToEntity[ prop ] = nil
	local props = self.entityToPickingProps[ src ]
	if props then props[ prop ] = nil end
end

function PickingManager:removeEntity( srcEntity )
	local props = self.entityToPickingProps[ srcEntity ]
	if not props then return end
	local pickingPropToEntity = self.pickingPropToEntity
	for prop in pairs( props ) do
		pickingPropToEntity[ prop ] = nil
	end
	self.entityToPickingProps[ srcEntity ] = nil
end


function PickingManager:setTargetScene( scene )
	self.targetScene = scene
	--scan
	for e in pairs( self.targetScene.entities ) do
		self:buildForEntity( e, false )
	end
end

function PickingManager:onEntityEvent( ev, entity, com )
	if ev == 'clear' then
		self:clear()
		return
	end

	if entity.FLAG_EDITOR_OBJECT then return end

	if ev == 'add' then
		self:buildForEntity( entity ) 
	elseif ev == 'remove' then
		self:removeForEntity( entity )
	elseif ev == 'attach' then
		if self:isEntityPickable( entity ) then
			self:buildForObject( com, entity )
		end
	elseif ev == 'detach' then
		self:removeForObject( com, entity )
	end

end

function PickingManager:isEntityPickable( ent )
	if not ent:isVisible() then return false end
	if ent.FLAG_EDITOR_OBJECT then
		local isPickable = ent.isPickable
		if not isPickable then return false end
		if not isPickable( ent ) then return false end
	end
	return true
end


function PickingManager:buildForEntity( ent )
	if not self:isEntityPickable( ent ) then return end
	self:buildForObject( ent, ent )
	for com in pairs( ent.components ) do
		if not ( com.FLAG_EDITOR_OBJECT ) then
			self:buildForObject( com, ent )
		end
	end
	for child in pairs( ent.children ) do
		self:buildForEntity( child )
	end
end

function PickingManager:buildForObject( obj, srcEntity )
	getPickingProp = obj.getPickingProp
	if getPickingProp then
		local prop = getPickingProp( obj )
		if prop then
			self:addPickingProp( srcEntity, prop )
		end
	end
end

function PickingManager:removeForObject( obj, srcEntity )
	getPickingProp = obj.getPickingProp
	if getPickingProp then
		local prop = getPickingProp( obj )
		if prop then
			self:removePickingProp( prop )
		end
	end
end

function PickingManager:removeForEntity( ent )
	for com in pairs( ent.components ) do
		self:removeForObject( com, ent )
	end
	for child in pairs( ent.children ) do
		self:removeForEntity( child )
	end
	self:removeForObject( ent, ent )
	self:removeEntity( ent )
end

function PickingManager:clear()
	self.pickingPropToEntity = {}
	self.entityToPickingProps = {}
end

local defaultSortMode = MOAILayer.SORT_Z_ASCENDING

function PickingManager:getVisibleLayers()
	local layers = {}
	for i, layer in ipairs( self.targetScene.layers ) do
		local srcLayer = layer.source
		if srcLayer:isEditorVisible() then
			table.insert( layers, layer )
		end
	end
	return table.reversed( layers )
end

function PickingManager:pickPoint( x, y, pad )
	-- print( 'picking', x, y )
	local pickingPropToEntity = self.pickingPropToEntity

	for i, layer in ipairs( self:getVisibleLayers() ) do
		local partition = layer:getPartition()
		local result = { partition:propListForRay( x, y, -1000, 0, 0, 1, defaultSortMode ) }
		for i, prop in ipairs( result ) do
			local ent = pickingPropToEntity[ prop ]
			if ent and ent.getPickingTarget then
				ent = ent:getPickingTarget()
			end
			if ent and ent:isVisible() then --TODO: sorting & sub picking
				-- print( ent:getName() )
				return { ent }
			end
		end
	end

	return {}
end

function PickingManager:pickRect( x0, y0, x1, y1, pad )
	-- print( 'picking rect', x0, y0, x1, y1 )
	local picked = {}
	local pickingPropToEntity = self.pickingPropToEntity

	for i, layer in ipairs( self:getVisibleLayers() ) do
		local partition = layer:getPartition()
		local result = { partition:propListForRect( x0, y0, x1, y1, defaultSortMode ) }
		for i, prop in ipairs( result ) do
			local ent = pickingPropToEntity[ prop ]
			if ent then --TODO: sub picking
				if ent.getPickingTarget then
					ent = ent:getPickingTarget()
				end
				if ent:isVisible() then
					picked[ ent ] = true
				end
				-- print( ent:getName() )
			end
		end
	end

	return table.keys( picked )
end
