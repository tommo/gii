local findTopLevelEntities       = mock_edit.findTopLevelEntities
local getTopLevelEntitySelection = mock_edit.getTopLevelEntitySelection
local isEditorEntity             = mock_edit.isEditorEntity

local affirmGUID      = mock_edit.affirmGUID
local affirmSceneGUID = mock_edit.affirmSceneGUID
local generateGUID = MOAIEnvironment.generateGUID

--------------------------------------------------------------------
CLASS:  SceneGraphEditor()

function SceneGraphEditor:__init()
	self.failedRefreshData = false
	connectSignalMethod( 'mainscene.open',  self, 'onMainSceneOpen' )
	connectSignalMethod( 'mainscene.close', self, 'onMainSceneClose' )
end

function SceneGraphEditor:getScene()
	return self.scene
end

function SceneGraphEditor:openScene( path )
	local scene = mock.game:openSceneByPath( path ) --dont start
	assert( scene )
	self.scene = scene
	affirmSceneGUID( scene )
	--
	self:postLoadScene()
	mock.setAssetCacheWeak()
	GIIHelper.forceGC()
	mock.setAssetCacheStrong()
	mock_edit.updateMOAIGfxResource()
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
	affirmSceneGUID( self.scene )
	mock.serializeSceneToFile( self.scene, path, 'keepProto' )
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

local function collectFoldState( ent )
end

function SceneGraphEditor:saveIntrospectorFoldState()
	local output = {}
	for ent in pairs( self.scene.entities ) do
		if ent.__guid and ent.__foldState then output[ent.__guid] = true end
		for com in pairs( ent.components ) do
			if com.__guid and com.__foldState then output[com.__guid] = true end
		end
	end
	return gii.tableToDict( output )
end

function SceneGraphEditor:loadIntrospectorFoldState( containerFoldState )
	containerFoldState = gii.dictToTable( containerFoldState )
	for ent in pairs( self.scene.entities ) do
		if ent.__guid and containerFoldState[ent.__guid] then
			ent.__foldState = true
		end
		for com in pairs( ent.components ) do
			if com.__guid and containerFoldState[ com.__guid ] then
				com.__foldState = true
			end
		end

	end
end

function SceneGraphEditor:locateProto( path )
	local protoData = mock.loadAsset( path )
	local rootId = protoData.rootId
	for ent in pairs( self.scene.entities ) do
		if ent.__guid == rootId then
			return gii.changeSelection( 'scene', ent )
		end
	end
end

function SceneGraphEditor:postLoadScene()
	local scene = self.scene
	scene:setEntityListener( function( action, ... ) return self:onEntityEvent( action, ... ) end )
end


function SceneGraphEditor:startScenePreview()
	_collectgarbage( 'collect' )
	-- GIIHelper.forceGC()
	mock.game:start()
end

function SceneGraphEditor:stopScenePreview()
	_collectgarbage( 'collect' )
	-- GIIHelper.forceGC()
	mock.game:stop()
	--restore layer visiblity
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
	self.retainedSceneData = mock.serializeScene( self.scene, 'keepProto' )
	--keep node fold state
end


function SceneGraphEditor:restoreScene()
	if not self.retainedSceneData then return true end
	local function _onError( msg )
		local errMsg = msg
		local tracebackMsg = debug.traceback(2)
		return errMsg .. '\n' .. tracebackMsg
	end

	local ok, msg = xpcall( function()
			mock.deserializeScene( self.retainedSceneData, self.scene )
		end,
		_onError
		)
	gii.emitPythonSignal( 'scene.update' )
	if ok then
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
		print( msg )
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
	if isInstance( e, typeId ) then
		collection[ e ] = true
	end
	for child in pairs( e.children ) do
		collectEntity( child, typeId, collection )
	end
end

local function collectComponent( entity, typeId, collection )
	if isEditorEntity( entity ) then return end
	for com in pairs( entity.components ) do
		if not com.FLAG_INTERNAL and isInstance( com, typeId ) then
			collection[ com ] = true
		end
	end
	for child in pairs( entity.children ) do
		collectComponent( child, typeId, collection )
	end
end

local function collectEntityGroup( group, collection )
	if isEditorEntity( group ) then return end
	collection[ group ] = true 
	for child in pairs( group.childGroups ) do
		collectEntityGroup( child, collection )
	end
end

