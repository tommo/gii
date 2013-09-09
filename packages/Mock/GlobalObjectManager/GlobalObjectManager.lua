require 'mock'
function addObject()
	local lib = mock.game:getGlobalObjectLibrary()
	local node = lib.root:addObject( 'object', Entity() )
	return node
end

function addGroup()
	local lib = mock.game:getGlobalObjectLibrary()
	local node = lib.root:addGroup( 'group' )
	return node
end

function renameObject( node, name )
	
end

function remove( node )
	node.parent:removeNode( node.name )
end



--------------------------------------------------------------------
CLASS: CmdCreateGlobalObject ( EditorCommand )
	:register( 'scene_editor/create_global_object' )

function CmdCreateGlobalObject:init( option )
	self.className = option.name
end

function CmdCreateGlobalObject:redo()
	local objClas = mock.getGlobalObjectClass( self.className )
	assert( objClas )
	local object = objClas()
	self.created = object
	local lib = mock.game:getGlobalObjectLibrary()
	local node = lib.root:addObject( 'object', object )
	gii.emitPythonSignal('global_object.added', node )
end

function CmdCreateGlobalObject:undo()
	--TODO
	gii.emitPythonSignal('global_object.removed', self.created )
end