require 'mock.env'
require 'mock_edit'

function scheduleUpdate()
	-- return _view:scheduleUpdate()
	return updateCanvas()
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
addColor( 'handle-x', 1,0,0, alpha )
addColor( 'handle-y', 0,1,0, alpha )
addColor( 'handle-z', 0,0,1, alpha )
addColor( 'handle-all', 1,1,0, alpha )
addColor( 'handle-active', 1,1,0, alpha )

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

	self:attach( mock.InputScript{ device = inputDevice } )

	self.gizmos  = {}
	self.handles = {}
	
	self.currentHandle = 'rotation'

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
	if not ent.layer.source:isVisible() then return false end
	if ent.layer.source:isLocked() then return false end
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
		local count = table.len( topEntities )
		if count > 1 then
			target = TransformProxy()
			target:setTargets( topEntities )
		else
			target = next( topEntities )
		end
		local handle = self:addHandle( self:getCurrentHandle() )
		handle:setTarget( target )
		self.handles[ handle ] = true
	end
	--gizmo
	for e in pairs( entities ) do
		local gizmo = self:addHandle( BoundGizmo() )
		gizmo:setTarget( e )
		self.gizmos[ gizmo ] = true
	end
	scheduleUpdate()
end

function SceneView:getCurrentHandle()
	local currentHandle = self.currentHandle
	if currentHandle == 'translation' then
		return TranslationHandle()
	elseif currentHandle == 'rotation' then
		return RotationHandle()
	elseif currentHandle == 'scale' then
		return ScaleHandle()
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

function SceneView:onKeyDown( key )
	if key == 'w' then --translation
		self.currentHandle = 'translation'
	elseif key == 'e' then --rotation
		self.currentHandle = 'rotation'
	elseif key == 'r' then --rescale
		self.currentHandle = 'scale'
	end
end

--------------------------------------------------------------------
CLASS: TransformProxy( mock.Entity )

function TransformProxy:__init()
	self.updateNode = MOAIScriptNode.new()
	self.updateNode:setCallback( function() self:onUpdate() end )
	self.updateNode:setNodeLink( self._prop )
end

function TransformProxy:setTargets( targets )
	self.targets = targets
	local proxies = {}
	local count = 0

	local totalX, totalY = 0, 0
	for e in pairs( targets ) do
		local x1,y1 = e:getWorldLoc()
		totalX = totalX + x1
		totalY = totalY + y1
		count = count + 1
	end

	local trans = self._prop
	trans:setLoc( totalX/count, totalY/count, 0 )
	trans:forceUpdate()
	for e in pairs( targets ) do
		local proxy = MOAITransform.new()
		proxies[e] = proxy
		inheritTransform( proxy, trans )
		e:forceUpdate()
		local x, y = trans:worldToModel( e:getWorldLoc( 0, 0 ) )
		proxy:setLoc( x, y )
	end
	self.proxies = proxies
	self:onUpdate()
end

local function setWorldLoc( e, x, y )
	local p = e.parent
	if p then
		x, y = p:worldToModel( x, y )
		e:setLoc( x, y )
	else
		e:setLoc( x, y )
	end
end

function TransformProxy:onUpdate()
	for e, proxy in pairs( self.proxies ) do
		proxy:forceUpdate()
		local x,y = proxy:modelToWorld( 0,0,0 )
		setWorldLoc( e, x, y )

	end
end


--------------------------------------------------------------------
CLASS: SelectionHandle ( mock_edit.CanvasHandle )
function SelectionHandle:onMouseUp( btn, x, y )
	if btn == 'left' then
		local x1, y1 = view:wndToWorld( x, y )
		local e = view:pick( x1, y1 )
		gii.changeSelection( 'scene', e )
	end
end

--------------------------------------------------------------------
CLASS: BoundGizmo( mock_edit.CanvasHandle )
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
	if not target.components then 
		return self:destroy()
	end
	for com in pairs( target.components ) do
		local drawBounds = com.drawBounds
		if drawBounds then drawBounds( com ) end
	end
end

--------------------------------------------------------------------
CLASS: TranslationHandle( mock_edit.CanvasHandle )
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

function TranslationHandle:wndToTarget( x, y )
	local x, y = self:wndToWorld( x, y )
	if self.target then 
		local parent = self.target.parent
		if parent then
			return parent:worldToModel( x, y )
		end
	end
	return x, y
end

function TranslationHandle:setTarget( target )
	self.target = target
	inheritLoc( self:getProp(), target:getProp() )
end

function TranslationHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	self.x0, self.y0 = self:wndToTarget( x, y )	
	x, y = self:wndToModel( x, y )
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
	x, y = self:wndToTarget( x, y )
	local dx = x - self.x0
	local dy = y - self.y0
	self.x0, self.y0 = x, y 
	local tx, ty = self.target:getLoc()
	
	local mode = 'global'
	local parent = target.parent
	if parent and mode == 'global' then
		local wx, wy   = target:getWorldLoc( 0,0,0 )
		local wx1, wy1 = parent:modelToWorld( tx + dx, ty + dy )
		if self.activeAxis == 'all' then
			--pass			
		elseif self.activeAxis == 'x' then
			wy1 = wy
		elseif self.activeAxis == 'y' then
			wx1 = wx
		end
		tx, ty = parent:worldToModel( wx1, wy1 )
	else
		if self.activeAxis == 'all' then
			tx = tx + dx
			ty = ty + dy
		elseif self.activeAxis == 'x' then
			tx = tx + dx
		elseif self.activeAxis == 'y' then
			ty = ty + dy
		end
	end
	target:setLoc( tx, ty )
	
	gii.emitPythonSignal( 'entity.modified', target, 'view' )
	scheduleUpdate()
	return true
end


--------------------------------------------------------------------
CLASS: RotationHandle( mock_edit.CanvasHandle )
function RotationHandle:__init( option )
	self.option = option
	self.align  = false
	self.active = false
end

function RotationHandle:onLoad()
	self:attach( mock.DrawScript() )
end

function RotationHandle:setTarget( target )
	self.target = target
	inheritLoc( self:getProp(), target:getProp() )
end

function RotationHandle:onDraw()
	if self.active then
		applyColor 'handle-active'
	else
		applyColor 'handle-z'
	end
	MOAIDraw.fillCircle( 0, 0, 5 )
	MOAIDraw.drawCircle( 0, 0, 80 )
end

function RotationHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	local x1, y1 = self:wndToModel( x, y )
	local r = distance( 0,0, x1,y1 )
	if r > 80 then return end
	local rx,ry,rz = self.target:getRot()
	self.rot0 = rz
	self.dir0 = direction( 0,0, x1,y1 )
	self.active = true
	scheduleUpdate()
	return true
end

function RotationHandle:onMouseMove( x, y )
	if not self.active then return end
	local x1, y1 = self:wndToModel( x, y )
	local r = distance( 0,0, x1,y1 )
	if r>5 then
		local dir = direction( 0,0, x1,y1)
		local ddir = dir - self.dir0
		local rx,ry,rz = self.target:getRot()
		rz = self.rot0 + ddir * 180/math.pi
		self.target:setRot( rx, ry, rz )
		gii.emitPythonSignal( 'entity.modified', self.target, 'view' )
		scheduleUpdate()
	end
	return true
end

function RotationHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.active then return end
	self.active = false
	scheduleUpdate()
	return true
end

--------------------------------------------------------------------
CLASS: ScaleHandle( mock_edit.CanvasHandle )
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
	MOAIDraw.fillRect( 0, 0, handleArrowSize, handleArrowSize )
	--x axis
	applyColor 'handle-x'
	MOAIDraw.drawLine( 0, 0, handleSize, 0 )
	MOAIDraw.fillRect( handleSize,0, handleSize + handleArrowSize, handleArrowSize )
	--y axis
	applyColor 'handle-y'
	MOAIDraw.drawLine( 0, 0, 0, handleSize )
	MOAIDraw.fillRect( 0, handleSize, handleArrowSize, handleSize + handleArrowSize )
end

function ScaleHandle:setTarget( target )
	self.target = target
	inheritLoc( self:getProp(), target:getProp() )
end

function ScaleHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	x, y = self:wndToModel( x, y )
	self.x0 = x
	self.y0 = y
	if x >= -5 and y >= -5 and x <= handleArrowSize + 5 and y <= handleArrowSize + 5 then
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
	x, y = self:wndToTarget( x, y )
	local dx = x - self.x0
	local dy = y - self.y0
	self.x0, self.y0 = x, y 
	local tx, ty = self.target:getLoc()
	
	local mode = 'global'
	local parent = target.parent
	if parent and mode == 'global' then
		local wx, wy   = target:getWorldLoc( 0,0,0 )
		local wx1, wy1 = parent:modelToWorld( tx + dx, ty + dy )
		if self.activeAxis == 'all' then
			--pass			
		elseif self.activeAxis == 'x' then
			wy1 = wy
		elseif self.activeAxis == 'y' then
			wx1 = wx
		end
		tx, ty = parent:worldToModel( wx1, wy1 )
	else
		if self.activeAxis == 'all' then
			tx = tx + dx
			ty = ty + dy
		elseif self.activeAxis == 'x' then
			tx = tx + dx
		elseif self.activeAxis == 'y' then
			ty = ty + dy
		end
	end
	target:setLoc( tx, ty )
	
	gii.emitPythonSignal( 'entity.modified', target, 'view' )
	scheduleUpdate()
	return true
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