function SceneGraphEditor:enumerateObjects( typeId )	
	local scene = self.scene
	if not scene then return nil end
	local result = {}
	--REMOVE: demo codes
	if typeId == 'entity' then	
		local collection = {}	
		
		for e in pairs( scene.entities ) do
			collectEntity( e, mock.Entity, collection )
		end

		for e in pairs( collection ) do
			table.insert( result, e )
		end
	
	elseif typeId == 'group' then	
		local collection = {}	
		
		for g in pairs( scene:getRootGroup().childGroups ) do
			collectEntityGroup( g, collection )
		end

		for g in pairs( collection ) do
			table.insert( result, g )
		end

	elseif typeId == 'entity_in_group' then	
		local collection = {}	
		--TODO:!!!!
		
		for e in pairs( scene.entities ) do
			collectEntity( e, mock.Entity, collection )
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
		_owner.addEntityNode( entity )
		-- gii.emitPythonSignal( 'scene.update' )
	elseif action == 'remove' then
		_owner.removeEntityNode( entity )
		-- gii.emitPythonSignal( 'scene.update' )
	elseif action == 'add_group' then
		_owner.addEntityNode( entity )
		-- gii.emitPythonSignal( 'scene.update' )
	elseif action == 'remove_group' then
		_owner.removeEntityNode( entity )
		-- gii.emitPythonSignal( 'scene.update' )
	end

end

function SceneGraphEditor:onMainSceneOpen( scn )
	gii.emitPythonSignal( 'scene.change' )
end

function SceneGraphEditor:onMainSceneClose( scn )
	gii.emitPythonSignal( 'scene.change' )
end

function SceneGraphEditor:makeSceneSelectionCopyData()
	local targets = getTopLevelEntitySelection()
	local dataList = {}
	for _, ent in ipairs( targets ) do
		local data = mock.makeEntityCopyData( ent )
		table.insert( dataList, data )
	end
	return encodeJSON( { 
		entities = dataList,
		scene    = editor.scene.assetPath or '<unknown>',
	} )
end

editor = SceneGraphEditor()

--------------------------------------------------------------------
function enumerateSceneObjects( enumerator, typeId, context )
	--if context~='scene_editor' then return nil end
	return editor:enumerateObjects( typeId )
end

function getSceneObjectRepr( enumerator, obj )
	if isInstance( obj, mock.Entity ) then
		return obj:getName() or '<unnamed>'
	elseif isInstance( obj, mock.EntityGroup ) then
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


