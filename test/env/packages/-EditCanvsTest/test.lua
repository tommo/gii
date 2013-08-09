local canvasWidth, canvasHeight = 100, 100
local canvasCameras = {}

function onResize( w, h )
	canvasWidth, canvasHeight = w, h
	for cam in pairs( canvasCameras ) do
		cam:updateViewport()
	end
end

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

---
CLASS: PlaceHolder( mock.Entity )
function PlaceHolder:onLoad()
	self:attach( mock.DrawScript() )
	self:attach( mock.InputScript() )
end

function PlaceHolder:onDraw()
	MOAIDraw.fillRect( -50, -50, 50, 50 )
end

function PlaceHolder:onMouseMove( x, y )
	self:setRot( 0, y, x )
end

function PlaceHolder:onKeyDown( key )
	print( key )
end

---
CLASS: TestScene ( mock.Scene )
function TestScene:onEnter()
	camera = self:addEntity( mock.SingleEntity( EditCanvasCamera() ) )
	self:addEntity( PlaceHolder() )	
end

function TestScene:getActionRoot()
	local ctx = gii.getCurrentRenderContext()
	return ctx.actionRoot
end

--------------------------------------------------------------------
function onStart()
	testScene = TestScene()
	testScene:enter()
	_owner:startUpdateTimer( 30 )
	running = true	
end

local running = false
function onMouseUp()
	if running then
		running = false
		_owner:stopUpdateTimer()
	else
		running = true
		_owner:startUpdateTimer( 30 )
	end
end

function onMouseMove( x, y )
	if camera then
		camera:setLoc(  - x + canvasWidth/2, y - canvasHeight/2 )
	end
end