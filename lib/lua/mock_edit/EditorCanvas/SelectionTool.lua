module 'mock_edit'


CLASS: SelectionTool ( mock_edit.CanvasTool )
function SelectionTool:onMouseUp( btn, x, y )
	if btn == 'left' then
		self:pickAndSelect( x, y )
	end
end

registerCanvasTool( 'selection', SelectionTool )
