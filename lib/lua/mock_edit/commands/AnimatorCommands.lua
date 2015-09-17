module 'mock_edit'

local function findTopNodes( nodeSet )
	local found = {}
	for node in pairs( nodeSet ) do
		local p = node.parent
		local isTop = true
		while p do
			if nodeSet[ p ] then isTop = false break end
			p = p.parent
		end
		if isTop then found[node] = true end
	end
	return found
end

--------------------------------------------------------------------
CLASS: CmdAnimatorReparentTrack ( mock_edit.EditorCommand )
	:register( 'scene_editor/animator_reparent_track' )


function CmdAnimatorReparentTrack:init( option )
	local sources = gii.listToTable( option['source'] )
	local sourceSet = {}
	for i, node in ipairs( sources ) do
		sourceSet[ node ] = true
	end
	sourceSet = findTopNodes( sourceSet )
	local target = option['target']
	if target == 'root' then
		local node1 = next( sourceSet )
		target = node1:getRoot()
	end
	
	--validate
	local valid = true
	for node in pairs( sourceSet ) do
		if not node:canReparent( target ) then
			valid = false
			_warn( 'cannot reparent track', node:toString(), '->', target:toString() )
		end
	end
	if not valid then
		return false
	end

	local prevParents = {}
	for node in pairs( sourceSet ) do
		prevParents[ node ] = node.parent
	end
	self.prevParents = prevParents
	self.source = sourceSet
	self.target = target
end

function CmdAnimatorReparentTrack:redo()
	local target = self.target
	for node in pairs( self.source ) do
		node:reparent( target )
	end
	local view = gii.getModule( 'animator_view' )
	if view then
		view:refreshTimeline()
	end
end

function CmdAnimatorReparentTrack:undo()
	local prevParents = self.prevParents
	for node in pairs( self.source ) do
		local prevParent = prevParents[ node ]
		node:reparent( prevParent )
	end
end


--------------------------------------------------------------------
CLASS: CmdAnimatorAddClip ( mock_edit.EditorCommand )
	:register( 'scene_editor/animator_add_clip' )
function CmdAnimatorAddClip:init( option )
	self.targetAnimatorData = option[ 'animator_data' ]
	self.targetParentGroup  = option[ 'parent_group'  ]
	self.createdClip = false
end

function CmdAnimatorAddClip:redo()
	if not self.createdClip then
		self.createdClip = self.targetAnimatorData:createClip(
			'New Clip',
			self.targetParentGroup
		)
	else
		self.targetAnimatorData:addClip( self.createdClip, self.targetParentGroup )
	end
end

function CmdAnimatorAddClip:undo()
	self.targetAnimatorData:removeClip( self.createdClip )
end

function CmdAnimatorAddClip:getResult()
	return self.createdClip
end

--------------------------------------------------------------------
CLASS: CmdAnimatorAddClipGroup ( mock_edit.EditorCommand )
	:register( 'scene_editor/animator_add_clip_group' )

function CmdAnimatorAddClipGroup:init( option )
	self.targetAnimatorData = option[ 'animator_data' ]
	self.targetParentGroup  = option[ 'parent_group'  ]
	self.createdGroup = false
end

function CmdAnimatorAddClipGroup:redo()
	if not self.createdGroup then
		self.createdGroup = self.targetAnimatorData:createClipGroup(
			'New Group',
			self.targetParentGroup
		)
	else
		self.targetAnimatorData:addClip( self.createdGroup, self.targetParentGroup )
	end
end

function CmdAnimatorAddClipGroup:undo()
	self.targetAnimatorData:removeClip( self.createdGroup )
end

function CmdAnimatorAddClipGroup:getResult()
	return self.createdGroup
end

--------------------------------------------------------------------
CLASS: CmdAnimatorRemoveClipNode ( mock_edit.EditorCommand )
	:register( 'scene_editor/animator_remove_clip_node' )

function CmdAnimatorRemoveClipNode:init( option )
	self.targetAnimatorData = option[ 'animator_data' ]
	self.targetNode         = option[ 'target_node'  ]
	self.targetParentGroup  = self.targetNode.parentGroup
end

function CmdAnimatorRemoveClipNode:redo()
	if self.targetNode:isInstance( mock.AnimatorClip ) then
		self.targetParentGroup:removeChildClip( self.targetNode )
	else
		self.targetParentGroup:removeChildGroup( self.targetNode )
	end
end

function CmdAnimatorRemoveClipNode:undo()
	if self.targetNode:isInstance( mock.AnimatorClip ) then
		self.targetParentGroup:addChildClip( self.targetNode )
	else
		self.targetParentGroup:addChildGroup( self.targetNode )
	end
end


--------------------------------------------------------------------
CLASS: CmdAnimatorCloneClipNode ( mock_edit.EditorCommand )
	:register( 'scene_editor/animator_clone_clip_node' )

function CmdAnimatorCloneClipNode:init( option )
	self.targetAnimatorData = option[ 'animator_data' ]
	self.targetNode         = option[ 'target_node'  ]
	self.targetParentGroup  = self.targetNode.parentGroup
	self.cloned = false
end

function CmdAnimatorCloneClipNode:redo()
	if not self.cloned then
		local serializedData = mock.serialize( self.targetNode )
		local cloned = mock.deserialize( nil, serializedData )
		cloned.name = cloned.name .. '_copy'
		cloned.parentGroup = false
		self.cloned = cloned
	end

	local cloned = self.cloned
	if cloned:isInstance( mock.AnimatorClip ) then
		cloned:getRoot():_load()
		self.targetAnimatorData:addClip( cloned, self.targetParentGroup )
	else
		cloned:_load()
		self.targetAnimatorData:addClipGroup( cloned, self.targetParentGroup )
	end
end

function CmdAnimatorCloneClipNode:undo()
	local cloned = self.cloned
	if cloned:isInstance( mock.AnimatorClip ) then
		self.targetAnimatorData:removeClip( cloned )
	else
		self.targetAnimatorData:removeClipGroup( cloned )
	end
end

function CmdAnimatorCloneClipNode:getResult()
	return self.cloned
end

---------------------------------------------------------------------
CLASS: CmdAnimatorAddTrack ( mock_edit.EditorCommand )
	:register( 'scene_editor/animator_add_track' )

