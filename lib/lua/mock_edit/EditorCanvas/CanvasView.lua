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


local function isEntityPickable( ent )
	if ent.FLAG_EDITOR_OBJECT then return false end
	if not ent:isVisible() then return false end
	local layerSrc = ent.layer.source
	if not layerSrc:isVisible() then return false end
	if not layerSrc:isEditorVisible() then return false end
	if layerSrc.editorSolo == 'hidden' then return false end
	if layerSrc:isLocked() then return false end
	return true
end

local function _pick( ent, x, y ) --depth first search
	if not isEntityPickable( ent ) then return nil end
	-- local children = ent.children
	-- if children then
	-- 	for child in pairs( children ) do
	-- 		local pickedEnt = _pick( child, x, y )
	-- 		if pickedEnt then return pickedEnt end
	-- 	end
	-- end
	local picked = ent:pick( x, y )
	if picked then return ent end
	return nil
end

function CanvasView:pick( x, y )
	--TODO: use layer order?
	x, y = self:wndToWorld( x, y )
	local candidates = {}
	for ent in pairs( self:getScene().entities ) do
		-- if isEntityPickable( ent ) and ent:inside( x, y ) then
		-- 	table.insert( candidates, ent )
		-- end
		if not ent.parent then
			local p = _pick( ent, x, y )
			if p then
				table.insert( candidates, p )
			end
		end
	end

	--TODO:sort and find
	return candidates[1]
end

function CanvasView:pickAndSelect( x, y, pad )
	local picked = self:pick( x, y, pad )
	gii.changeSelection( 'scene', picked )
	return picked
end
