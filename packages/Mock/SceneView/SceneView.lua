require 'mock'

local canvasWidth, canvasHeight = 100, 100
local canvasCameras = {}

function onResize( w, h )
	canvasWidth, canvasHeight = w, h
	for cam in pairs( canvasCameras ) do
		cam:updateViewport()
	end
end

----
CLASS: EditorEntity( mock.Entity )
function EditorEntity:__init()
	self.__editor_entity  = true
end
----

CLASS: EditCanvasCamera ( mock.Camera )
function EditCanvasCamera:__init()
	canvasCameras[ self ] = true
	self.context = gii.getCurrentRenderContextKey()
	print( 'camera context:', self.context )
	self:setRot(0,0,45)
end

function EditCanvasCamera:getGameViewRect()
	return 0, 0, canvasWidth, canvasHeight
end

function EditCanvasCamera:getGameViewScale()
	return canvasWidth, canvasHeight
end


--------------------------------------------------------------------
function onStart()
	
end

function openScene( path )
	local ctx = gii.getCurrentRenderContext()
	local s = mock.loadAsset( path )
	s.timer:attach( ctx.actionRoot )
	
	local cam = EditorEntity()
	cam:attach( EditCanvasCamera() )
	s:addEntity( cam )
end
