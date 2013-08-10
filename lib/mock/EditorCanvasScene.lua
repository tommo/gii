--------------------------------------------------------------------
CLASS: EditorCanvasCamera ( mock.Camera )
function EditorCanvasCamera:__init()
	self.context = gii.getCurrentRenderContextKey()
	self.screenWidth   = 100
	self.screenHeight	 = 100
end

function EditorCanvasCamera:getScreenSize()
	return self.screenWidth, self.screenHeight
end

function EditorCanvasCamera:setScreenSize( w, h )
	self.screenWidth, self.screenHeight = w, h
	self:updateViewport()
end

--
CLASS: EditorCanvasScene ( mock.Scene )
function EditorCanvasScene:onEnter()
	self.cameraCom = EditorCanvasCamera()
	self.camera    = self:addEntity( mock.SingleEntity( self.cameraCom ) )
end

function EditorCanvasScene:getActionRoot()
	local ctx = gii.getCurrentRenderContext()
	return ctx.actionRoot
end

---
function createMockEditorScene()
	local env = getfenv( 2 )
	local scn = EditorCanvasScene()

	function env.onResize( w, h )
		scn.cameraCom:setScreenSize( w, h )
	end

	function env.onLoad()
	end

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

	function env.EditorInputScript()
		return mock.InputScript{ device = inputDevice }
	end

	scn.inputDevice = inputDevice
	scn:enter()
	return scn
end 

