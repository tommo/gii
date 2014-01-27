local generateGUID = MOAIEnvironment.generateGUID

local function findTopLevelEntities( entities )
	local found = {}
	for e in pairs( entities ) do
		local p = e.parent
		local isTop = true
		while p do
			if entities[ p ] then isTop = false break end
			p = p.parent
		end
		if isTop then found[e] = true end
	end
	return found
end

local function getTopLevelEntitySelection()
	local entities = {}
	for i, e in ipairs( gii.getSelection( 'scene' ) ) do
		if isInstanceOf( e, mock.Entity ) then 
			entities[ e ] = true
		end
	end
	return findTopLevelEntities( entities )
end

local function isEditorEntity( e )
	while e do
		if e.FLAG_EDITOR_OBJECT or e.FLAG_INTERNAL then return true end
		e = e.parent
	end
	return false
end

local function affirmGUID( entity )
	if not entity.__guid then
		entity.__guid = generateGUID()
	end
	for com in pairs( entity.components ) do
		if not com.__guid then
			com.__guid = generateGUID()
		end
	end
	for child in pairs( entity.children ) do
		affirmGUID( child )
	end
end

--------------------------------------------------------------------
CLASS:  SceneGraphEditor()

function SceneGraphEditor:__init()
	self.failedRefreshData = false
	connectSignalMethod( 'mainscene.open',  self, 'onMainSceneOpen' )
	connectSignalMethod( 'mainscene.close', self, 'onMainSceneClose' )
end

function SceneGraphEditor:getScene()
end

function SceneGraphEditor:getScene()
	return self.scene
end

function SceneGraphEditor:openScene( path )
	local scene = mock.game:openSceneByPath( path ) --dont start
	assert( scene )
	self.scene = scene
	--affirm guid
	for entity in pairs( scene.entities ) do
		affirmGUID( entity )
	end
	--
	self:postLoadScene()
	print('open!!!')
	return scene
end

function SceneGraphEditor:closeScene()
	if not self.scene then return end
	self:clearScene()
	self.scene = false
	self.retainedSceneData = false
	self.retainedSceneSelection = false
	mock.game:resetClock()
end

function SceneGraphEditor:saveScene( path )
	if not self.scene then return false end
	mock.serializeSceneToFile( self.scene, path )
	return true
end

function SceneGraphEditor:clearScene( keepEditorEntity )
	-- _collectgarbage( 'stop' )
	self.scene:clear( keepEditorEntity )
	self.scene:setEntityListener( false )
	-- _collectgarbage( 'restart' )
end

function SceneGraphEditor:refreshScene()
	self:retainScene()
	self:clearScene( true )
	local r = self:restoreScene()	
	return r
end

function SceneGraphEditor:postLoadScene()
	local scene = self.scene
	scene:setEntityListener( function( action, ... ) return self:onEntityEvent( action, ... ) end )
end


function SceneGraphEditor:startScenePreview()
	-- _collectgarbage( 'collect' )
	GIIHelper.forceGC()
	mock.game:start()
end

function SceneGraphEditor:stopScenePreview()
	-- _collectgarbage( 'collect' )
	GIIHelper.forceGC()
	mock.game:stop()
	--recover layer visiblity
	for i, l in pairs( mock.game:getLayers() ) do 
		l:setVisible( true )
	end

end

function SceneGraphEditor:retainScene()
	--keep current selection
	local guids = {}
	for i, e in ipairs( gii.getSelection( 'scene' ) ) do
		guids[ i ] = e.__guid
	end
	self.retainedSceneSelection = guids
	self.retainedSceneData = mock.serializeScene( self.scene )
	--keep node fold state
end


function SceneGraphEditor:restoreScene()
	if not self.retainedSceneData then return true end
	if pcall( mock.deserializeScene, self.retainedSceneData, self.scene ) then
		self.retainedSceneData = false
		self:postLoadScene()		
		_owner.tree:rebuild()
		local result = {}
		for i, guid in ipairs( self.retainedSceneSelection ) do
			local e = self:findEntityByGUID( guid )
			if e then table.insert( result, e ) end			
		end
		gii.changeSelection( 'scene', unpack( result ) )
		self.retainedSceneSelection = false		
		return true
	else
		self.failedRefreshData = self.retainedSceneData
		return false
	end
