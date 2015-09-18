module 'mock_edit'

CLASS:CanvasView ( EditorEntity )

function CanvasView:__init( canvasEnv )
	self.canvasEnv = assert( canvasEnv )
	
	--config
	self.gridSnapping = false

end

function CanvasView:onLoad()
	self:initContext()
	self:initAddons()
	self:onInit()
	self:connect( 'scene.entity_event', 'onEntityEvent' )
end

function CanvasView:createCamera( canvasEnv )
	local cameraEntity = EditorEntity()
	local cameraCom    = EditorCanvasCamera( canvasEnv )
	cameraEntity:attach( cameraCom )
	self:addChild( cameraEntity )
	return cameraEntity, cameraCom
end

function CanvasView:initContext()
	self:setName( '__scene_view__' )
	local inputDevice = createEditorCanvasInputDevice( self.canvasEnv )
	self:attach( mock.InputScript{ device = inputDevice } )
	self.inputDevice = inputDevice
	self.camera, self.cameraCom = self:createCamera( self.canvasEnv )
end

function CanvasView:initAddons()
	self.grid = self:addChild( CanvasGrid() )
	self.navi = self:addChild( CanvasNavigate{ 
			inputDevice = assert( self:getInputDevice() ),
			camera      = self:getCamera()
		} )
	self.toolManager    = self:addChild( CanvasToolManager() )
	self.gizmoManager   = self:addChild( GizmoManager() )
	self.itemManager    = self:addChild( CanvasItemManager() )
	self.pickingManager = PickingManager()
	self.pickingManager:setTargetScene( self:getScene() )
end

function CanvasView:onInit()
end

function CanvasView:getInputDevice()
	return self.inputDevice
end

function CanvasView:getCamera()
	return self.camera
end

function CanvasView:getCameraComponent()
	return self.cameraCom
end

function CanvasView:wndToWorld( x, y )
	return self.cameraCom:wndToWorld( x, y )
end

function CanvasView:addCanvasItem( item )
	self.itemManager:addItem( item )
end

function CanvasView:removeCanvasItem( item )
	self.itemManager:removeItem( item )
end

function CanvasView:changeEditTool( name )
	self.toolManager:setTool( name )
end

function CanvasView:getActiveTool()
	return self.toolManager:getActiveTool()
end

function CanvasView:getActiveToolId()
	return self.toolManager:getActiveToolId()
end

function CanvasView:updateCanvas( force )
	return self.canvasEnv.updateCanvas()
end

function CanvasView:toggleDebugLines()
	self.cameraCom:setShowDebugLines( not self.cameraCom.showDebugLines )
	self:updateCanvas()
end

function CanvasView:onCanvasResize( w, h )
	self.camera:getComponent( EditorCanvasCamera ):setScreenSize( w, h )
end

function CanvasView:onSelectionChanged( selection )
	selection = gii.listToTable( selection )
	--TODO:use signal or message for this
	self.gizmoManager :onSelectionChanged( selection )
	self.toolManager  :onSelectionChanged( selection )
	self:updateCanvas()
end

function CanvasView:onEntityEvent( ev, entity, com ) --FIXME: remove this
	self.gizmoManager   :onEntityEvent ( ev, entity, com )
	self.toolManager    :onEntityEvent ( ev, entity, com )
	self.pickingManager :onEntityEvent ( ev, entity, com )
end


function CanvasView:pick( x, y, pad )
	return self.pickingManager:pickPoint( x, y, pad )
end

function CanvasView:pickRect( x0, y0, x1, y1, pad )
	return self.pickingManager:pickRect( x0, y0, x1, y1, pad )
end

function CanvasView:pickAndSelect( x, y, pad )
	local picked = self:pick( x, y, pad )
	gii.changeSelection( 'scene', unpack( picked ) )
	return picked
end


--------------------------------------------------------------------
function CanvasView:setGridSize( w, h )
	return self.grid:setSize( w, h )
end

function CanvasView:getGridSize()
	return self.grid:getSize()
end

function CanvasView:getGridWidth()
	return self.grid:getWidth()
end

function CanvasView:getGridHeight()
	return self.grid:getHeight()
end

function CanvasView:setGridWidth( w )
	return self.grid:setWidth( w )
end

function CanvasView:setGridHeight( h )
	return self.grid:setHeight( h )
end

function CanvasView:isGridVisible()
	return self.grid:isVisible()
end

function CanvasView:setGridVisible( vis )
	self.grid:setVisible( vis )
end

function CanvasView:isGridSnapping()
	return self.gridSnapping
end

function CanvasView:setGridSnapping( snapping )
	self.gridSnapping = snapping
end

function CanvasView:snapLoc( x,y,z, activeAxis )
	--2d
	if not self.gridSnapping then return x,y,z end
	local gw, gh = self:getGridSize()
	local x1 = math.floor( x/gw ) * gw
	local y1 = math.floor( y/gh ) * gh
	local dx = x - x1
	if dx > gw*0.5 then
		x1 = x1 + gw
		dx = dx - gw
	end
	local dy = y - y1
	if dy > gh*0.5 then
		y1 = y1 + gh
		dy = dy - gh
	end
	local snapX = true --dx*dx < gw*gw*0.09
	local snapY = true --dy*dy < gh*gh*0.09
	if activeAxis == 'x' then
		snapY = true
	elseif activeAxis == 'y' then
		snapX = true
	end
	if snapX and snapY then
		return x1,y1,z
	else
		return x,y,z
	end

end
