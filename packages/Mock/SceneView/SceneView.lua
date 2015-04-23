require 'mock.env'
require 'mock_edit'

--------------------------------------------------------------------
view = false

function onSceneOpen( scene )
	-- local ctx = gii.getCurrentRenderContext()	
	-- local gameActionRoot = game:getActionRoot()
	-- gii.setCurrentRenderContextActionRoot( game:getActionRoot() )
	view = mock_edit.createSceneView( scene, _M )
	scene:addEntity( view )
end

function onSceneClose()
	view = false
end

function onResize( w, h )
	if view then view:onCanvasResize( w, h ) end
end

