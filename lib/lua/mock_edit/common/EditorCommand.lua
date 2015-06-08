module 'mock_edit'
--------------------------------------------------------------------
--Editor Command
--------------------------------------------------------------------
CLASS: EditorCommand ()
function EditorCommand.register( clas, name )
	_stat( 'register Lua Editor Command', name )
	gii.registerLuaEditorCommand( name, clas )
end

function EditorCommand:init( option )
end

function EditorCommand:redo()
end

function EditorCommand:undo()
end

function EditorCommand:hasHistory()
	return true
end

function EditorCommand:canUndo()
	return true
end


--------------------------------------------------------------------
CLASS: EditorCommandNoHistory (EditorCommand)
	:MODEL{}

function EditorCommandNoHistory:hasHistory()
	return false
end


--------------------------------------------------------------------
CLASS: EditorCommandNoUndo (EditorCommand)
	:MODEL{}

function EditorCommandNoUndo:canUndo()
	return false
end

