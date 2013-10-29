
--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

--------------------------------------------------------------------
----PEX EDITOR
--------------------------------------------------------------------
CLASS: SimpleParticleEditor ( mock_edit.EditorEntity )
	:MODEL{}

function SimpleParticleEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	-- self.system
	self.config = mock.SimpleParticleSystemConfig()
end

function SimpleParticleEditor:open( path )
	local config, node = mock.loadAsset( path )
	if config then
		self.config = node.cached.simpleConfig
		self:updateParticle()
		return self.config
	end
end

function SimpleParticleEditor:save( path )
	if self.config then
		mock.serializeToFile( self.config, path )
	end
end

function SimpleParticleEditor:updateParticle()
	local prevEmitter = self.emitter
	if self.system then
		self:clearParticle()
	end
	local systemConfig = self.config:buildSystemConfig()
	self.system = self:attach( mock.ParticleSystem() )
	self.system:setConfigData( systemConfig )

	self.emitter = mock.ParticleEmitter()
	self.emitter.system = self.system
	self.emitter:setEmitterName( 'default' )
	self:attach( self.emitter )
	self.emitter:updateEmitter()
	if prevEmitter then
		self.emitter.emitter:setLoc( prevEmitter.emitter:getLoc() )
		self.emitter.emitter:setRot( prevEmitter.emitter:getRot() )
	end
	self.emitter:start()
	self.system:start()
	startUpdateTimer( 60 )
end

function SimpleParticleEditor:clearParticle()
	if self.emitter then
		self:detach( self.emitter )
		self.emitter = false
	end
	if self.system then
		self:detach( self.system )
		self.system = false
	end
	stopUpdateTimer()
end

function SimpleParticleEditor:onMouseDown( btn )
	if btn=='left' then 
		self.dragging = true
	end
end

function SimpleParticleEditor:onMouseUp( btn )
	if btn=='left' then 		
		self.dragging = false
	end
end

function SimpleParticleEditor:onMouseMove( x, y )
	if not self.dragging then return end
	x,y = self:wndToWorld( x, y )
	local em = self.emitter and self.emitter.emitter
	if em then
		em:setLoc( x, y )
	end
end

function SimpleParticleEditor:update()
end


--------------------------------------------------------------------
editor = scn:addEntity( SimpleParticleEditor() )