end

function SceneGraphEditor:findEntityByGUID( id )
	local result = false
	for e in pairs( self.scene.entities ) do
		if e.__guid == id then
			result = e
		end
	end
	return result
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
	if isEditorEntity( entity ) then return end
	for com in pairs( entity.components ) do
		if not com.FLAG_INTERNAL and isInstanceOf( com, typeId ) then
			collection[ com ] = true
		end
	end
	for child in pairs( entity.children ) do
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

	else
		local collection = {}	
		for e in pairs( scene.entities ) do
			collectComponent( e, typeId, collection )
		end

		for e in pairs( collection ) do
			table.insert( result, e )
		end
	end
	return result
end


function SceneGraphEditor:onEntityEvent( action, entity, com )
	emitSignal( 'scene.entity_event', action, entity, com )
	
	if action == 'clear' then
		return gii.emitPythonSignal( 'scene.clear' )
	end

	if isEditorEntity( entity ) then return end

	if action == 'add' then
		_owner.tree:addNode( entity )
		gii.emitPythonSignal( 'scene.update' )
	elseif action == 'remove' then
		_owner.tree:removeNode( entity )
		gii.emitPythonSignal( 'scene.update' )
	end

end

function SceneGraphEditor:onMainSceneOpen( scn )
	gii.emitPythonSignal( 'scene.change' )
end

function SceneGraphEditor:onMainSceneClose( scn )
	gii.emitPythonSignal( 'scene.change' )
end

editor = SceneGraphEditor()

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
	local ent = obj._entity
	if ent then
		return ent:getName() or '<unnamed>'
	end
	return nil
end

function getSceneObjectTypeRepr( enumerator, obj )
	local class = getClass( obj )
	if class then
		return class.__name
	end
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
CLASS: CmdCreateEntityBase ( mock_edit.EditorCommand )
function CmdCreateEntityBase:init( option )
	local parent = gii.getSelection( 'scene' )[1]
	if isInstanceOf( parent, mock.Entity ) then
		self.parentEntity = parent
	end
end

function CmdCreateEntityBase:createEntity()
end

function CmdCreateEntityBase:redo()
	local entity = self:createEntity()
	if not entity then return false end
	entity.__guid = generateGUID()
	self.created = entity
	if self.parentEntity then
		self.parentEntity:addChild( entity )
	else
		editor.scene:addEntity( entity )
	end
	gii.emitPythonSignal( 'entity.added', self.created, 'new' )
end

function CmdCreateEntityBase:undo()
	self.created:destroyNow()
	gii.emitPythonSignal( 'entity.removed', self.created )
end

--------------------------------------------------------------------
CLASS: CmdCreateEntity ( CmdCreateEntityBase )
	:register( 'scene_editor/create_entity' )

function CmdCreateEntity:init( option )
	CmdCreateEntityBase.init( self, option )
	self.entityName = option.name
end

function CmdCreateEntity:createEntity()
	local entType = mock.getEntityType( self.entityName )
	assert( entType )
	local e = entType()
	if not e.name then e.name = self.entityName end
	return e
end

function CmdCreateEntity:undo()
	self.created:destroyWithChildrenNow()
	gii.emitPythonSignal('entity.removed', self.created )
end

--------------------------------------------------------------------
CLASS: CmdRemoveEntity ( mock_edit.EditorCommand )
	:register( 'scene_editor/remove_entity' )

function CmdRemoveEntity:init( option )
	local target = gii.getSelection( 'scene' )[1]
	if not isInstanceOf( target, mock.Entity ) then return false end
	self.selection = gii.getSelection( 'scene' )
end

function CmdRemoveEntity:redo()
	for _, target in ipairs( self.selection ) do
		if target.scene then 
			target:destroyWithChildrenNow()
			gii.emitPythonSignal('entity.removed', target )
		end
	end
end

function CmdRemoveEntity:undo()
	--todo: RESTORE deleted
	-- gii.emitPythonSignal('entity.added', self.created )
end

--------------------------------------------------------------------
CLASS: CmdCreateComponent ( mock_edit.EditorCommand )
	:register( 'scene_editor/create_component' )

function CmdCreateComponent:init( option )
	self.componentName = option.name	
	local target = gii.getSelection( 'scene' )[1]
	if not isInstanceOf( target, mock.Entity ) then
		_warn( 'attempt to attach component to non Entity object', target:getClassName() )
		return false
	end	
	self.targetEntity  = target
