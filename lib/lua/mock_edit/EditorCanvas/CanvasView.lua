module 'mock_edit'

CLASS:CanvasView ( EditorEntity )

function CanvasView:__init( canvasEnv )
	self.canvasEnv = assert( canvasEnv )
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
