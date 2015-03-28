module 'mock_edit'


local CanvasToolRegistry = {}
--------------------------------------------------------------------
function registerCanvasTool( id, clas )
	CanvasToolRegistry[ id ] = clas
end

--------------------------------------------------------------------
CLASS: CanvasToolManager ( SceneEventListener )
	:MODEL{}

function CanvasToolManager:__init( option )
	self.option = option or {}
	self.activeTool = false
end

function CanvasToolManager:onLoad()
	local inputDevice = self.option.inputDevice or self:getScene().inputDevice
	-- self.targetCamera = assert( self.option.camera or self:getScene().camera )
	self:attach( mock.InputScript{ 
			device = inputDevice
		} )
	self.zoom = 1
end

function CanvasToolManager:getView()
	return self.parent
end

function CanvasToolManager:getActiveTool()
	return self.activeTool
end

function CanvasToolManager:getActiveToolId()
	return self.activeTool and self.activeTool.toolId
end

function CanvasToolManager:setTool( id )
	--TODO: allow tool cache??
	local toolClass = CanvasToolRegistry[ id ]
	if not toolClass then
		_warn( 'no tool found', id )
		return false
	end

	local prevTool = self.activeTool
	if prevTool then
		prevTool:destroyWithChildrenNow()
	end

	local tool = toolClass()
	tool:installInput( self.option.inputDevice or self:getScene().inputDevice )	
	self.activeTool = tool
	self:addChild( tool )
end


function CanvasToolManager:onSelectionChanged( selection )
	if self.activeTool then
		self.activeTool:onSelectionChanged( selection )
	end
end

function CanvasToolManager:onEntityEvent( ev, entity, com )
	if self.activeTool then
		self.activeTool:onEntityEvent( ev, entity, com )
	end
end

--------------------------------------------------------------------
--------------------------------------------------------------------
CLASS: CanvasTool( SceneEventListener )

function CanvasTool:__init()
	self.items = {}
end

function CanvasTool:installInput( inputDevice )
	self:attach( mock.InputScript{ 
			device = inputDevice
		} )
end

--TODO:use more unified framework for editor canvas scene
function CanvasTool:getCurrentView()
	return self:findEntity( '__scene_view__' )
end

function CanvasTool:updateCanvas()
	self:getCurrentView():updateCanvas()
end

function CanvasTool:updateAllViews()
	--TODO:
end

function CanvasTool:onActivate()
end

function CanvasTool:onDeactivate()
end

function CanvasTool:addCanvasItem( item )
	local view = self:getCurrentView()
	view:addCanvasItem( item )
	self.items[ item ] = true
	return item
end

function CanvasTool:removeCanvasItem( item )
	if item then
		item:destroyWithChildrenNow()
	end
end

function CanvasTool:onDestroy()
	for item in pairs( self.items ) do
		item:destroyWithChildrenNow()
	end
	self:updateCanvas()
end

function CanvasTool:getSelection( key )
	return gii.getSelection( key or 'scene' )
end

function CanvasTool:pick( x, y, pad )
	local view = self:getCurrentView()
	if view then
		x, y = view:wndToWorld( x, y )
		return view:pick( x, y, pad )
	end
end

function CanvasTool:pickAndSelect( x, y, pad )
	local picked = self:pick( x, y )
	gii.changeSelection( 'scene', picked )
	return picked
end

function CanvasTool:findTopLevelEntities( entities )
	local found = {}
	if not entities then return false end
	for e in pairs( entities ) do
		local p = e.parent
		local isTop = true
		while p do
			if entities[ p ] then isTop = false break end
			p = p.parent
		end
		if isTop then found[e] = true end
	end
	return found
end

function CanvasTool:onSelectionChanged( selection )
end

