module 'mock_edit'


--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegate ()
	:MODEL{}

function PhysicsShapeEditorDelegate:__init( editor, shape )
	self.editor = editor
	self.shape  = shape
end

--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegateBox ( PhysicsShapeEditorDelegate )

function PhysicsShapeEditorDelegateBox:onInit( editor, shape )
	self.vertC = editor:addCanvasItem( CanvasItemVert() )
	self.vertT = editor:addCanvasItem( CanvasItemVert() )
	self.vertL = editor:addCanvasItem( CanvasItemVert() )
	self.vertR = editor:addCanvasItem( CanvasItemVert() )
	self.vertB = editor:addCanvasItem( CanvasItemVert() )
	self.vertC.onMove = function( vert ) return self:onVertDrag( 'C', vert ) end
	self.vertT.onMove = function( vert ) return self:onVertDrag( 'T', vert ) end
	self.vertL.onMove = function( vert ) return self:onVertDrag( 'L', vert ) end
	self.vertR.onMove = function( vert ) return self:onVertDrag( 'R', vert ) end
	self.vertB.onMove = function( vert ) return self:onVertDrag( 'B', vert ) end
	self.vertC:setShape( 'circle' )
	self:syncVerts()
end

function PhysicsShapeEditorDelegateBox:syncVerts()
	local shape = self.shape
	local w, h = shape:getSize()
	local x, y = shape:getLoc()
	-- local ent = shape._entity
	self.vertC:setLoc( shape:modelToWorld( x +    0, y + 0    ) )
	self.vertT:setLoc( shape:modelToWorld( x +    0, y +  h/2 ) )
	self.vertB:setLoc( shape:modelToWorld( x +    0, y + -h/2 ) )
	self.vertL:setLoc( shape:modelToWorld( x + -w/2, y + 0    ) )
	self.vertR:setLoc( shape:modelToWorld( x +  w/2, y + 0    ) )

end

function PhysicsShapeEditorDelegateBox:onVertDrag( id, vert )
	if id == 'C' then
		local x, y = vert:getLoc()
		local x1, y1 = self.shape:worldToModel( x, y )
		self.shape:setLoc( x1, y1 )
		self:syncVerts()
		gii.emitPythonSignal( 'entity.modified', self.shape._entity )
	else
		local x0, x1 = self.vertL:getLocX() , self.vertR:getLocX()
		local y0, y1 = self.vertB:getLocY() , self.vertT:getLocY()
		local xc,yc = (x0+x1)/2, (y0+y1)/2
		self.shape:setLoc( self.shape:worldToModel( xc, yc ) )
		self.shape:setWidth( math.max( x1 - x0, 0 ) )
		self.shape:setHeight( math.max( y1 - y0, 0 ) )
		self:syncVerts()
		gii.emitPythonSignal( 'entity.modified', self.shape._entity )
	end
end

--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegateCircle ( PhysicsShapeEditorDelegate )


function PhysicsShapeEditorDelegateCircle:onInit( editor, shape )
	self.vertC = editor:addCanvasItem( CanvasItemVert() )
	self.vertR = editor:addCanvasItem( CanvasItemVert() )
	self.vertC.onMove = function( vert ) return self:onVertDrag( 'C', vert ) end
	self.vertR.onMove = function( vert ) return self:onVertDrag( 'R', vert ) end
	self.vertC:setShape( 'circle' )
	self:syncVerts()
end

function PhysicsShapeEditorDelegateCircle:syncVerts()
	local shape = self.shape
	local x, y = shape:getLoc()
	local r = shape:getRadius()
	-- local ent = shape._entity
	self.vertC:setLoc( shape:modelToWorld( x +  0, y + 0    ) )
	self.vertR:setLoc( shape:modelToWorld( x +  r, y + 0    ) )

end

function PhysicsShapeEditorDelegateCircle:onVertDrag( id, vert )
	if id == 'C' then
		local x, y = vert:getLoc()
		local x1, y1 = self.shape:worldToModel( x, y )
		self.shape:setLoc( x1, y1 )
		self:syncVerts()
		gii.emitPythonSignal( 'entity.modified', self.shape._entity )
	else
		local x0 = self.vertC:getLocX()
		local x1 = self.vertR:getLocX()
		self.shape:setRadius( x1 - x0 )
		self:syncVerts()
		gii.emitPythonSignal( 'entity.modified', self.shape._entity )
	end
end


--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegatePolygon ( PhysicsShapeEditorDelegate )

function PhysicsShapeEditorDelegatePolygon:onInit( editor, shape )
end


--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegateEdges ( PhysicsShapeEditorDelegate )

function PhysicsShapeEditorDelegateEdges:onInit( editor, shape )
end

--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegateChain ( PhysicsShapeEditorDelegateEdges )

-- function PhysicsShapeEditorDelegateChain:onInit( editor, shape )
-- end



--------------------------------------------------------------------
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
	self:updateSelection()
end

function PhysicsShapeEditor:onSelectionChanged( selection )
	self:updateSelection()
end

function PhysicsShapeEditor:updateSelection()
	self:clearCanvasItems()
	self.delegates = {}
	local selection = self:getSelection()
	for i, e in ipairs( selection ) do
		if isInstance( e, mock.Entity ) then 
			for com in pairs( e.components ) do
				if isInstance( com, mock.PhysicsShape ) then
					self:addDelegate( com )
				end
			end
		end
	end
end

function PhysicsShapeEditor:addDelegate( shape )
	local delegate

	if isInstance( shape, mock.PhysicsShapeBox ) then
		delegate = PhysicsShapeEditorDelegateBox( self, shape )
	
	elseif isInstance( shape, mock.PhysicsShapeCircle ) then
		delegate = PhysicsShapeEditorDelegateCircle( self, shape )

	elseif isInstance( shape, mock.PhysicsShapePolygon ) then
		delegate = PhysicsShapeEditorDelegatePolygon( self, shape )

	elseif isInstance( shape, mock.PhysicsShapeEdges ) then
		delegate = PhysicsShapeEditorDelegateEdges( self, shape )

	elseif isInstance( shape, mock.PhysicsShapeChain ) then
		delegate = PhysicsShapeEditorDelegateChain( self, shape )

	else
		_error( 'unknown shape', shape:getClassName() )
		return
	end

	delegate:onInit( self, shape )
	self.delegates[ delegate ] = true
end


registerCanvasTool( 'physics_shape_editor', PhysicsShapeEditor )
