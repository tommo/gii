----
CLASS: EditCanvasCamera ( mock.Camera )
function EditCanvasCamera:__init()
	canvasCameras[ self ] = true
	self.context = gii.getCurrentRenderContextKey()
end

function EditCanvasCamera:getGameViewRect()
	return 0, 0, canvasWidth, canvasHeight
end

function EditCanvasCamera:getGameViewScale()
	return canvasWidth, canvasHeight
end
