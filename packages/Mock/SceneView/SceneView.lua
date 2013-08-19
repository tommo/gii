require 'mock'
--------------------------------------------------------------------
scn = gii.createMockEditorScene()
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
addColor( 'selection', 1,1,0, alpha )
addColor( 'handle-x', 1,0,0, alpha )
addColor( 'handle-y', 0,1,0, alpha )
addColor( 'handle-z', 0,0,1, alpha )


--------------------------------------------------------------------
CLASS:SceneView ( EditorEntity )

function SceneView:onLoad()
	self.gizmos = {}

	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = self:getScene().inputDevice } )

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
	gii.changeSelection( e )
	local gizmo = self:addSibling( SelectionGizmo() )
	gizmo:setTarget( e )
	self.gizmos[ e ] = gizmo
	updateCanvas()
end

function SceneView:clearSelection()
end

function SceneView:pick( x, y )
	for ent in pairs( scn.entities ) do
		if not ent.__editor_entity then
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
		local getBounds = com.getBounds
		if getBounds then
			local x1,y1,z1, x2,y2,z2 = getBounds( com )
			GIIHelper.setVertexTransform( com )
			MOAIDraw.drawRect( x1,y1,x2,y2 )
		end
	end
	
end


--------------------------------------------------------------------

sceneView = scn:addEntity( SceneView() )

function openScene( path )
	local ctx = gii.getCurrentRenderContext()
	local scene = mock.loadAsset( path, { scene = scn } )
	scene.timer:attach( ctx.actionRoot )
end

function getScene()
	return scn
end