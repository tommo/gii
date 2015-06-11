module 'mock_edit'

CLASS: SceneTool ()
	:MODEL{}

--class function
function SceneTool.register( clas, categoryId, id )
	_stat( 'register Lua Scene Tool', name )
	gii.registerLuaCommand( name, clas )
end

function SceneTool:getName()
end


---------------------------------------------------------------------
function registerSceneToolCategory( id, name, icon )

end

