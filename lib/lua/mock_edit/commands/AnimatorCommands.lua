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
