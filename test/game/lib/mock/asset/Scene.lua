module 'mock'

local function loadComponent( data )
	local comTypeName = data['type']
	local comType = getComponetType( comTypeName )
	local com = comType()	
	return com
end

local function loadEntity( data )
	local entity
	local etype = data['type']
	if etype then
		--TODO: custom entity template?
	end
	entity = Entity()
	for i, comData in pairs( data['components'] ) do
		local com = loadComponent( comData )
		entity:attach( com )
	end

	for i, childData in pairs( data['children'] ) do
		local child = loadEntity( childData )
		entity:addChild( child )
	end
	return entity
end

function sceneLoader( node )
	local reg = getComponentRegistry()	
	local data = loadAssetDataTable( node:getAbsFilePath() )
	local scn = Scene()
	for i, entityData in ipairs( data['entities'] ) do
		local entity = loadEntity( entityData )
		scn:addEntity( entity )
	end
	return scn
end

registerAssetLoader( 'scene', sceneLoader )
