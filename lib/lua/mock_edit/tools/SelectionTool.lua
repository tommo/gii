module 'mock_edit'

--------------------------------------------------------------------
CLASS: SelectionTool ( mock_edit.CanvasTool )

function SelectionTool:onLoad()
	local plane = self:addCanvasItem( CanvasPickPlane() )
	plane:setPickCallback( function( picked )
		gii.changeSelection( 'scene', unpack( picked ) )
	end)
end

registerCanvasTool( 'selection', SelectionTool )
