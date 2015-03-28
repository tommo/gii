module 'mock_edit'

CLASS: CanvasPickPlane ( CanvasItem )
	:MODEL{}

function CanvasPickPlane:inside()
	return true
end

function CanvasPickPlane:onMouseUp( btn, x, y )
	local picked = self:getView():pick( x, y )
	if self.onPicked then
		return self.onPicked( picked )
	end
end

function CanvasPickPlane:setPickCallback( cb )
	self.onPicked = cb
end
