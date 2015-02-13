module 'mock'

CLASS: StereoCamera ( Camera )
	:MODEL{
		Field '----';
		Field 'eyeDistance';
}

registerComponent( 'StereoCamera', StereoCamera )

function StereoCamera:_initDefault()
	self.eyeDistance = 10
	self.leftEyeViewport  = MOAIViewport.new()
	self.leftEyeCamera    = MOAICamera.new()
	self.rightEyeViewport = MOAIViewport.new()
	self.rightEyeCamera   = MOAICamera.new()
	inheritTransform( self.leftEyeCamera, self._camera )
	inheritTransform( self.rightEyeCamera, self._camera )
	
	self.leftEyeCamera:setLoc( -self.eyeDistance/2 )
	self.rightEyeCamera:setLoc( self.eyeDistance/2 )

	-- self.leftEyeCamera:setAttrLink( MOAICamera.ATTR_FOV, self._camera )
	-- self.rightEyeCamera:setAttrLink( MOAICamera.ATTR_FOV, self._camera )
	return Camera._initDefault( self )
end

function StereoCamera:loadPasses()
	self.passes = {}
	self:addPass( StereoSceneCameraPass( self.clearBuffer, self.clearColor, self.eyeDistance ) )
end

function StereoCamera:updateViewport()
	Camera.updateViewport( self )
	local vx0, vy0, vx1, vy1 = unpack( self.viewportWndRect )
	local vw, vh = vx1 - vx0, vy1 - vy0
	self.leftEyeViewport:setSize( vx0, vy0, vx0 + vw/2, vy1 )
	self.rightEyeViewport:setSize( vx0 + vw/2, vy0, vx1, vy1 )
end

function StereoCamera:updateZoom()
	Camera.updateZoom( self )
	if self.perspective then
		local zoom = self:getZoom()
		if zoom <= 0 then zoom = 0.00001 end
		local dx,dy,dx1,dy1 = self:getScreenRect()
		local dw = dx1-dx
		local dh = dy1-dy
		self.leftEyeViewport:setScale( dw/zoom/2, dh/zoom )
		self.rightEyeViewport:setScale( dw/zoom/2, dh/zoom )
	else
		local w,h = unpack( self.viewportScale )
		self.leftEyeViewport:setScale( w/2, h )
		self.rightEyeViewport:setScale( w/2, h )
	end
	
end

function StereoCamera:setNearPlane( near )
	local cam = self._camera
	self.nearPlane = near
	cam:setNearPlane( near )
	self.leftEyeCamera:setNearPlane( near )
	self.rightEyeCamera:setNearPlane( near )
end

function StereoCamera:setFarPlane( far )
	local cam = self._camera
	self.farPlane = far
	cam:setFarPlane( far )
	self.leftEyeCamera:setFarPlane( near )
	self.rightEyeCamera:setFarPlane( near )
end

function StereoCamera:setPerspective( p )
	self.leftEyeCamera:setOrtho( not p )
	self.rightEyeCamera:setOrtho( not p )
	return Camera.setPerspective( self, p )	
end

function StereoCamera:setFOV( fov )
	Camera.setFOV( self, fov )
	self.leftEyeCamera:setFieldOfView( fov )
	self.rightEyeCamera:setFieldOfView( fov )
end


--------------------------------------------------------------------

CLASS: StereoSceneCameraPass ( CameraPass )
 	:MODEL{} 

function StereoSceneCameraPass:__init( clear, clearColor, eyeDistance )
	self.clearBuffer = clear ~= false
	self.clearColor  = clearColor or false
	self.eyeDistance = eyeDistance or 10
end

function StereoSceneCameraPass:onBuild()
	if not self.clearBuffer then
		self:pushFrameBuffer( false, { clearColor = false } )
	else
		self:pushFrameBuffer( false, { clearColor = self.clearColor } )
	end
	--left eye
	local camera = self.camera
	self:pushSceneRenderPass( nil, {
			viewport = camera.leftEyeViewport,
			transform = camera.leftEyeCamera 
		})
	self:pushSceneRenderPass( nil, {
			viewport = camera.rightEyeViewport,
			transform = camera.rightEyeCamera 
		})
end
