require 'mock.env'
require 'mock_edit'

function scheduleUpdate()
	return _view:scheduleUpdate()
	-- return updateCanvas()
end
--------------------------------------------------------------------
local inputDevice = mock_edit.createEditorCanvasInputDevice()

--------------------------------------------------------------------
--TODO: use a global configure for this
local ColorTable   = {}
local defaultColor = { 1,1,1,1 }

function addColor( name, r,g,b,a )
	ColorTable[ name ] = {r,g,b,a}
end

function addHexColor( name, hex, alpha )
	return addColor( name, hexcolor(hex, alpha) )
end

function applyColor( name )
	MOAIGfxDevice.setPenColor( getColor( name ) )
end

function getColor( name )
	local color = ColorTable[ name ] or defaultColor
	return unpack( color )
end

addColor( 'white', 1,1,1,1 )
addColor( 'black', 0,0,0,1 )

local alpha = 0.8
addColor( 'selection', 0,1,1, alpha )
addColor( 'handle-x',  1,0,0, alpha )
addColor( 'handle-y',  0,1,0, alpha )
addColor( 'handle-z',  0,0,1, alpha )
addColor( 'handle-all', 1,1,0, alpha )
addColor( 'handle-active', 1,1,0, alpha )
addColor( 'handle-previous', .5,.5,.5, .5 )

--------------------------------------------------------------------
local handleSize = 100
local handleArrowSize = 20

--------------------------------------------------------------------
CLASS:SceneView ( mock_edit.EditorEntity )

function SceneView:onLoad()
	self.gizmos = {}
	self.cameraCom = mock_edit.EditorCanvasCamera( _M )
	self.camera = self:addChild( 
			mock.SingleEntity( self.cameraCom )
		)

	self.grid = self:addChild( mock_edit.CanvasGrid() )
	self.navi = self:addChild( mock_edit.CanvasNavigate{ 
			inputDevice = inputDevice,
			camera      = self.camera
		} )

	self.handleLayer = self:addChild( mock_edit.CanvasHandleLayer{
			inputDevice = inputDevice,
			camera      = self.camera
		} )
	self.handleLayer:setUpdateCallback(
		function()
			scheduleUpdate()
		end
	)
	self:attach( mock.InputScript{ device = inputDevice } )

	self.gizmos  = {}
	self.handles = {}
	
	self.currentHandle = 'translation'

	self:addHandle( SelectionHandle() )
	self:connect( 'scene.serialize', 'preSceneSerialize' )

	self:readConfig()
end

function SceneView:readConfig()
	local cfg = self.scene.metaData[ 'scene_view' ]
	if not cfg then return end
	local cameraCfg = cfg['camera']
	if cameraCfg then
		self.camera:setLoc( unpack(cameraCfg['loc']) )
		self.camera:getComponent( mock_edit.EditorCanvasCamera ):setZoom( cameraCfg['zoom'] )
		self.navi.zoom = cameraCfg['zoom']
	end
end

function SceneView:addHandle( h )
	return self.handleLayer:addHandle( h )	
end

function SceneView:wndToWorld( x, y )
	return self.cameraCom:wndToWorld( x, y )
end

function SceneView:wndToEntity( ent, x, y )
	return ent:worldToModel( self:wndToWorld( x, y ) )
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

function SceneView:pick( x, y )
	for ent in pairs( self:getScene().entities ) do
		if isEntityPickable( ent ) then
			local picked = ent:pick( x, y )
			if picked then return picked end
		end
	end
	return nil
end

function SceneView:clearSelection()
	--clear gizmo
	for gizmo in pairs( self.gizmos ) do
		gizmo:destroyNow()
	end

	for handle in pairs( self.handles ) do
		handle:destroyNow()
	end
	--clear handle
	self.handles = {}
	self.gizmos = {}
	self.editTarget  = false
end


local function findTopLevelEntities( entities )
	local found = {}
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

function SceneView:onSelectionChanged( selection )
	self:clearSelection()
	local entities = {}
	for i, e in ipairs( gii.listToTable( selection ) ) do
		if isInstanceOf( e, mock.Entity ) then entities[ e ] = true end
	end

	--handle
	if next( entities ) then
		local topEntities = findTopLevelEntities( entities )
		local target
		target = mock_edit.TransformProxy()
		target:setTargets( topEntities )		
		self.editTarget = target 		
	end

	--gizmo
	for e in pairs( entities ) do
		local gizmo = self:addHandle( mock_edit.BoundGizmo() )
		gizmo:setTarget( e )
		self.gizmos[ gizmo ] = true
	end

	self:refreshEditHandle()
	scheduleUpdate()
end

function SceneView:getCurrentHandle()
	local currentHandle = self.currentHandle
	if currentHandle == 'translation' then
		return mock_edit.TranslationHandle()
	elseif currentHandle == 'rotation' then
		return mock_edit.RotationHandle()
	elseif currentHandle == 'scale' then
		return mock_edit.ScaleHandle()
	end
end

function SceneView:preSceneSerialize( scene )
	if scene ~= self.scene then return end
	local cam = self.camera
	self.scene.metaData [ 'scene_view' ] = {
		camera = {
			loc = { cam:getLoc() },
			zoom = cam:getComponent( mock_edit.EditorCanvasCamera ):getZoom(),
		}
	}
end

function SceneView:changeEditTool( name )
	local targetTool
	if name == 'translation' then --translation
		targetTool = 'translation'
	elseif name == 'rotation' then --rotation
		targetTool = 'rotation'
	elseif name == 'scale' then --rescale
		targetTool = 'scale'
	end
	if not targetTool then return _error( 'unknown edit tool', name ) end
	self.currentHandle = targetTool
	self:refreshEditHandle()
end

function SceneView:refreshEditHandle()
	for handle in pairs( self.handles ) do
		handle:destroyNow()
	end
	self.handles = {}
	if not self.editTarget then return end
	local handle = self:addHandle( self:getCurrentHandle() )
	handle:setTarget( self.editTarget )
	self.handles[ handle ] = true
	scheduleUpdate()
end

function SceneView:focusSelection()
	if not self.editTarget then return end
	self.camera:setLoc( self.editTarget:getWorldLoc() )
	--todo: fit viewport to entity bound
	scheduleUpdate()
end

--------------------------------------------------------------------
CLASS: SelectionHandle ( mock_edit.CanvasHandle )
function SelectionHandle:onMouseUp( btn, x, y )
	if btn == 'left' then
		local x1, y1 = view:wndToWorld( x, y )
		local e = view:pick( x1, y1 )
		if inputDevice:isKeyDown( 'ctrl' ) then			
			gii.addSelection( 'scene', e )
		else
			gii.changeSelection( 'scene', e )
		end
	end
end

--------------------------------------------------------------------
view = false

function openScene( scene )
	local ctx = gii.getCurrentRenderContext()	
	gii.setCurrentRenderContextActionRoot( game:getActionRoot() )
	view = scene:addEntity( SceneView() )
end

function closeScene()
	view = false
end

function onResize( w, h )
	if view then
		view.camera:getComponent( mock_edit.EditorCanvasCamera ):setScreenSize( w, h )
	end
end

function getScene()
	return scn
end