end

function CmdCreateComponent:redo()	
	local comType = mock.getComponentType( self.componentName )
	assert( comType )
	local component = comType()
	component.__guid = generateGUID()
	self.createdComponent = component
	self.targetEntity:attach( component )
	gii.emitPythonSignal( 'component.added', component, self.targetEntity )	
end

function CmdCreateComponent:undo()
	self.targetEntity:detach( self.createdComponent )
	gii.emitPythonSignal( 'component.removed', component, self.targetEntity )	
end

--------------------------------------------------------------------
CLASS: CmdRemoveComponent ( mock_edit.EditorCommand )
	:register( 'scene_editor/remove_component' )

function CmdRemoveComponent:init( option )
	self.target = option['target']
end

function CmdRemoveComponent:redo()
	--todo
	local ent = self.target._entity
	if ent then
		ent:detach( self.target )
	end
	self.previousParent = ent
	gii.emitPythonSignal( 'component.removed', self.target, self.previousParent )	
end

function CmdRemoveComponent:undo()
	self.previousParent:attach( self.target )
	gii.emitPythonSignal( 'component.added', self.target, self.previousParent )	
end


--------------------------------------------------------------------
CLASS: CmdCloneEntity ( mock_edit.EditorCommand )
	:register( 'scene_editor/clone_entity' )

function CmdCloneEntity:init( option )
	local targets = getTopLevelEntitySelection()
	self.targets = targets
	if not next( targets ) then return false end
end

function CmdCloneEntity:redo()
	local createdList = {}
	for target in pairs( self.targets ) do
		local created = mock.cloneEntity( target )
		created.__prefabId = target.__prefabId
		local n = created:getName()
		if n then
			created:setName( n .. '_1' )
		end
		local parent = target.parent
		if parent then
			parent:addChild( created )
		else
			editor.scene:addEntity( created )
		end		
		gii.emitPythonSignal('entity.added', created, 'clone' )
		table.insert( createdList, created )
	end
	gii.changeSelection( 'scene', unpack( createdList ) )
end

function CmdCloneEntity:undo()
	--todo:
	gii.emitPythonSignal('entity.removed', self.created )
	self.created:destroyWithChildrenNow()
end

--------------------------------------------------------------------
CLASS: CmdReparentEntity ( mock_edit.EditorCommand )
	:register( 'scene_editor/reparent_entity' )

function CmdReparentEntity:init( option )
	self.target   = option['target']
	self.children = gii.getSelection( 'scene' )
	self.oldParents = {}
end

function CmdReparentEntity:redo()
	local target = self.target
	for i, e in ipairs( self.children ) do
		local e1 = mock.cloneEntity(e)
		local tx, ty ,tz = e:getWorldLoc()
		if target == 'root' then
			editor.scene:addEntity( e1 )
			e1:setLoc( tx, ty, tz )
		else
			target:addChild( e1 )
			target:forceUpdate()
			local x, y, z = target:worldToModel( tx, ty, tz )
			e1:setLoc( x, y, z )
		end
		e:destroyWithChildrenNow()
	end	
end

function CmdReparentEntity:undo()
	--todo:
end

--------------------------------------------------------------------
local function saveEntityToPrefab( entity, prefabFile )
	local data = mock.serializeEntity( entity )
	local str  = encodeJSON( data )
	local file = io.open( prefabFile, 'wb' )
	if file then
		file:write( str )
		file:close()
	else
		_error( 'can not write to scene file', prefabFile )
		return false
	end
	return true
end

local function reloadPrefabEntity( entity )
	local guid = entity.__guid
	local prefabPath = entity.__prefabId
	--Just recreate entity from prefab
	local prefab, node = mock.loadAsset( prefabPath )
	if not prefab then return false end
	local newEntity = prefab:createInstance()
	--only perserve location?
	newEntity:setLoc( entity:getLoc() )
	newEntity.__guid = guid
	newEntity.__prefabId = prefabPath
	--TODO: just marked as deleted
	entity:addSibling( newEntity )
	entity:destroyWithChildrenNow()	
end

--------------------------------------------------------------------
CLASS: CmdCreatePrefab ( mock_edit.EditorCommand )
	:register( 'scene_editor/create_prefab' )

