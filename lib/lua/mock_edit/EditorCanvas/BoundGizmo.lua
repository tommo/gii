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
	MOAIGfxDevice.setPenWidth(1)
	for com in pairs( target.components ) do
		if not com.FLAG_INTERNAL then
			local drawBounds = com.drawBounds
			if drawBounds then drawBounds( com ) end
		end
	end
end
