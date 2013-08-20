function getActiveScenes()
	local scenes = game.getActiveScenes()
	for k, s in pairs( scenes ) do
		if s.__editor_scene then scenes[ k ] = nil end
	end
	return scenes
end

function onEntityEvent( action, entity, scene, layer )
	if entity.__editor_entity then return end
	if action == 'add' then
		_owner:addEntity( entity, scene )
	elseif action == 'remove' then
		_owner:removeEntity( entity, scene )
	end
end

