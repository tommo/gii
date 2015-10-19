module 'mock_edit'
--------------------------------------------------------------------
--EditorCanvasCamera
--------------------------------------------------------------------
CLASS: EditorCanvasCamera ( mock.Camera )
function EditorCanvasCamera:__init( env )
	self.FLAG_EDITOR_OBJECT = true
	context = gii.getCurrentRenderContext()
	self.context = context.key
	self.env = env
	self.parallaxEnabled = false
end

function EditorCanvasCamera:loadPasses()
	self:addPass( mock.SceneCameraPass( self.clearBuffer, self.clearColor ) )
end

function EditorCanvasCamera:isEditorCamera()
	return true
end

function EditorCanvasCamera:getDefaultOutputRenderTarget()
	context = gii.getCurrentRenderContext()
	local w, h = context.w, context.h
	self.canvasRenderTarget = mock.DeviceRenderTarget( 
		MOAIGfxDevice.getFrameBuffer(), 1, 1
	)
	self:setScreenSize( w or 100, h or 100 )
	return self.canvasRenderTarget
end

function EditorCanvasCamera:tryBindSceneLayer( layer )
	local name = layer.name
	if name == '_GII_EDITOR_LAYER' then
		layer:setViewport( self:getMoaiViewport() )
		layer:setCamera( self._camera )
	end
end

function EditorCanvasCamera:getScreenRect()
	return self.canvasRenderTarget:getAbsPixelRect()
end

function EditorCanvasCamera:getScreenScale()
	return self.canvasRenderTarget:getScale()
end

function EditorCanvasCamera:setScreenSize( w, h )
	self.canvasRenderTarget:setPixelSize( w, h )
	self.canvasRenderTarget:setFixedScale( w, h )
	self:updateZoom()
end

function EditorCanvasCamera:updateCanvas()
	if self.env then self.env.updateCanvas() end
end

function EditorCanvasCamera:hideCursor()
	if self.env then self.env.hideCursor() end
end

function EditorCanvasCamera:showCursor()
	if self.env then self.env.showCursor() end
end

function EditorCanvasCamera:setCursor( id )
	if self.env then self.env.setCursor( id ) end
end

function EditorCanvasCamera:onAttach( entity )
	entity.FLAG_EDITOR_OBJECT = true
	return mock.Camera.onAttach( self, entity)
end


--------------------------------------------------------------------
--EditorCanvasScene
--------------------------------------------------------------------
CLASS: EditorCanvasScene ( mock.Scene )
function EditorCanvasScene:__init()
	self.__editor_scene = true
end

function EditorCanvasScene:setEnv( env )
	self.env = env
end

function EditorCanvasScene:getEnv()
	return self.env
end

function EditorCanvasScene:initLayers()
	self.layerSource = mock.Layer( '_GII_EDITOR_LAYER' )
	local l = self.layerSource:makeMoaiLayer()
	self.layers = { l }
	self.layersByName = {
		['_GII_EDITOR_LAYER']	 = l
	}
	self.defaultLayer = l
end

function EditorCanvasScene:onLoad()
	self.cameraCom = EditorCanvasCamera( self.env )
	self.camera    = mock.SingleEntity( self.cameraCom )
	self.camera.FLAG_EDITOR_OBJECT = true
	self:addEntity( self.camera )
end


function EditorCanvasScene:getActionRoot()
	local ctx = gii.getCurrentRenderContext()
	return ctx.actionRoot
end

function EditorCanvasScene:updateCanvas()
	self.env.updateCanvas()
end

function EditorCanvasScene:getCanvasSize()
	local s = self.env.getCanvasSize()
	return s[0], s[1]
end

function EditorCanvasScene:hideCursor()
	return self.env.hideCursor()
end

function EditorCanvasScene:setCursor( id )
	return self.env.setCursor( id )
end

function EditorCanvasScene:showCursor()
	return self.env.showCursor()
end

function EditorCanvasScene:setCursorPos( x, y )
	return self.env.setCursorPos( x, y )
end

function EditorCanvasScene:startUpdateTimer( fps )
	return self.env.startUpdateTimer( fps )
end

function EditorCanvasScene:stopUpdateTimer()
	return self.env.stopUpdateTimer()
end

function EditorCanvasScene:getCameraZoom()
	return self.cameraCom:getZoom()
end

function EditorCanvasScene:setCameraZoom( zoom )
	self.cameraCom:setCameraZoom( zoom )
end

-- function EditorCanvasScene:threadMain( dt )
	
-- end

--------------------------------------------------------------------
function createEditorCanvasInputDevice( env )
	local env = env or getfenv( 2 )
	local inputDevice = mock.InputDevice( assert( env.contextName), true )

	function env.onMouseDown( btn, x, y )
		inputDevice:sendMouseEvent( 'down', x, y, btn )
	end

	function env.onMouseUp( btn, x, y )
		inputDevice:sendMouseEvent( 'up', x, y, btn )
	end

	function env.onMouseMove( x, y )
		inputDevice:sendMouseEvent( 'move', x, y, false )
	end

	function env.onMouseScroll( dx, dy, x, y )
		inputDevice:sendMouseEvent( 'scroll', dx, dy, false )
	end

	function env.onMouseEnter()
		inputDevice:sendMouseEvent( 'enter' )
	end

	function env.onMouseLeave()
		inputDevice:sendMouseEvent( 'leave' )
	end

	function env.onKeyDown( key )
		inputDevice:sendKeyEvent( key, true )
	end

	function env.onKeyUp( key )
		inputDevice:sendKeyEvent( key, false )
	end

	env._delegate:updateHooks()
	return inputDevice
end


---------------------------------------------------------------------
function createEditorCanvasScene()
	local env = getfenv( 2 )
	local scn = EditorCanvasScene()

	scn:setEnv( env )

	function env.onResize( w, h )
		scn.cameraCom:setScreenSize( w, h )
	end

	function env.onLoad()
	end

	local inputDevice = createEditorCanvasInputDevice( env )

	function env.EditorInputScript()
		return mock.InputScript{ device = inputDevice }
	end

	scn.inputDevice = inputDevice
	scn:init()
	scn.defaultLayer.name = '_GII_EDITOR_LAYER'
	scn:start()
	return scn
end 