local function extractNumberPrefix( name )
	local numberPart = string.match( name, '_%d+$' )
	if numberPart then
		local mainPart = string.sub( name, 1, -1 - #numberPart )
		return mainPart, tonumber( numberPart )
	end
	return name, nil
end

local function findNextNumberProfix( scene, name )
	local max = -1
	local pattern = name .. '_(%d+)$'
	for ent in pairs( scene.entities ) do
		local n = ent:getName()
		if n then
			if n == name then 
				max = math.max( 0, max )
			else
				local id = string.match( n, pattern )
				if id then
					max = math.max( max, tonumber( id ) )
				end
			end
		end
	end
	return max
end

local function makeNumberProfix( scene, entity )
	local n = entity:getName()
	if n then
		--auto increase prefix
		local header, profix = extractNumberPrefix( n )
		local number = findNextNumberProfix( scene, header )
		if number >= 0 then
			local profix = '_' .. string.format( '%02d', number + 1 )
			entity:setName( header .. profix )
		end
	end
end

--------------------------------------------------------------------
CLASS: CmdCreateEntityBase ( mock_edit.EditorCommand )
function CmdCreateEntityBase:init( option )
	local contextEntity = gii.getSelection( 'scene' )[1]
	if isInstance( contextEntity, mock.Entity ) then
		if option[ 'create_sibling' ] then
			self.parentEntity = contextEntity:getParent()
		else
			self.parentEntity = contextEntity
		end
	elseif isInstance( contextEntity, mock.EntityGroup ) then
		self.parentEntity = contextEntity
	else
		self.parentEntity = false
	end
end

function CmdCreateEntityBase:createEntity()
end

function CmdCreateEntityBase:getResult()
	return self.created
end

function CmdCreateEntityBase:redo()
	local entity = self:createEntity()
	if not entity then return false end
	affirmGUID( entity )
	self.created = entity
	if self.parentEntity then
		self.parentEntity:addChild( entity )
	else
		editor.scene:addEntity( entity )
	end
	gii.emitPythonSignal( 'entity.added', self.created, 'new' )
end

function CmdCreateEntityBase:undo()
	self.created:destroyWithChildrenNow()
	gii.emitPythonSignal( 'entity.removed', self.created )
end

--------------------------------------------------------------------
CLASS: CmdCreateEntity ( CmdCreateEntityBase )
	:register( 'scene_editor/create_entity' )

function CmdCreateEntity:init( option )
	CmdCreateEntityBase.init( self, option )
	self.entityName = option.name
end

local function _editorInitEntity( e )
	if e.onEditorInit then
		e:onEditorInit()
	end

	for com in pairs( e.components ) do
		if com.onEditorInit then
		com:onEditorInit()
		end
	end

	for child in pairs( e.children ) do
		_editorInitEntity( child )
	end
end

function CmdCreateEntity:createEntity()
	local entType = mock.getEntityType( self.entityName )
	assert( entType )
	local e = entType()
	_editorInitEntity( e )
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
	self.selection = getTopLevelEntitySelection()
end

function CmdRemoveEntity:redo()
	for _, target in ipairs( self.selection ) do
		if isInstance( target, mock.Entity ) then
			if target.scene then 
				target:destroyWithChildrenNow()
				gii.emitPythonSignal('entity.removed', target )
			end
		elseif isInstance( target, mock.EntityGroup ) then
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
	if not isInstance( target, mock.Entity ) then
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
	if component.onEditorInit then
		component:onEditorInit()
	end
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
	self.created = false
	if not next( targets ) then return false end
end

function CmdCloneEntity:redo()
	local createdList = {}
	for _, target in ipairs( self.targets ) do
		if isInstance( target, mock.EntityGroup ) then
			mock_edit.alertMessage( 'todo', 'Group clone not yet implemented', 'info' )
			return false
		else
			local created = mock.copyAndPasteEntity( target, generateGUID )
			makeNumberProfix( editor.scene, created )
			local parent = target.parent
			if parent then
				parent:addChild( created )
			else
				editor.scene:addEntity( created, nil, target._entityGroup )
			end		
			gii.emitPythonSignal('entity.added', created, 'clone' )
			table.insert( createdList, created )
		end
	end
	gii.changeSelection( 'scene', unpack( createdList ) )
	self.createdList = createdList
end

function CmdCloneEntity:undo()
	--todo:
	for i, created in ipairs( self.createdList ) do
		created:destroyWithChildrenNow()
		gii.emitPythonSignal('entity.removed', created )
	end
	self.createdList = false
end

--------------------------------------------------------------------
CLASS: CmdPasteEntity ( mock_edit.EditorCommand )
	:register( 'scene_editor/paste_entity' )

function CmdPasteEntity:init( option )
	self.data   = decodeJSON( option['data'] )
	self.parent = gii.getSelection( 'scene' )[1] or false
	self.createdList = false
	if not self.data then _error( 'invalid entity data' ) return false end
end

function CmdPasteEntity:redo()
	local createdList = {}
	local parent = self.parent
	for i, copyData in ipairs( self.data.entities ) do
		local entityData = mock.makeEntityPasteData( copyData, generateGUID )
		local created = mock.deserializeEntity( entityData )
		if parent then
			parent:addChild( created )
		else
			editor.scene:addEntity( created )
		end		
		gii.emitPythonSignal('entity.added', created, 'paste' )
		table.insert( createdList, created )
	end
	self.createdList = createdList
	gii.changeSelection( 'scene', unpack( createdList ) )
end

function CmdPasteEntity:undo()
	--todo:
	for i, created in ipairs( self.createdList ) do
		created:destroyWithChildrenNow()
		gii.emitPythonSignal('entity.removed', created )
	end
	self.createdList = false
end


--------------------------------------------------------------------
CLASS: CmdReparentEntity ( mock_edit.EditorCommand )
	:register( 'scene_editor/reparent_entity' )

function CmdReparentEntity:init( option )
	self.target   = option['target']
	self.children = gii.getSelection( 'scene' )
	self.oldParents = {}
	local targetIsEntity = isInstance( self.target, mock.Entity )
	for i, e in ipairs( self.children ) do
		if isInstance( e, mock.EntityGroup ) and targetIsEntity then
			mock_edit.alertMessage( 'fail', 'cannot move Group into Entity', 'info' )
			return false
		end
	end
end

function CmdReparentEntity:redo()
	local target = self.target
	for i, e in ipairs( self.children ) do
		if isInstance( e, mock.Entity ) then
			self:reparentEntity( e, target )
		elseif isInstance( e, mock.EntityGroup ) then
			self:reparentEntityGroup( e, target )
		end
	end	
end

function CmdReparentEntity:reparentEntityGroup( e, target )
	local targetGroup = false
	if target == 'root' then
		targetGroup = editor.scene:getRootGroup()

	elseif isInstance( target, mock.EntityGroup ) then
		targetGroup = target

	else
		error()		
	end

	e:reparent( targetGroup )
end

function CmdReparentEntity:reparentEntity( e, target )
	local e1 = mock.cloneEntity(e)
	e:forceUpdate()
	local tx, ty ,tz = e:getWorldLoc()
	local sx, sy ,sz = e:getWorldScl()
	local rz = e:getWorldRot()
	--TODO: world rotation X,Y	
	if target == 'root' then
		editor.scene:addEntity( e1 )
		e1:setLoc( tx, ty, tz )
		e1:setScl( sx, sy, sz )
		e1:setRotZ( rz )

	elseif isInstance( target, mock.EntityGroup ) then
		editor.scene:addEntity( e1, nil, target )
		e1:setLoc( tx, ty, tz )
		e1:setScl( sx, sy, sz )
		e1:setRotZ( rz )

	else
		target:forceUpdate()
		local x, y, z = target:worldToModel( tx, ty, tz )
		e1:setLoc( x, y, z )
		
		local sx1, sy1, sz1 = target:getWorldScl()
		sx = ( sx1 == 0 ) and 0 or sx/sx1
		sy = ( sy1 == 0 ) and 0 or sy/sy1
		sz = ( sz1 == 0 ) and 0 or sz/sz1
		e1:setScl( sx, sy, sz )

		local rz1 = target:getWorldRot()
		rz = rz1 == 0 and 0 or rz/rz1
		e1:setRotZ( rz )
		target:addChild( e1 )
	end
	e:destroyWithChildrenNow()
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
	newEntity:setName( entity:getName() )
	newEntity:setLayer( entity:getLayer() )
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
CLASS: CmdCreatePrefabContainer ( CmdCreateEntityBase )
	:register( 'scene_editor/create_prefab_container' )

function CmdCreatePrefabContainer:init( option )
	CmdCreateEntityBase.init( self, option )
	self.prefabPath = option['prefab']
end

function CmdCreatePrefabContainer:createEntity()
	local container = mock.PrefabContainer()
	container:setPrefab( self.prefabPath )
	return container	
end

--------------------------------------------------------------------
CLASS: CmdMakeProto ( mock_edit.EditorCommand )
	:register( 'scene_editor/make_proto' )

function CmdMakeProto:init( option )
	self.entity = option['entity']
end

function CmdMakeProto:redo()
	self.entity.FLAG_PROTO_SOURCE = true
end

function CmdMakeProto:undo()
	self.entity.FLAG_PROTO_SOURCE = false
end


--------------------------------------------------------------------
CLASS: CmdCreateProtoInstance ( CmdCreateEntityBase )
	:register( 'scene_editor/create_proto_instance' )

function CmdCreateProtoInstance:init( option )
	CmdCreateEntityBase.init( self, option )
	self.protoPath = option['proto']
end

function CmdCreateProtoInstance:createEntity()
	local proto = mock.loadAsset( self.protoPath )
	local id    = generateGUID()
	local instance = proto:createInstance( nil, id )
	instance.__overrided_fields = {
		[ 'loc' ] = true,
		[ 'name' ] = true,
	}
	makeNumberProfix( editor.scene, instance )
	return instance
end


--------------------------------------------------------------------
CLASS: CmdUnlinkProto ( mock_edit.EditorCommand )
	:register( 'scene_editor/unlink_proto' )

function CmdUnlinkProto:_retainAndClearComponentProtoState( entity, data )
	for com in pairs( entity.components ) do
		if com.__proto_history then
			data[ com ] = {
				overrided = com.__overrided_fields,
				history   = com.__proto_history,
			}
			com.__overrided_fields = nil
			com.__proto_history = nil
		end
	end
end

function CmdUnlinkProto:_retainAndClearChildProtoState( entity, data )
	if entity.PROTO_INSTANCE_STATE then return end
	if not entity.__proto_history then return end
	data[ entity ] = {
		overrided = entity.__overrided_fields,
		history   = entity.__proto_history,
	}
	entity.__overrided_fields = nil
	entity.__proto_history = nil
	self:_retainAndClearComponentProtoState( entity, data )
	for child in pairs( entity.children ) do
		self:_retainAndClearChildProtoState( child, data )
	end
end

function CmdUnlinkProto:_retainAndClearEntityProtoState( root, data )
	data = data or {}
	if root.PROTO_INSTANCE_STATE then
		data[ root ] = {
			overrided = root.__overrided_fields,
			history   = root.__proto_history,
			state     = root.PROTO_INSTANCE_STATE
		}
		for child in pairs( root.children ) do
			self:_retainAndClearChildProtoState( child, data )
		end
		self:_retainAndClearComponentProtoState( root, data )
		root.__overrided_fields   = nil
		root.__proto_history      = nil
		root.PROTO_INSTANCE_STATE = nil
	end
	return data
end

function CmdUnlinkProto:_restoreEntityProtoState( root, data )
	for ent, retained in pairs( data ) do
		if retained.state then
			ent.PROTO_INSTANCE_STATE = retained.state
		end
		ent.__overrided_fields = retained.overrided
		ent.__proto_history = retained.history
	end
end
--TODO
function CmdUnlinkProto:init( option )
	self.entity     = option['entity']
end

function CmdUnlinkProto:redo()	
	self.retainedState =  self:_retainAndClearEntityProtoState( self.entity )
	gii.emitPythonSignal( 'proto.unlink', self.entity )
	gii.emitPythonSignal( 'entity.modified', self.entity )
end

function CmdUnlinkProto:undo()
	self:_restoreEntityProtoState( self.retainedState )
	gii.emitPythonSignal( 'proto.relink', self.entity )
	gii.emitPythonSignal( 'entity.modified', self.entity )
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
CLASS: CmdToggleEntityVisibility ( mock_edit.EditorCommand )
	:register( 'scene_editor/toggle_entity_visibility' )

function CmdToggleEntityVisibility:init( option )
	self.entities  = gii.getSelection( 'scene' )	
	self.originalVis  = {}
end

function CmdToggleEntityVisibility:redo()
	local vis = false
	local originalVis = self.originalVis
	for i, e in ipairs( self.entities ) do
		originalVis[ e ] = e:isLocalVisible()
		if e:isLocalVisible() then vis = true end
	end	
	vis = not vis
	for i, e in ipairs( self.entities ) do
		e:setVisible( vis )
		mock.markProtoInstanceOverrided( e, 'visible' )
		gii.emitPythonSignal( 'entity.visible_changed', e )
		gii.emitPythonSignal( 'entity.modified', e, '' )
	end
end

function CmdToggleEntityVisibility:undo()
	local originalVis = self.originalVis
	for i, e in ipairs( self.entities ) do
		e:setVisible( originalVis[ e ] )
		gii.emitPythonSignal( 'entity.modified', e, '' )
	end	
	self.originalVis  = {}
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

--------------------------------------------------------------------
CLASS: CmdFreezePivot ( mock_edit.EditorCommand )
	:register( 'scene_editor/freeze_entity_pivot' )

function CmdFreezePivot:init( option )
	self.entities  = gii.getSelection( 'scene' )
	self.previousPivots = {}
end

function CmdFreezePivot:redo( )
	local pivots = self.previousPivots
	for i, e in ipairs( self.entities ) do
		local px, py, pz = e:getPiv()
		e:setPiv( 0,0,0 )
		e:addLoc( -px, -py, -pz )
		-- for child in pairs( e:getChildren() ) do
		-- 	child:addLoc( -px, -py, -pz )
		-- end
		gii.emitPythonSignal( 'entity.modified', e, '' )
	end
end

function CmdFreezePivot:undo( )
	--TODO
end



--------------------------------------------------------------------
CLASS: CmdEntityGroupCreate ( mock_edit.EditorCommand )
	:register( 'scene_editor/entity_group_create')


function CmdEntityGroupCreate:init( option )
	local contextEntity = gii.getSelection( 'scene' )[1]
	
	if isInstance( contextEntity, mock.Entity ) then
		if not contextEntity._entityGroup then
			mock_edit.alertMessage( 'fail', 'cannot create Group inside Entity', 'info' )
			return false
		end
		self.parentGroup = contextEntity._entityGroup
	elseif isInstance( contextEntity, mock.EntityGroup ) then
		self.parentGroup = contextEntity
	else
		self.parentGroup = editor.scene:getRootGroup()
	end

	self.guid = generateGUID()

end

function CmdEntityGroupCreate:redo()
	self.createdGroup = mock.EntityGroup()
	self.parentGroup:addChildGroup( self.createdGroup )
	self.createdGroup.__guid = self.guid
	gii.emitPythonSignal( 'entity.added', self.createdGroup, 'new' )
end

function CmdEntityGroupCreate:undo()
	--TODO
	self.parentGroup:removeChildGroup( self.createdGroup )
end

