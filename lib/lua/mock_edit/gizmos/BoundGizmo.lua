module 'mock_edit'
--------------------------------------------------------------------
CLASS: SimpleBoundGizmo( Gizmo )
function SimpleBoundGizmo:__init()
	self.target = false
end

function SimpleBoundGizmo:onLoad()
	self:attach( mock.DrawScript() ):setBlend( 'alpha' )
end

function SimpleBoundGizmo:setTarget( target )
	self.target = target
	self.drawBounds = target.drawBounds
end

function SimpleBoundGizmo:onDraw()
	local drawBounds = self.drawBounds
	if drawBounds then
		applyColor 'selection'
		MOAIGfxDevice.setPenWidth(1)
		return drawBounds( self.target )
	end	
end


--------------------------------------------------------------------
--Bind to core components
local function methodBuildBoundGizmo( self )
	if self.drawBounds then		
		local giz = SimpleBoundGizmo()
		giz:setTarget( self )
		return giz
	end
end

local function installBoundGizmo( clas )
	clas.onBuildSelectedGizmo = methodBuildBoundGizmo
end


installBoundGizmo( mock.DeckComponent )
installBoundGizmo( mock.TexturePlane  )
installBoundGizmo( mock.TextLabel     )
installBoundGizmo( mock.MSprite       )
