module 'mock_edit'
--------------------------------------------------------------------
CLASS: CmdFillRenderMaterial ( mock_edit.EditorCommand )
	:register( 'scene_editor/fill_render_material' )

function CmdFillRenderMaterial:init( option )
	-- print( 'toggle floor helper:', option.toggle )
	local sceneView = mock_edit.getCurrentSceneView()
	if not sceneView then return end
	sceneView:toggleDebugLines( option.toggle )
	gii.emitPythonSignal( 'scene.update' )
end

