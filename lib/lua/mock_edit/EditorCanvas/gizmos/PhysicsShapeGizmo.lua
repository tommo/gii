module 'mock_edit'

addColor( 'physics_gizmo', hexcolor( '#ff3d32', 0.5) )
addColor( 'physics_gizmo_active', hexcolor( '#ff9000', 0.5) )

--------------------------------------------------------------------
CLASS: PhysicsShapeGizmo( Gizmo )
function PhysicsShapeGizmo:__init( shape )
	self.shape = shape
	self.transform = MOAITransform.new()
	inheritTransform( self.transform, shape._entity:getProp( 'physics' ) )
end

function PhysicsShapeGizmo:onLoad()
	self:attach( mock.DrawScript() ):setBlend( 'alpha' )
end

function PhysicsShapeGizmo:onDraw()
end


--------------------------------------------------------------------
CLASS: PhysicsShapeBoxGizmo( PhysicsShapeGizmo )

function PhysicsShapeBoxGizmo:__init( shape )
end

function PhysicsShapeBoxGizmo:onDraw()
	local shape = self.shape
	local x, y = shape:getLoc()
	local w, h = shape.w, shape.h
	local rot  = shape.rotation
	self.transform:setLoc( x, y )
	self.transform:setRot( 0,0, rot )
	GIIHelper.setVertexTransform( self.transform )

	applyColor 'physics_gizmo'	
	MOAIGfxDevice.setPenWidth(1)
	
	MOAIDraw.drawRect( -0.5*w, -0.5*h, 0.5*w, 0.5*h )
end

--Install
mock.PhysicsShapeBox.onBuildGizmo = function( self )
	return PhysicsShapeBoxGizmo( self )
end


--------------------------------------------------------------------
CLASS: PhysicsShapeCircleGizmo( PhysicsShapeGizmo )

function PhysicsShapeCircleGizmo:__init( shape )
end

function PhysicsShapeCircleGizmo:onDraw()
	local shape = self.shape
	local x, y = shape:getLoc()
	local radius = shape.radius
	self.transform:setLoc( x, y )
	GIIHelper.setVertexTransform( self.transform )

	applyColor 'physics_gizmo'	
	MOAIGfxDevice.setPenWidth(1)
	
	MOAIDraw.drawCircle( 0,0, radius )
end

--Install
mock.PhysicsShapeCircle.onBuildGizmo = function( self )
	return PhysicsShapeCircleGizmo( self )
end
