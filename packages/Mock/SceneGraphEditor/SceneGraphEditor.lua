
local function isEditorEntity( e )
	while e do
		if e.FLAG_EDITOR_OBJECT then return true end
		e = e.parent
	end
	return false
end

--------------------------------------------------------------------
CLASS:  SceneGraphEditor()

function SceneGraphEditor:openScene( path )
	local ctx = gii.getCurrentRenderContext()
	local scene = mock.loadAsset( path )
	scene.timer:attach( ctx.actionRoot )
	self.scene = scene
	self:postLoadScene()
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
	local data = mock.serializeScene( self.scene )
	self.scene:exit()
	self.scene = mock.deserializeScene( data )
	self:postLoadScene()
end

function SceneGraphEditor:postLoadScene()
	local scene = self.scene
	scene:setEntityListener( function( ... ) return self:onEntityEvent( ... ) end )
end


local function collectEntity( e, typeId, collection )
	if isEditorEntity( e ) then return end
	if isInstanceOf( e, typeId ) then
		collection[ e ] = true
	end
	for child in pairs( e.children ) do
		collectEntity( child, typeId, collection )
	end
end

local function collectComponent( entity, typeId, collection )
	if isEditorEntity( e ) then return end
	for com in pairs( entity.components ) do
		if isInstanceOf( com, typeId ) then
			collection[ e ] = entity
		end
	end
	for child in pairs( e.children ) do
		collectComponent( child, typeId, collection )
	end
end


function SceneGraphEditor:enumerateObjects( typeId )	
	local scene = self.scene
	if not scene then return nil end
	local result = {}
	--REMOVE: demo codes
	if typeId == mock.Entity then	
		local collection = {}	
		
		for e in pairs( scene.entities ) do
			collectEntity( e, typeId, collection )
		end

		for e in pairs( collection ) do
			table.insert( result, e )
		end
	end
	return result
end


function SceneGraphEditor:onEntityEvent( action, entity, scene, layer )
	if isEditorEntity( entity ) then return end
	if action == 'add' then
		_owner.tree:addNode( entity )
		gii.emitPythonSignal( 'scene.update', scene )
	elseif action == 'remove' then
		_owner.tree:removeNode( entity )
		gii.emitPythonSignal( 'scene.update', scene )
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
	self.entityName = option.name
end

function CmdCreateEntity:redo()
	local entType = mock.getEntityType( self.entityName )
	assert( entType )
	local entity = entType()
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


--------------------------------------------------------------------
function enumerateSceneObjects( enumerator, typeId, context )
	--if context~='scene_editor' then return nil end
	return editor:enumerateObjects( typeId )
end

function getSceneObjectRepr( enumerator, obj )
	if isInstanceOf( obj, mock.Entity ) then
		return obj:getName() or '<unnamed>'
	end
	--todo: component
	return nil
end

function getSceneObjectTypeRepr( enumerator, obj )
	local class = getClass( obj )
	if class then
		return class.__name
	end
	--todo: component
	return nil
end

gii.registerObjectEnumerator{
	name = 'scene_object_enumerator',
	enumerateObjects   = enumerateSceneObjects,
	getObjectRepr      = getSceneObjectRepr,
	getObjectTypeRepr  = getSceneObjectTypeRepr
}
