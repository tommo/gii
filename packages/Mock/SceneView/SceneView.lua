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
CLASS:SceneView ( EditorEntity )

function SceneView:onLoad()
	self.gizmos = {}
	
	self.camera = self:addChild( 
			mock.SingleEntity( EditorCanvasCamera( _M ) )
		)

	self.grid = self:addChild( CanvasGrid() )
	self.navi = self:addChild( CanvasNavigate{ 
			inputDevice = inputDevice,
			camera      = self.camera
		} )
	self:attach( mock.InputScript{ device = inputDevice } )
end

function SceneView:onMouseDown( btn, x, y )
	if btn == 'left' then
		x, y = self:wndToWorld( x, y )
		local e = self:pick( x, y )
		if e then
			self:selectEntity( e )
		end
	end
end

function SceneView:selectEntity( e, additive )
	gii.changeSelection( 'scene', e )
	-- local gizmo = self:addSibling( SelectionGizmo() )
	-- gizmo:setTarget( e )
	-- self.gizmos[ e ] = gizmo

	self.handle = self:addSibling( TranslationHandle{ inputDevice = inputDevice } )
	self.handle:setTarget( e )
	updateCanvas()
end

function SceneView:clearSelection()
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

--------------------------------------------------------------------
CLASS: SelectionGizmo( EditorEntity )

function SelectionGizmo:onLoad()
	self.target = false
	self:attach( mock.DrawScript() )
end

function SelectionGizmo:setTarget( e )
	self.target = e
end

function SelectionGizmo:onDraw()
	local target = self.target
	if not target then return end
	applyColor 'selection'
	for com in pairs( target.components ) do
		local drawBounds = com.drawBounds
		if drawBounds then drawBounds( com ) end
	end
	
end

--------------------------------------------------------------------
local handleSize = 120
local handleArrowSize = 30

CLASS: TranslationHandle( EditorEntity )
function TranslationHandle:__init( option )
	self.option = option
	self.activeAxis = false
	
end

function TranslationHandle:onLoad()
	local option = self.option
	self:attach( mock.DrawScript() )
	self:attach( mock.InputScript{ 
			device = assert( option.inputDevice )
		} )
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
	inheritTransform( self:getProp(), target:getProp() )
end

function TranslationHandle:onMouseDown( btn, x, y )
	if btn~='left' then return end
	x, y = self:wndToModel( x, y )
	self.x0 = x
	self.y0 = y
	if x >= 0 and y >= 0 and x <= handleArrowSize and y <= handleArrowSize then
		self.activeAxis = 'all'
		return
	end
	if math.abs( y ) < 5 and x <= handleSize + handleArrowSize then
		self.activeAxis = 'x'
		return
	end
	if math.abs( x ) < 5 and y <= handleSize + handleArrowSize then
		self.activeAxis = 'y'
		return
	end
	updateCanvas()
end

function TranslationHandle:onMouseUp( btn, x, y )
	if btn~='left' then return end
	if not self.activeAxis then return end
	self.activeAxis = false
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
