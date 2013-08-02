module 'mock'
local insert = table.insert
local remove = table.remove

--[[
	camera = 
		RenderTable 
]]

local function prioritySortFunc( a, b )	
	local pa = a.priority or 0
	local pb = b.priority or 0
	return pa < pb
end

local globalCameraList = {}

local function findMainCameraForScene( scene )
	for _, cam in ipairs( globalCameraList ) do
		if cam.scene == scene and cam.mainCamera then return cam end
	end
	return nil
end

local function updateRenderStack()
	local context = game.currentRenderContext
	local renderTableMap = {}
	local bufferTable    = {}
	local deviceBuffer   = MOAIGfxDevice.getFrameBuffer()
	local count = 0

	table.sort( globalCameraList, prioritySortFunc )

	for _, cam in ipairs( globalCameraList ) do
		if cam.context == context then
			local fb = cam:getFrameBuffer()
			local rt = renderTableMap[ fb ]
			if not rt then
				rt = {}
				renderTableMap[ fb ] = rt
				fb:setRenderTable( rt )
				if fb ~= deviceBuffer then --add framebuffer by camera order
					insert( bufferTable, fb )
				end
			end
			for i, layer in ipairs( cam.moaiLayers ) do
				count = count + 1
				insert( rt, layer )
			end
		end
	end

	MOAIRenderMgr.setBufferTable( bufferTable )
end

local function _onScreenResize( w, h )
	for _, cam in ipairs( globalCameraList ) do
		if not cam.fixedViewport then
			cam:updateViewport()
		end
	end
end

connectSignalFunc( 'gfx.resize', _onScreenResize )
-------------
CLASS: Camera ( Actor )
wrapWithMoaiTransformMethods( Camera, '_camera' )

function Camera:__init( option )
	option = option or {}
	local cam = MOAICamera.new()
	local ortho = option.ortho ~= false
	cam:setOrtho( ortho )
	local defaultNearPlane, defaultFarPlane = -100, 10000
	if ortho then
		defaultNearPlane, defaultFarPlane = -100, 10000
	end
	cam:setNearPlane( option.nearPlane or defaultNearPlane )
	cam:setFarPlane(  option.farPlane  or defaultFarPlane )

	--TODO: add support for fixed viewport
	self.fixedViewport = option.fixedViewport or false
	self.viewportSize  = {0,0,1,1}
	self._camera    = cam
	self.zoom       = 1
	self.moaiLayers = {}
	self.viewport   = MOAIViewport.new()
	self.priority   = option.priority or 0
	self.mainCamera = false

	self.dummyLayer = MOAILayer.new()  --just for projection transform
	self.dummyLayer:setViewport( self.viewport )
	self.dummyLayer:setCamera( self._camera )
	
	self.includedLayers = option.included or 'all'
	self.excludedLayers = option.excluded or ( option.included and 'all' or false )
	self:setFrameBuffer()

	self.context = 'game'
end

function Camera:onAttach( entity )
	self.scene = entity.scene
	table.insert( globalCameraList, self )
	self:setViewport()
	self:updateLayers()
	entity:_attachTransform( self._camera )
	--use as main camera if no camera applied yet for current scene
	if not findMainCameraForScene( self.scene ) then 
		self:setMainCamera()
	end
end

function Camera:onDetach( entity )
	--remove from global camera list
	for i, cam in ipairs( globalCameraList ) do
		if cam == self then remove( globalCameraList, i ) break end
	end
	updateRenderStack()
end

--will affect Entity:wndToWorld
function Camera:setMainCamera()
	if self.mainCamera then return end
	local scene = self.scene
	if not scene then return end
	for _, cam in ipairs( globalCameraList ) do
		if cam.mainCamera and cam ~= self and cam.scene == self.scene then
			cam.mainCamera = false
		end 
	end
	scene:setDefaultViewport( self.viewport )
	scene:setDefaultCamera( self._camera )
end

function Camera:isMainCamera()
	return self.mainCamera
end

function Camera:getMainCamera()
	if not self.scene then return nil end
	return findMainCameraForScene( self.scene )
end

function Camera:isLayerIncluded( name )
	for i, layer in ipairs( self.moaiLayers ) do
		if layer.name == name then return true end
	end
	return false
end 

--internal use
function Camera:_isLayerIncluded( name )
	if self.includedLayers == 'all' then return nil end
	for i, n in ipairs( self.includedLayers ) do
		if n == name then return true end
	end
	return false
end

--internal use
function Camera:_isLayerExcluded( name )
	if self.excludedLayers == 'all' then return true end
	if not self.excludedLayers then return false end
	for i, n in ipairs( self.excludedLayers ) do
		if n == name then return true end
	end
	return false
end