function CmdCreatePrefab:init( option )
	self.prefabFile = option['file']
	self.prefabPath = option['prefab']
	self.entity     = option['entity']
end

function CmdCreatePrefab:redo()
	if saveEntityToPrefab( self.entity, self.prefabFile ) then
		self.entity.__prefabId = self.prefabPath
		return true
	else
		return false
	end
end

--------------------------------------------------------------------
CLASS: CmdCreatePrefabEntity ( CmdCreateEntityBase )
	:register( 'scene_editor/create_prefab_entity' )

function CmdCreatePrefabEntity:init( option )
	CmdCreateEntityBase.init( self, option )
	self.prefabPath = option['prefab']
end

function CmdCreatePrefabEntity:createEntity()
	local prefab, node = mock.loadAsset( self.prefabPath )
	if not prefab then return false end
	return prefab:createInstance()
end

--------------------------------------------------------------------
CLASS: CmdUnlinkPrefab ( mock_edit.EditorCommand )
	:register( 'scene_editor/unlink_prefab' )

function CmdUnlinkPrefab:init( option )
	self.entity     = option['entity']
	self.prefabId = self.entity.__prefabId
end

function CmdUnlinkPrefab:redo()
	self.entity.__prefabId = nil
	gii.emitPythonSignal( 'prefab.unlink', self.entity )
end

function CmdUnlinkPrefab:undo()
	self.entity.__prefabId = self.prefabId --TODO: other process
	gii.emitPythonSignal( 'prefab.relink', self.entity )
end


--------------------------------------------------------------------
CLASS: CmdPushPrefab ( mock_edit.EditorCommand )
	:register( 'scene_editor/push_prefab' )

function CmdPushPrefab:init( option )
	self.entity     = option['entity']
end

function CmdPushPrefab:redo()
	local entity = self.entity
	local prefabPath = entity.__prefabId
	local node = mock.getAssetNode( prefabPath )
	local filePath = node:getAbsObjectFile( 'def' )
	if saveEntityToPrefab( entity, filePath ) then
		gii.emitPythonSignal( 'prefab.push', entity )
		--Update all entity in current scene
		local scene = entity.scene
		local toReload = {}
		for e in pairs( scene.entities ) do
			if e.__prefabId == prefabPath and e~=entity then
				toReload[ e ] = true
			end
		end
		for e in pairs( toReload ) do
			reloadPrefabEntity( e )
		end
	else
		return false
	end
end

--------------------------------------------------------------------
CLASS: CmdPullPrefab ( mock_edit.EditorCommand )
	:register( 'scene_editor/pull_prefab' )

function CmdPullPrefab:init( option )
	self.entity     = option['entity']
end

function CmdPullPrefab:redo()
	reloadPrefabEntity( self.entity )
	gii.emitPythonSignal( 'prefab.pull', self.newEntity )
	--TODO: reselect it ?
end

--------------------------------------------------------------------
CLASS: CmdAssignEntityLayer ( mock_edit.EditorCommand )
	:register( 'scene_editor/assign_layer' )

function CmdAssignEntityLayer:init( option )
	self.layerName = option['target']
	self.entities  = gii.getSelection( 'scene' )	
	self.oldLayers = {}
end

function CmdAssignEntityLayer:redo()
	local layerName = self.layerName
	local oldLayers = self.oldLayers
	for i, e in ipairs( self.entities ) do
		oldLayers[ e ] = e:getLayer()
		e:setLayer( layerName )
		gii.emitPythonSignal( 'entity.renamed', e, '' )
	end	
end

function CmdAssignEntityLayer:undo()
	local oldLayers = self.oldLayers
	for i, e in ipairs( self.entities ) do
		layerName = oldLayers[ e ]
		e:setLayer( layerName )
		gii.emitPythonSignal( 'entity.renamed', e, '' )
	end	
end

--------------------------------------------------------------------
CLASS: CmdUnifyChildrenLayer ( mock_edit.EditorCommand )
	:register( 'scene_editor/unify_children_layer' )

function CmdUnifyChildrenLayer:init( option )
	--TODO
end

function CmdUnifyChildrenLayer:redo( )
	--TODO
end

function CmdUnifyChildrenLayer:undo( )
	--TODO
end
