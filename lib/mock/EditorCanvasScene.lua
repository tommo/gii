--------------------------------------------------------------------
CLASS: EditorEntity ( mock.Entity )
function EditorEntity:__init()
	self.__editor_entity = true
end

--------------------------------------------------------------------
function createEditorCanvasInputDevice( env )
	local env = env or getfenv( 2 )
	local inputDevice = mock.InputDevice( env.contextName )

	function env.onMouseDown( btn, x, y )
		inputDevice:sendMouseEvent( 'down', x, y, btn )
	end

	function env.onMouseUp( btn, x, y )
		inputDevice:sendMouseEvent( 'up', x, y, btn )
	end

	function env.onMouseMove( x, y )
		inputDevice:sendMouseEvent( 'move', x, y, false )
	end

	function env.onScroll( dx, dy, x, y )
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

	return inputDevice
end

--------------------------------------------------------------------
--EditorCanvasCamera
--------------------------------------------------------------------
CLASS: EditorCanvasCamera ( mock.Camera )
function EditorCanvasCamera:__init( env )	
	self.__editor_entity = true
	self.context = gii.getCurrentRenderContextKey()
	self.screenWidth   = 100
	self.screenHeight	 = 100

	self.env = env

end

function EditorCanvasCamera:getScreenSize()
	return self.screenWidth, self.screenHeight
end

function EditorCanvasCamera:setScreenSize( w, h )
	self.screenWidth, self.screenHeight = w, h
	if self.scene then
		self:updateViewport()
	end
end

function EditorCanvasCamera:updateCanvas()
	if self.env then self.env.updateCanvas() end
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

function EditorCanvasScene:onEnter()
	self.cameraCom = EditorCanvasCamera( self.env )
	self.camera    = mock.SingleEntity( self.cameraCom )
	self.camera.__editor_entity = true
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

---------------------------------------------------------------------
function createMockEditorScene()
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
	scn:enter()
	return scn
end 

--------------------------------------------------------------------
