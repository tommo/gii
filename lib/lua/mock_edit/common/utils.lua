module 'mock_edit'

local generateGUID = MOAIEnvironment.generateGUID

--------------------------------------------------------------------
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

local function affirmSceneGUID( scene )
	--affirm guid
	for entity in pairs( scene.entities ) do
		affirmGUID( entity )
	end
end

--------------------------------------------------------------------
local function findTopLevelGroups( groupSet )
	local found = {}
	for g in pairs( groupSet ) do
		local isTop = true
		local p = g.parent
		while p do
			if groupSet[ p ] then isTop = false break end
			p = p.parent
		end
		if isTop then found[g] = true end
	end
	return found
end

local function findTopLevelEntities( entitySet )
	local found = {}
	for e in pairs( entitySet ) do
		local p = e.parent
		local isTop = true
		while p do
			if entitySet[ p ] then isTop = false break end
			p = p.parent
		end
		if isTop then found[e] = true end
	end
	return found
end

local function findEntitiesOutsideGroups( entitySet, groupSet )
	local found = {}
	for e in pairs( entitySet ) do
		local g = e:getEntityGroup( true )
		local isTop = true
		while g do
			if entitySet[ g ] then isTop = false break end
			g = g.parent
		end
		if isTop then found[e] = true end
	end
	return found
end

local function getTopLevelEntitySelection()
	local entitySet = {}
	local groupSet  = {}
	for i, e in ipairs( gii.getSelection( 'scene' ) ) do
		if isInstance( e, mock.Entity ) then 
			entitySet[ e ] = true
		elseif isInstance( e, mock.EntityGroup ) then 
			groupSet[ e ] = true
		end
	end
	local topLevelEntitySet = findTopLevelEntities( entitySet )
	local topLevelGroupSet = findTopLevelGroups( groupSet )
	topLevelEntitySet = findEntitiesOutsideGroups( topLevelEntitySet, topLevelGroupSet )
	local list = {}
	for ent in pairs( topLevelEntitySet ) do
		table.insert( list, ent )
	end
	for group in pairs( topLevelGroupSet ) do
		table.insert( list, group )
	end
	return list
end

local function isEditorEntity( e )
	while e do
		if e.FLAG_EDITOR_OBJECT or e.FLAG_INTERNAL then return true end
		e = e.parent
	end
	return false
end

local updateGfxResource = MOAIGfxResourceMgr.update
function updateMOAIGfxResource()
	if updateGfxResource then
		updateGfxResource()
	end
end
--------------------------------------------------------------------
_M.findTopLevelEntities       = findTopLevelEntities
_M.getTopLevelEntitySelection = getTopLevelEntitySelection
_M.isEditorEntity             = isEditorEntity
_M.affirmGUID                 = affirmGUID
_M.affirmSceneGUID            = affirmSceneGUID
