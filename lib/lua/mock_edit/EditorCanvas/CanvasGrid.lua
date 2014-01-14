module 'mock_edit'
--------------------------------------------------------------------
--CanvasGrid
--------------------------------------------------------------------
CLASS: CanvasGrid( EditorEntity )
function CanvasGrid:onLoad()
	self:attach( mock.DrawScript{	priority = -1	} )
	self.gridSize = 100
end

function CanvasGrid:onDraw()
	local context = gii.getCurrentRenderContext()
	local w, h = MOAIGfxDevice:getViewSize()
	local x0, y1 = self:wndToWorld( 0, 0 )
	local x1, y0 = self:wndToWorld( w, h )
	if w and h then
		--sub grids
		MOAIGfxDevice.setPenWidth( 1 )
		MOAIGfxDevice.setPenColor( .3, .3, .3, .3 )
		local dx = x1-x0
		local dy = y1-y0
		local gs = self.gridSize
		x0, y1 = self:wndToWorld( 0, 0 )
		x1, y0 = self:wndToWorld( w, h )
		local col = math.ceil( dx/gs )
		local row = math.ceil( dy/gs )
		local cx0 = math.floor( x0/gs ) * gs
		local cy0 = math.floor( y0/gs ) * gs
		for x = cx0, cx0 + col*gs, gs do
			MOAIDraw.drawLine( x, y0, x, y1 )
		end
		for y = cy0, cy0 + row*gs, gs do
			MOAIDraw.drawLine( x0, y, x1, y )
		end
	else
		x0, y0 = -10000, -10000
		x1, y1 =  10000,  10000
	end
	--Axis
	MOAIGfxDevice.setPenWidth( 2 )
	MOAIGfxDevice.setPenColor( .3, .3, .3, .5 )
	MOAIDraw.drawLine( x0, 0, x1, 0 )
	MOAIDraw.drawLine( 0, y0, 0, y1 )

end