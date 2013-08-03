function getActiveScenes()
	local scenes = game.getActiveScenes()
	for k, s in pairs( scenes ) do
		if s._editorScene then scenes[ k ] = nil end
	end
	return scenes
end

function onEntityEvent( action, entity, scene, layer )
	if action == 'add' then
		_owner:addEntity( entity, scene )
	elseif action == 'remove' then
		_owner:removeEntity( entity, scene )
	end
end

function onSceneEnter( scn )
	_owner:addScene( scn )
	scn:setEntityListener( onEntityEvent )	
end

function onSceneExit( scn )
	_owner:removeScene( scn )
end

connectSignal( 'scene.enter', onSceneEnter )
connectSignal( 'scene.exit',  onSceneExit )
