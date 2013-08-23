
--------------------------------------------------------------------
CLASS:  SceneGraphEditor()

function SceneGraphEditor:openScene( path )
	local ctx = gii.getCurrentRenderContext()
	local scene = mock.loadAsset( path )
	scene.timer:attach( ctx.actionRoot )
	self.scene = scene
	scene:setEntityListener( function( ... ) return self:onEntityEvent( ... ) end )
	return scene
end

function SceneGraphEditor:closeScene()
	if not self.scene then return end
	self.scene:exitNow()
	self.scene = false
end

function SceneGraphEditor:saveScene( path )
	if not self.scene then return false end
	mock.serializeSceneToFile( self.scene, path )
	return true
end

function SceneGraphEditor:refreshScene()
end

local function isEditorEntity( e )
	while e do
		if e.FLAG_EDITOR_OBJECT then return true end
		e = e.parent
	end
	return false
end

function SceneGraphEditor:onEntityEvent( action, entity, scene, layer )
	if isEditorEntity( entity ) then return end
	if action == 'add' then
		_owner.tree:addNode( entity )
	elseif action == 'remove' then
		_owner.tree:removeNode( entity )
	end

end

editor = SceneGraphEditor()

--------------------------------------------------------------------
function getActiveScenes()
	local scenes = game.getActiveScenes()
	for k, s in pairs( scenes ) do
		if s.__editor_scene then scenes[ k ] = nil end
	end
	return scenes
end



--------------------------------------------------------------------
CLASS: CmdCreateEntity ( EditorCommand )
	:register( 'scene_editor/create_entity' )

function CmdCreateEntity:init( option )
	if option.good then print "shit" end
end

function CmdCreateEntity:redo()
	local entity = Entity()
	self.created = entity
	editor.scene:addEntity( entity )
end

function CmdCreateEntity:undo()
	self.created:destroy()
end

--------------------------------------------------------------------
CLASS: CmdRemoveEntity ( EditorCommand )
	:register( 'scene_editor/remove_entity' )

function CmdRemoveEntity:init( option )
	self.target = option['target']
end

function CmdRemoveEntity:redo()
	self.target:destroy()
end

function CmdRemoveEntity:undo()
	--todo:
end


