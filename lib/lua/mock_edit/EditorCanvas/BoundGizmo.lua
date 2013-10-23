module 'mock_edit'

--------------------------------------------------------------------
CLASS: BoundGizmo( CanvasHandle )
function BoundGizmo:onLoad()
	self.target = false
	self:attach( mock.DrawScript() )
end

function BoundGizmo:setTarget( e )
	self.target = e
end

function BoundGizmo:onDraw()
	local target = self.target
	if not target then return end
	applyColor 'selection'
	if not target.components then 
		return self:destroy()
	end
	for com in pairs( target.components ) do
		local drawBounds = com.drawBounds
		if drawBounds then drawBounds( com ) end
	end
end
