module 'mock_edit'

--------------------------------------------------------------------
CLASS: SelectionTool ( mock_edit.CanvasTool )

function SelectionTool:onLoad()
	local plane = self:addCanvasItem( CanvasPickPlane() )	
	local inputDevice = plane:getView():getInputDevice()
	plane:setPickCallback( function( picked )
		if inputDevice:isCtrlDown() then
			gii.toggleSelection( 'scene', unpack( picked ) )

		elseif inputDevice:isShiftDown() then
			gii.addSelection( 'scene', unpack( picked ) )

		elseif inputDevice:isAltDown() then
			gii.removeSelection( 'scene', unpack( picked ) )
		
		else
			gii.changeSelection( 'scene', unpack( picked ) )

		end
	end)
end

registerCanvasTool( 'selection', SelectionTool )
