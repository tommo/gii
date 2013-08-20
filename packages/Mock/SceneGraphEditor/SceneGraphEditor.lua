
--------------------------------------------------------------------
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

function openScene( path )
	local ctx = gii.getCurrentRenderContext()
	local scene = mock.loadAsset( path, { scene = scn } )
	scene.timer:attach( ctx.actionRoot )
	return scene
end

--------------------------------------------------------------------
CLASS: CmdCreateEntity ( EditorCommand )
	:register( 'scene_editor/create_entity' )

function CmdCreateEntity:redo()
	self.created = Entity()
	print 'adding'
end

function CmdCreateEntity:undo()
	print 'removing'
end

--------------------------------------------------------------------
CLASS: CmdRemoveEntity ( EditorCommand )
	:register( 'scene_editor/create_entity' )

function CmdRemoveEntity:init( option )
	self.target = option['target']
end

function CmdRemoveEntity:redo()
	print 'removing'
end

function CmdRemoveEntity:undo()
	print 're adding'
end


