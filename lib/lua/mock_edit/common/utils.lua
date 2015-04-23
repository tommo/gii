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
		if isInstance( e, mock.Entity ) then 
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
