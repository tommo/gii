require 'mock'
--------------------------------------------------------------------
local inputDevice = createEditorCanvasInputDevice()

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
addColor( 'handle-x', 1,0,0, alpha )
addColor( 'handle-y', 0,1,0, alpha )
addColor( 'handle-z', 0,0,1, alpha )
addColor( 'handle-all', 1,1,0, alpha )

--------------------------------------------------------------------
local handleSize = 100
local handleArrowSize = 20

--------------------------------------------------------------------
CLASS:SceneView ( EditorEntity )

function SceneView:onLoad()
	self.gizmos = {}
	self.cameraCom = EditorCanvasCamera( _M )
	self.camera = self:addChild( 
			mock.SingleEntity( self.cameraCom )
		)

	self.grid = self:addChild( CanvasGrid() )
	self.navi = self:addChild( CanvasNavigate{ 
			inputDevice = inputDevice,
			camera      = self.camera
		} )

	self.handleLayer = self:addChild( CanvasHandleLayer{
			inputDevice = inputDevice,
			camera      = self.camera
		} )

	self:attach( mock.InputScript{ device = inputDevice } )

	self.gizmos  = {}
	self.handles = {}

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
		self.camera:getComponent( EditorCanvasCamera ):setZoom( cameraCfg['zoom'] )
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

function SceneView:pick( x, y )
	for ent in pairs( self:getScene().entities ) do
		if not ent.FLAG_EDITOR_OBJECT then
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
end

function SceneView:onSelectionChanged( selection )
	self:clearSelection()
	for i, e in ipairs( gii.listToTable( selection ) ) do
		if isInstanceOf( e, mock.Entity ) then
			--manipulator
			local handle = self:addHandle( TranslationHandle() )
			handle:setTarget( e )
			self.handles[ handle ] = true
			--gizmo
			local gizmo = self:addHandle( BoundGizmo() )
			gizmo:setTarget( e )
			self.gizmos[ gizmo ] = true
		end
	end
	updateCanvas()
	
end

function SceneView:preSceneSerialize( scene )
	if scene ~= self.scene then return end
	local cam = self.camera
	self.scene.metaData [ 'scene_view' ] = {
		camera = {
			loc = { cam:getLoc() },
			zoom = cam:getComponent( EditorCanvasCamera ):getZoom(),
		}
	}
end

--------------------------------------------------------------------
CLASS: SelectionHandle ( CanvasHandle )
function SelectionHandle:onMouseUp( btn, x, y )
	if btn == 'left' then
		local x1, y1 = view:wndToWorld( x, y )
		local e = view:pick( x1, y1 )
		gii.changeSelection( 'scene', e )
	end
end

--------------------------------------------------------------------
CLASS: BoundGizmo( CanvasHandle )
function BoundGizmo:onLoad()
	self.target = false
	self:attach( mock.DrawScript() )
end

function BoundGizmo:setTarget( e )
	self.target = e
end

function BoundGizmo:onDraw()
	local target = self.target
	if not target then return end
	applyColor 'selection'
	for com in pairs( target.components ) do
		local drawBounds = com.drawBounds
		if drawBounds then drawBounds( com ) end
	end
end

--------------------------------------------------------------------
CLASS: TranslationHandle( CanvasHandle )
function TranslationHandle:__init( option )
	self.option = option
	self.activeAxis = false
end

function TranslationHandle:onLoad()
	local option = self.option
	self:attach( mock.DrawScript() )	
end

function TranslationHandle:onDraw()
	applyColor 'handle-all'
	MOAIDraw.fillRect( 0,0, handleArrowSize, handleArrowSize )
	--x axis
	applyColor 'handle-x'
	MOAIDraw.drawLine( 0,0, handleSize, 0 )
	MOAIDraw.fillFan(
		handleSize,  handleArrowSize/3, 
		handleSize + handleArrowSize, 0,
		handleSize, -handleArrowSize/3
		-- handleSize,  handleArrowSize/3
		)
	-- MOAIDraw.fillFan( 0,0, handleSize / 5, handleSize / 5 )
	--y axis
	applyColor 'handle-y'
	MOAIDraw.drawLine( 0,0, 0, handleSize )
	MOAIDraw.fillFan(
		handleArrowSize/3, handleSize, 
		0, handleSize + handleArrowSize,
		-handleArrowSize/3, handleSize 
		-- handleArrowSize/3, handleSize, 
		)
end

