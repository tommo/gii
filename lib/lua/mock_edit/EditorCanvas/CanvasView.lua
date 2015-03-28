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

function CanvasView:initContext()
	self:setName( '__scene_view__' )
	local inputDevice = createEditorCanvasInputDevice( self.canvasEnv )
	self:attach( mock.InputScript{ device = inputDevice } )
	self.inputDevice = inputDevice
	self.camera = self:addChild( EditorEntity() )
	self.cameraCom = self.camera:attach( EditorCanvasCamera( self.canvasEnv ) )
end

function CanvasView:initAddons()
	self.grid = self:addChild( CanvasGrid() )
	self.navi = self:addChild( CanvasNavigate{ 
			inputDevice = assert( self:getInputDevice() ),
			camera      = self:getCamera()
		} )
	self.toolManager  = self:addChild( CanvasToolManager() )
	self.gizmoManager = self:addChild( GizmoManager() )
	self.itemManager  = self:addChild( CanvasItemManager() )
end

function CanvasView:onInit()
end

function CanvasView:getInputDevice()
	return self.inputDevice
end

function CanvasView:getCamera()
	return self.camera
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

function CanvasView:updateCanvas( force )
	return self.canvasEnv.updateCanvas( force )
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
	self.gizmoManager:onSelectionChanged( selection )
	self.toolManager:onSelectionChanged( selection )
	self:updateCanvas()
end

function CanvasView:onEntityEvent( ev, entity, com ) --FIXME: remove this
	self.gizmoManager:onEntityEvent( ev, entity, com ) 
	self.toolManager:onEntityEvent( ev, entity, com )
end


