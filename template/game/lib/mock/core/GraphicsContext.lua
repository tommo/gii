module 'mock'

local _currentGraphicsContext = false

--------------------------------------------------------------------
CLASS: GraphicsContext ()
	:MODEL{}

function GraphicsContext:__init()
	self.deviceWidth = 100
	self.deviceHeight = 100
	self.viewportWidth = 100
	self.viewportHeight = 100
	self._current = false
end

function GraphicsContext:makeCurrent()
	if self._current then return end
	if _currentGraphicsContext then
		_currentGraphicsContext._current = false
	end
	self._current = true
	_currentGraphicsContext = self	
end

function GraphicsContext:isCurrent()
	return self._current
end

function GraphicsContext:setDeviceSize( w, h )
	self.deviceWidth  = w
	self.deviceHeight = h
end

function GraphicsContext:setViewportSize( w, h )
	self.viewportWidth  = w
	self.viewportHeight = h
end

--------------------------------------------------------------------
local _graphicsContextRegistry = {}
local _contextCounter = 0
function createGraphicsContext( id )
	_contextCounter = _contextCounter + 1
	if id then
		if _graphicsContextRegistry[ id ] then
			_error( 'graphics context duplicated!', id )
		end
	else --find a unique id
		id = 'graphics-context-'.._contextCounter
		assert not _graphicsContextRegistry[ id ]
	end
	local context = GraphicsContext()
	context.id = id	
	_graphicsContextRegistry[ id ] = context
	return context
end

function getGraphicsContext( id )
	return _graphicsContextRegistry[ id ]
end

function setCurrentGraphicsContext( id )
	local context = getGraphicsContext( id )
	if not context then
		_error( 'graphics context not found', id )
	end
	context:makeCurrent()
	return context
end