function TranslationHandle:setTarget( target )
	self.target = target
	linkLoc( self:getProp(), target:getProp() )
end

function TranslationHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	x, y = self:wndToModel( x, y )
	self.x0 = x
	self.y0 = y
	if x >= 0 and y >= 0 and x <= handleArrowSize + 5 and y <= handleArrowSize + 5 then
		self.activeAxis = 'all'
		return true
	end
	if math.abs( y ) < 5 and x <= handleSize + handleArrowSize then
		self.activeAxis = 'x'
		return true
	end
	if math.abs( x ) < 5 and y <= handleSize + handleArrowSize then
		self.activeAxis = 'y'
		return true
	end
end

function TranslationHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.activeAxis then return end
	self.activeAxis = false
	return true
end

function TranslationHandle:onMouseMove( x, y )
	if not self.activeAxis then return end
	local target = self.target
	target:forceUpdate()
	self:forceUpdate()
	x, y = self:wndToModel( x, y )
	local dx = x - self.x0
	local dy = y - self.y0
	if self.activeAxis == 'all' then
		target:addLoc( dx, dy )
	elseif self.activeAxis == 'x' then
		target:addLoc( dx, 0 )
	elseif self.activeAxis == 'y' then
		target:addLoc( 0, dy )
	end
	gii.emitPythonSignal( 'entity.modified', target, 'view' )
	updateCanvas()
	return true
end


--------------------------------------------------------------------
CLASS: ScaleHandle( CanvasHandle )
function ScaleHandle:__init( option )
	self.option = option
	self.activeAxis = false
end

function ScaleHandle:onLoad()
	local option = self.option
	self:attach( mock.DrawScript() )	
end

function ScaleHandle:onDraw()
	applyColor 'handle-all'
	MOAIDraw.fillRect( 0,0, handleArrowSize, handleArrowSize )
	--x axis
	applyColor 'handle-x'
	MOAIDraw.drawLine( 0,0, handleSize, 0 )
	MOAIDraw.fillFan(
		handleSize,  handleArrowSize/3, 
		handleSize + handleArrowSize, 0,
		handleSize, -handleArrowSize/3
		-- handleSize,  handleArrowSize/3
		)
	-- MOAIDraw.fillFan( 0,0, handleSize / 5, handleSize / 5 )
	--y axis
	applyColor 'handle-y'
	MOAIDraw.drawLine( 0,0, 0, handleSize )
	MOAIDraw.fillFan(
		handleArrowSize/3, handleSize, 
		0, handleSize + handleArrowSize,
		-handleArrowSize/3, handleSize 
		-- handleArrowSize/3, handleSize, 
		)
end

function ScaleHandle:setTarget( target )
	self.target = target
	linkLoc( self:getProp(), target:getProp() )
end

function ScaleHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	x, y = self:wndToModel( x, y )
	self.x0 = x
	self.y0 = y
	if x >= 0 and y >= 0 and x <= handleArrowSize + 5 and y <= handleArrowSize + 5 then
		self.activeAxis = 'all'
		return true
	end
	if math.abs( y ) < 5 and x <= handleSize + handleArrowSize then
		self.activeAxis = 'x'
		return true
	end
	if math.abs( x ) < 5 and y <= handleSize + handleArrowSize then
		self.activeAxis = 'y'
		return true
	end
end

function ScaleHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.activeAxis then return end
	self.activeAxis = false
	return true
end

function ScaleHandle:onMouseMove( x, y )
	if not self.activeAxis then return end
	local target = self.target
	target:forceUpdate()
	self:forceUpdate()
	x, y = self:wndToModel( x, y )
	local dx = x - self.x0
	local dy = y - self.y0
	if self.activeAxis == 'all' then
		target:addLoc( dx, dy )
	elseif self.activeAxis == 'x' then
		target:addLoc( dx, 0 )
	elseif self.activeAxis == 'y' then
		target:addLoc( 0, dy )
	end
	gii.emitPythonSignal( 'entity.modified', target, 'view' )
	updateCanvas()
	return true
end

--------------------------------------------------------------------
view = false

function openScene( scene )
	local ctx = gii.getCurrentRenderContext()
	view = scene:addEntity( SceneView() )
end

function closeScene()
	view = false
end

function onResize( w, h )
	if view then
		view.camera:getComponent( EditorCanvasCamera ):setScreenSize( w, h )
	end
end

function getScene()
	return scn
end
