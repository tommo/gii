--------------------------------------------------------------------
--COMMAND: create global object
--------------------------------------------------------------------
CLASS: CmdCreateGlobalObject ( mock_edit.EditorCommand )
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


--------------------------------------------------------------------
--COMMAND: remove global object
--------------------------------------------------------------------
CLASS: CmdRemoveGlobalObject ( mock_edit.EditorCommand )
	:register( 'scene_editor/remove_global_object' )

function CmdRemoveGlobalObject:init( option )
	self.target = option.target
end

function CmdRemoveGlobalObject:redo()
	--TODO!!!!
	local target = self.target
	local parent = target and target.parent
	if parent then
		parent:removeNode( target.name )
		gii.emitPythonSignal( 'global_object.removed', target )
		return true
	else
		return false
	end
end

function CmdRemoveGlobalObject:undo()
	--TODO
	local target, parent = self.target, self.parent
	parent:addNode( target.name, target )
	gii.emitPythonSignal('global_object.added', target, 'undo' )

end


--------------------------------------------------------------------
--COMMAND: clone global object
--------------------------------------------------------------------
CLASS: CmdCloneGlobalObject ( mock_edit.EditorCommand )
	:register( 'scene_editor/clone_global_object' )

function CmdCloneGlobalObject:init( option )
	self.className = option.name
end

function CmdCloneGlobalObject:redo()
	--TODO!!!!
end

function CmdCloneGlobalObject:undo()
	--TODO
	gii.emitPythonSignal('global_object.removed', self.created )
end


