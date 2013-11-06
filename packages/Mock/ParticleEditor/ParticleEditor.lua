--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

---------------------------------------------------------------------
CLASS: ParticlePreview ( mock_edit.EditorEntity )

function ParticlePreview:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )

	self.previewing = false 
	self.previewSystem  = false
	self.previewEmitter = false 

	self.editingConfig  = false
	self.editingEmitter = false
	self.editingState   = false

end

function ParticlePreview:onMouseDown( btn, x, y )
	if btn == 'left' and  self.previewEmitter then
		self.previewEmitter:setLoc( self:wndToWorld( x, y ) )		
	end
end

function ParticlePreview:onMouseMove( x, y )
	if self.previewEmitter then
		if scn.inputDevice:isMouseDown('left') then
			self.previewEmitter:setLoc( self:wndToWorld( x, y ) )
		end
	end
end

function ParticlePreview:rebuildSystem()
	if not self.previewing then return end
	if self.previewSystem then
		self:detach( self.previewSystem )		
	end
	self.previewSystem =  self:attach( mock.ParticleSystem() )
	self.previewSystem:setConfigData( self.editingConfig )
	self.previewSystem:start()
	self:updateEmitter( true )	
end

function ParticlePreview:updateState( )
	local state = self.editingState
	self:rebuildSystem()
end

function ParticlePreview:updateEmitter( rebuild )
	if not self.previewing then return end
	local item = self.editingEmitter
	if not item then return end
	if rebuild then
		if self.previewEmitter then self.previewEmitter:stop() end
		self.previewEmitter = self.previewSystem:addEmitter( item.name )		
	else
		item:updateEmitter( self.previewEmitter )
	end
end

function ParticlePreview:activateEmitter( item )
	if self.editingEmitter == item then return end
	self.editingEmitter = item
	self:updateEmitter( true )	
end

function ParticlePreview:activateState( state )
	if state == self.editingState then return end
	self.editingState = state
	gii.app:getModule('particle_editor'):changeState( state )
end

function ParticlePreview:updateScript( initScript, renderScript )
	if not self.editingState then return end
	self.editingState.initScript   = initScript
	self.editingState.renderScript = renderScript
	self:updateState()	
end

function ParticlePreview:update( obj, field, value )
	if isInstanceOf( obj, mock.ParticleEmitterConfig ) then
		self:updateEmitter( field=='type' )
	elseif isInstanceOf( obj, mock.ParticleStateConfig ) then
		self:updateState()
	else --system		
		if field == 'blend' and self.previewSystem then
			return setPropBlend( self.previewSystem._system, value )
		end
		return self:rebuildSystem()
	end
end

function ParticlePreview:changeSelection( node )
	if isInstanceOf( node, mock.ParticleEmitterConfig ) then
		self:activateEmitter( node )
	elseif isInstanceOf( node, mock.ParticleStateConfig ) then
		self:activateState( node )
	end

end

function ParticlePreview:open( path )

	self.editingConfig = mock.loadAsset( path )
	self.editingConfig.allowPool = false
	
	-- self.editingConfig:addEmitterConfig().name = 'timed'
	-- self.editingConfig.deck = mock.findAsset( 'particle.deck2d/111' )
	-- local config2 = self.editingConfig:addEmitterConfig()
	-- config2.name = 'distance'
	-- config2.type = 'distance'
	
	-- local state = self.editingConfig:addStateConfig()
	-- state.renderScript = 'sprite()'

	self:rebuildSystem()
	
	return self.editingConfig
end

function ParticlePreview:save( filePath )
	mock.serializeToFile( self.editingConfig, filePath )
end

function ParticlePreview:startPreview()
	self.previewing = true
	self:rebuildSystem()
	startUpdateTimer( 60 )
end

function ParticlePreview:stopPreview()
	self.previewing = false
	self.previewSystem:stop()
	updateCanvas()
	stopUpdateTimer()
end

function ParticlePreview:addEmitter()
	local emitterConfig = self.editingConfig:addEmitterConfig()
	emitterConfig.name = 'emitter'
	return emitterConfig
end

function ParticlePreview:addState()
	local stateConfig = self.editingConfig:addStateConfig()
	stateConfig.name = 'state'
	return stateConfig
end

preview = scn:addEntity( ParticlePreview() )

