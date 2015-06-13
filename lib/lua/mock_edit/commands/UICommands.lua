module 'mock_edit'
--------------------------------------------------------------------
CLASS: CmdToggleDebugDraw ( mock_edit.EditorCommandNoHistory )
	:register( 'scene_editor/toggle_debug_draw' )

function CmdToggleDebugDraw:init( option )
	-- print( 'toggle floor helper:', option.toggle )
	local sceneView = mock_edit.getCurrentSceneView()
	if not sceneView then return end
	sceneView:toggleDebugLines( option.toggle )
	gii.emitPythonSignal( 'scene.update' )
end

