module 'mock_edit'


CLASS: PhysicsShapeEditor ( CanvasTool )
	:MODEL{}

function PhysicsShapeEditor:__init()
	self.verts = {}
end

function PhysicsShapeEditor:onLoad()
	local plane = self:addCanvasItem( CanvasPickPlane() )
	plane:setPickCallback( function( picked )
		gii.changeSelection( 'scene', picked )
	end)
	local vert = self:addCanvasItem( CanvasItemVert() )
	self:updateSelection()
end

function PhysicsShapeEditor:onSelectionChanged( selection )
	self:updateSelection()
end

function PhysicsShapeEditor:updateSelection()
end


registerCanvasTool( 'physics_shape_editor', PhysicsShapeEditor )
