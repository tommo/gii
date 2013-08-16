require 'mock'
--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

CLASS:SceneView ( EditorEntity )

function SceneView:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
end

--------------------------------------------------------------------
CLASS: PlaceHolder( mock.Entity )

function PlaceHolder:onLoad()
	self:attach( mock.DrawScript() )
end

function PlaceHolder:onDraw()
	MOAIDraw.fillRect( -50, -50, 50, 50 )
end
--------------------------------------------------------------------

sceneView = scn:addEntity( SceneView() )

function openScene( path )
	local ctx = gii.getCurrentRenderContext()
	local scene = mock.loadAsset( path, { scene = scn } )
	scene.timer:attach( ctx.actionRoot )
	scene:addEntity( PlaceHolder() )
end

function getScene()
	return scn
end