function Camera:updateLayers()
	local scene  = self.scene
	local layers = {} 
	self.moaiLayers = layers
	--make a copy of layers from current scene
	for name, sceneLayer in pairs( scene.layers ) do
		local layer = MOAILayer.new()
		if self:_isLayerIncluded( name ) or (not self:_isLayerExcluded( name )) then
			layer.name     = name
			layer.priority = sceneLayer.priority or 0
			layer:setPartition( sceneLayer:getPartition() )
			layer:setViewport( self.viewport )
			layer:setCamera( self._camera )
			
			--TODO: should be moved to debug facility
			layer:showDebugLines( true )
			local world = game:getBox2DWorld()
			if world then layer:setBox2DWorld( world ) end

			if sceneLayer.sortMode then
				layer:setSortMode( sceneLayer.sortMode )
			end
			inheritVisible( layer, sceneLayer )
			insert( layers, layer )
			layer._mock_camera = self
		end
	end
	
	table.sort( layers, prioritySortFunc )
	updateRenderStack()

end

function Camera:getRenderLayer( name )
	for i, layer in ipairs( self.moaiLayers ) do
		if layer.name == name then return layer end
	end
	return nil
end

function Camera:wndToWorld( x, y )
	return self.dummyLayer:wndToWorld( x, y )
end

function Camera:worldToWnd( x, y, z )
	return self.dummyLayer:worldToWnd( x, y, z )
end

function Camera:getGameViewRect()
	local rect
	local fb = self.frameBuffer
	if fb == MOAIGfxDevice.getFrameBuffer() then		
		return unpack( game.gfx.viewportRect )
	else
		local vw,vh = fb:getSize()
		return 0, 0, vw, vh
	end
end

function Camera:getGameViewScale()
	local gfx = game.gfx
	return gfx.w, gfx.h
end

function Camera:updateViewport()
	local zoom = self.zoom or 1
	if zoom <= 0 then zoom = 0.00001 end
	local	x0, y0, x1, y1 = unpack( self.viewportSize ) -- ratio ( 0 - 1 )
	local w, h = x1-x0, y1-y0	
	local gw, gh = self:getGameViewScale() --scale

	local vx0, vy0, vx1, vy1 = self:getGameViewRect()
	local vw, vh = vx1-vx0, vy1-vy0
	do
		local sclW, sclH = gw * w / zoom , gh * h / zoom
		local x0, y0, x1, y1 = vx0+vw*x0, vy0+vh*y0, vx0+vw*x1, vy0+vh*y1
		self.viewport:setScale( sclW, sclH )
		self.viewport:setSize( x0, y0, x1, y1 )
		self.viewportWorldSize = { sclW, sclH }
		self.viewportWndRect   = { x0, y0, x1, y1	}
	end
end

function Camera:getViewportWorldSize()
	return unpack( self.viewportWorldSize )
end

--TODO: getViewportWorldQuad?

function Camera:getViewportWndRect()
	return unpack( self.viewportWndRect )
end

----
--Layer control
function Camera:bindLayers( included )
	for i, layerName in ipairs( included ) do
		local layer = self.scene:getLayer( layerName )
		if not layer then error('no layer named:'..layerName,2) end
		layer:setCamera( self._camera )
	end
end

function Camera:bindAllLayerExcept( excluded )
	for k, layer in pairs( self.scene.layers ) do
		local match = false
		for i, n in ipairs(excluded) do
			if layer.name == n then match = true break end
		end
		if not match then layer:setCamera( self._camera ) end
	end
end



function Camera:hideLayer( layerName )
	return self:showLayer( layerName, false )
end

function Camera:hideAllLayers( layerName )
	return self:showAllLayers( layerName, false )
end

function Camera:showAllLayers( layerName, shown )
	shown = shown ~= false
	for i, layer in ipairs( self.moaiLayers ) do
		layer:setVisible( shown )
	end
end

function Camera:showLayer( layerName, shown )
	shown = shown ~= false
	for i, layer in ipairs( self.moaiLayers ) do
		if layer.name == layerName then
			layer:setVisible( shown )
		end
	end
end



-- --fixed or auto-resize

-- input value: ratio of screen
function Camera:setViewport( x0, y0, x1, y1 )
	-- local fb = self:getFrameBuffer()
	--TODO: use framebuffer size
	if not x0 then --full screen viewport
		x0, y0, x1, y1 =0, 0, 1, 1
	end
	self.viewportSize = {x0,y0,x1,y1}
	self:updateViewport()
end

function Camera:setZoom( zoom )
	self.zoom = zoom or 1
	self:updateViewport()
end

function Camera:setFrameBuffer( fb )
	self.frameBuffer = fb or MOAIGfxDevice.getFrameBuffer()
	if self.scene then
		self:updateViewport()
		self:updateLayers()
	end
	return self.frameBuffer
end

function Camera:getFrameBuffer()
	return self.frameBuffer
end

_wrapMethods(Camera, '_camera', {
		'setOrtho',
		'setFarPlane',
		'setNearPlane',
	})

wrapWithMoaiTransformMethods( Camera, '_camera' )