--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

CLASS: PlaceHolder( mock.Entity )
function PlaceHolder:onLoad()
	self:attach( mock.DrawScript() )
	self:attach( EditorInputScript() )
end

function PlaceHolder:onDraw()
	MOAIDraw.fillRect( -50, -50, 50, 50 )
end 

function PlaceHolder:onMouseMove( x, y )
	self:setRot( 0, y, x )
	updateCanvas()
end

function PlaceHolder:onKeyDown( key )
	print( key )
end

scn:addEntity( PlaceHolder() )
