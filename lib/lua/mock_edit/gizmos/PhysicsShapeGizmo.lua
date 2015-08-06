module 'mock_edit'

addColor( 'physics_gizmo', hexcolor( '#ff3d32', 0.7) )
addColor( 'physics_gizmo_active', hexcolor( '#ff9000', 0.7) )

--------------------------------------------------------------------
CLASS: PhysicsShapeGizmo( Gizmo )
function PhysicsShapeGizmo:__init( shape )
	self.shape = shape
	self.transform = MOAITransform.new()
	inheritTransform( self.transform, shape._entity:getProp( 'physics' ) )
end

function PhysicsShapeGizmo:onLoad()
	self.drawScript = self:attach( mock.DrawScript() )
	self.drawScript:setBlend( 'alpha' )
end

function PhysicsShapeGizmo:onDraw()
end

function PhysicsShapeGizmo:getPickingTarget()
	return self.shape._entity
end

function PhysicsShapeGizmo:isPickable()
	return false
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

function PhysicsShapeBoxGizmo:onGetRectX()
	local shape = self.shape
	local x, y = shape:getLoc()
	local w, h = shape.w, shape.h
	return -0.5*w, -0.5*h, 0.5*w, 0.5*h
end


function PhysicsShapeBoxGizmo:getPickingProp()
	return self.drawScript:getMoaiProp()
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


function PhysicsShapeCircleGizmo:onGetRectX()
	local shape = self.shape
	local x, y = shape:getLoc()
	local radius = shape.radius
	return -0.5*radius, -0.5*radius, 0.5*radius, 0.5*radius
end


function PhysicsShapeCircleGizmo:getPickingProp()
	return self.drawScript:getMoaiProp()
end

--Install
mock.PhysicsShapeCircle.onBuildGizmo = function( self )
	return PhysicsShapeCircleGizmo( self )
end



--------------------------------------------------------------------
CLASS: PhysicsShapeBevelBoxGizmo( PhysicsShapeBoxGizmo )

function PhysicsShapeBevelBoxGizmo:__init( shape )
end

function PhysicsShapeBevelBoxGizmo:onDraw()
	local shape = self.shape
	local x, y = shape:getLoc()
	local w, h = shape.w, shape.h
	local rot  = shape.rotation
	self.transform:setLoc( x, y )
	self.transform:setRot( 0,0, rot )
	GIIHelper.setVertexTransform( self.transform )

	applyColor 'physics_gizmo'	
	MOAIGfxDevice.setPenWidth(1)
	
	local w2, h2 = w/2, h/2
	local b = shape.bevel

	local srcVerts = {
		-w2,      h2 - b,
		-w2 + b,  h2,

		 w2 - b,  h2,
		 w2    ,  h2 - b,

		 w2    , -h2 + b,
		 w2 - b, -h2,

		-w2 + b, -h2,
		-w2    , -h2 + b,

		--LOOP
		-w2,      h2 - b,
	}
	MOAIDraw.drawLine( srcVerts )
end

--Install
mock.PhysicsShapeBevelBox.onBuildGizmo = function( self )
	return PhysicsShapeBevelBoxGizmo( self )
end



--------------------------------------------------------------------
CLASS: PhysicsShapePieGizmo( PhysicsShapeBoxGizmo )

function PhysicsShapePieGizmo:__init( shape )
end

function PhysicsShapePieGizmo:onDraw()
	local shape = self.shape
	local x, y = shape:getLoc()
	local w, h = shape.w, shape.h
	local rot  = shape.rotation
	self.transform:setLoc( x, y )
	self.transform:setRot( 0,0, rot )
	GIIHelper.setVertexTransform( self.transform )

	applyColor 'physics_gizmo'	
	MOAIGfxDevice.setPenWidth(1)
	
	local verts = shape:calcVerts()
	table.insert( verts, verts[1] )
	table.insert( verts, verts[2] )
	
	MOAIDraw.drawLine( verts )
end

--Install
mock.PhysicsShapePie.onBuildGizmo = function( self )
	return PhysicsShapePieGizmo( self )
end
