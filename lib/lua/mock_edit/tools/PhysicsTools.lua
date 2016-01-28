module 'mock_edit'


--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegate ()
	:MODEL{}

function PhysicsShapeEditorDelegate:__init( editor, shape )
	self.editor = editor
	self.shape  = shape
	self.items  = {}
end

function PhysicsShapeEditorDelegate:addCanvasItem( item )
	self.items[item] = true
	return self.editor:addCanvasItem( item )
end

function PhysicsShapeEditorDelegate:removeCanvasItem( item )
	self.items[item] = nil
	self.editor:removeCanvasItem( item )
end

function PhysicsShapeEditorDelegate:clearCanvasItems()
	for item in pairs( self.items ) do
		self.editor:removeCanvasItem( item )
	end
	self.items = {}
end

function PhysicsShapeEditorDelegate:onDestroy()
	self:clearCanvasItems()
end

--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegateBox ( PhysicsShapeEditorDelegate )

function PhysicsShapeEditorDelegateBox:onInit( editor, shape )
	local rect = self:addCanvasItem( CanvasItemRect() )
	function rect:onPullAttr() --x,y,radius
		local x, y = shape:getLoc()
		local w, h = shape:getSize()
		local rot  = shape:getRotation()
		x, y = shape:modelToWorld( x, y )
		return x, y, w, h, rot
	end

	function rect:onPushAttr( x,y, w,h,  rot )
		shape:forceUpdate()
		local x, y = shape:worldToModel( x, y )
		shape:setLoc( x, y )
		shape:setSize( w, h )
		shape:setRotation( rot )
		gii.emitPythonSignal( 'entity.modified', shape._entity )
		mock.markProtoInstanceFieldsOverrided(
			shape, 
			'loc', 'w', 'h'
		)
	end

	rect:updateShape()
end


--------------------------------------------------------------------
CLASS: PhysicsShapeEditorDelegateCircle ( PhysicsShapeEditorDelegate )

function PhysicsShapeEditorDelegateCircle:onInit( editor, shape )
	local circle = self:addCanvasItem( CanvasItemCircle() )
	function circle:onPullAttr() --x,y,radius
		local x, y = shape:getLoc()
		x, y = shape:modelToWorld( x, y )
		local r    = shape:getRadius()
		return x, y, r
	end

	function circle:onPushAttr( x,y, radius )
		shape:forceUpdate()
		local x, y = shape:worldToModel( x, y )
		shape:setLoc( x, y )
		shape:setRadius( radius )
		gii.emitPythonSignal( 'entity.modified', shape._entity )
		mock.markProtoInstanceFieldsOverrided(
			shape, 
			'loc',
			'radius'
		)
	end

	circle:updateShape()

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
CLASS: PhysicsShapeEditor ( SelectionTool )
	:MODEL{}

function PhysicsShapeEditor:__init()
	self.delegates = {}
end

function PhysicsShapeEditor:onLoad()
	PhysicsShapeEditor.__super.onLoad( self )
	self:updateSelection()
end

function PhysicsShapeEditor:onSelectionChanged( selection )
	self:updateSelection()
end

function PhysicsShapeEditor:updateSelection()
	--rebuild delegates
	for delegate in pairs( self.delegates ) do
		delegate:onDestroy()
	end
	
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

	elseif isInstance( shape, mock.PhysicsShapeBevelBox ) then
		delegate = PhysicsShapeEditorDelegateBox( self, shape )
	
	elseif isInstance( shape, mock.PhysicsShapeCircle ) then
		delegate = PhysicsShapeEditorDelegateCircle( self, shape )

	elseif isInstance( shape, mock.PhysicsShapePolygon ) then
		delegate = PhysicsShapeEditorDelegatePolygon( self, shape )

	elseif isInstance( shape, mock.PhysicsShapeEdges ) then
		delegate = PhysicsShapeEditorDelegateEdges( self, shape )

	elseif isInstance( shape, mock.PhysicsShapeChain ) then
		delegate = PhysicsShapeEditorDelegateChain( self, shape )

	elseif isInstance( shape, mock.PhysicsShapePie ) then
		return
	else
		_error( 'unknown shape', shape:getClassName() )
		return
	end

	delegate:onInit( self, shape )
	self.delegates[ delegate ] = true
end


registerCanvasTool( 'physics_shape_editor', PhysicsShapeEditor )
