--------------------------------------------------------------------

CLASS: Fake3DTest ( Entity )

function Fake3DTest:onLoad()	
	local data = {
		columns={
			
		}
	}
end


--------------------------------------------------------------------
CLASS: CameraEntity ( Entity )
function CameraEntity:onLoad()
	self:attach( mock.Camera() )
end

function OnTestStart( logic )	
	logic:addSibling( Fake3DTest() )

end
