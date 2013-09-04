
local function isEditorEntity( e )
	while e do
		if e.FLAG_EDITOR_OBJECT then return true end
		e = e.parent
	end
	return false
end

--------------------------------------------------------------------
CLASS:  SceneGraphEditor()

function SceneGraphEditor:__init()
	self.failedRefreshData = false
end

function SceneGraphEditor:openScene( path )
	local ctx = gii.getCurrentRenderContext()
	gii.setCurrentRenderContextActionRoot( game:getActionRoot() )
	local scene = mock.loadAsset( path )
	-- scene.timer:attach( ctx.actionRoot )
	self.scene = scene
	self:postLoadScene()
	return scene
end

function SceneGraphEditor:closeScene()
	if not self.scene then return end
	self.scene:exitNow()
	self.scene = false
	mock.game:resetClock()
end

function SceneGraphEditor:saveScene( path )
	if not self.scene then return false end
	mock.serializeSceneToFile( self.scene, path )
	return true
end

function SceneGraphEditor:refreshScene()
	local data = self.failedRefreshData or mock.serializeScene( self.scene )
	self.scene:stop()
	self.scene:clear( true )
	mock.game:resetClock()
	if pcall( mock.deserializeScene, data, self.scene ) then
		self.failedRefreshData = false
		self:postLoadScene()
	else
		self.failedRefreshData = data
	end
end

function SceneGraphEditor:postLoadScene()
	local scene = self.scene
	scene:setEntityListener( function( ... ) return self:onEntityEvent( ... ) end )
end

function SceneGraphEditor:retainScene()
	self.retainedSceneData = mock.serializeScene( self.scene )
end

function SceneGraphEditor:restoreScene()
	if not self.retainedSceneData then return end
	self.scene:stop()
	self.scene:clear( true )
	mock.game:resetClock()
	if pcall( mock.deserializeScene, self.retainedSceneData, self.scene ) then
		self.retainedSceneData = false
		self:postLoadScene()
	else
		self.failedRefreshData = self.retainedSceneData
	end
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
		gii.emitPythonSignal( 'scene.update' )
	elseif action == 'remove' then
		_owner.tree:removeNode( entity )
		gii.emitPythonSignal( 'scene.update' )
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


--------------------------------------------------------------------
function enumerateLayers( enumerator, typeId, context )
	--if context~='scene_editor' then return nil end
	if typeId ~= 'layer' then return nil end
	local r = {}
	for i, l in ipairs( game.layers ) do
		if l.name ~= '_GII_EDITOR_LAYER' then
			table.insert( r, l.name )
		end
	end
	return r
end

function getLayerRepr( enumerator, obj )
	return obj
end

function getLayerTypeRepr( enumerator, obj )
	return 'Layer'
end

gii.registerObjectEnumerator{
	name = 'layer_enumerator',
	enumerateObjects   = enumerateLayers,
	getObjectRepr      = getLayerRepr,
	getObjectTypeRepr  = getLayerTypeRepr
}


--------------------------------------------------------------------
--- COMMAND
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
	gii.emitPythonSignal('entity.added', self.created )
end

function CmdCreateEntity:undo()
	self.created:destroyNow()
	gii.emitPythonSignal('entity.removed', self.created )
end

--------------------------------------------------------------------
CLASS: CmdRemoveEntity ( EditorCommand )
	:register( 'scene_editor/remove_entity' )

function CmdRemoveEntity:init( option )
	local target = gii.getSelection( 'scene' )[1]
	if not isInstanceOf( target, mock.Entity ) then return false end
	self.selection = gii.getSelection( 'scene' )
end

function CmdRemoveEntity:redo()
	for _, target in ipairs( self.selection ) do
		if target.scene then 
			target:destroyNow()
			gii.emitPythonSignal('entity.removed', target )
		end
	end
end

function CmdRemoveEntity:undo()
	--todo: RESTORE deleted
	-- gii.emitPythonSignal('entity.added', self.created )
end

--------------------------------------------------------------------
CLASS: CmdCreateComponent ( EditorCommand )
	:register( 'scene_editor/create_component' )

function CmdCreateComponent:init( option )
	self.componentName = option.name	
	local target = gii.getSelection( 'scene' )[1]
	if not isInstanceOf( target, mock.Entity ) then return false end
	self.targetEntity  = target
end

function CmdCreateComponent:redo()	
	local entType = mock.getComponentType( self.componentName )
	assert( entType )
	local component = entType()
	self.createdComponent = component
	self.targetEntity:attach( component )
	gii.gii.emitPythonSignal( 'component.added', component, self.targetEntity )	
end

function CmdCreateComponent:undo()
	self.targetEntity:detach( self.createdComponent )
	gii.gii.emitPythonSignal( 'component.removed', component, self.targetEntity )	
end

--------------------------------------------------------------------
CLASS: CmdRemoveComponent ( EditorCommand )
	:register( 'scene_editor/remove_component' )

function CmdRemoveComponent:init( option )
	self.target = option['target']
end

function CmdRemoveComponent:redo()
	--todo
	-- self.target:destroy()
end

function CmdRemoveComponent:undo()
	--todo:
end


--------------------------------------------------------------------
CLASS: CmdCloneEntity ( EditorCommand )
	:register( 'scene_editor/clone_entity' )

function CmdCloneEntity:init( option )
	local target = gii.getSelection( 'scene' )[1]
	if not isInstanceOf( target, mock.Entity ) then return false end
	self.target = target
end

function CmdCloneEntity:redo()
	self.created = mock.cloneEntity( self.target )
	local parent = self.target.parent
	if parent then
		parent:addChild( self.created )
	else
		editor.scene:addEntity( self.created )
	end
	gii.emitPythonSignal('entity.added', self.created )
end

function CmdCloneEntity:undo()
	--todo:
	gii.emitPythonSignal('entity.removed', self.created )
	self.created:destroyNow()
end

--------------------------------------------------------------------
CLASS: CmdReparentEntity ( EditorCommand )
	:register( 'scene_editor/reparent_entity' )

function CmdReparentEntity:init( option )
	self.target = option['target']
	self.children = gii.getSelection( 'scene' )
	self.oldParents = {}
end

function CmdReparentEntity:redo()
	for i, e in ipairs( self.children ) do
		local e1 = mock.cloneEntity(e)
		self.target:addChild( e1 )
		e:destroyNow()
		print( self.target.name, e.name )
	end	
end

function CmdReparentEntity:undo()
	--todo:
end

