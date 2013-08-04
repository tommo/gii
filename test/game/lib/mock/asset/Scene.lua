module 'mock'

local function loadComponent( data )
	local comTypeName = data['type']
	local comType = getComponentType( comTypeName )
	local com = comType()	
	return com
end

local function loadEntity( data )
	local entity
	local entityTypeName = data['type']
	if entityTypeName then --custom entity template?
		--TODO: 
		local entityType = getEntityType( entityTypeName )
		entity = entityType()
	else --entity from configuration
		entity = Entity()
	end
	--load component
	local components =  data['components']
	if components then
		for i, comData in pairs( components ) do
			local com = loadComponent( comData )
			entity:attach( com )
		end
	end
	--load children
	local children =  data['children']
	if children then
		for i, childData in pairs( children ) do
			local child = loadEntity( childData )
			entity:addChild( child )
		end
	end		
	if data['name'] then entity:setName( data['name'] ) end
	return entity
end

function sceneLoader( node )
	local reg = getComponentRegistry()	
	local data = loadAssetDataTable( node:getAbsFilePath() )
	local scn = Scene()
	--configuration
	scn:enter()
	--entities
	for i, entityData in ipairs( data['entities'] ) do
		local entity = loadEntity( entityData )
		scn:addEntity( entity )
	end
	return scn
end

registerAssetLoader( 'scene', sceneLoader )
