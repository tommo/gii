--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

---------------------------------------------------------------------
CLASS: ParticlePreview ( EditorEntity )

function ParticlePreview:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )

	self.testSystem  = false
	self.testEmitter = false 

	self.editingConfig  = false
	self.editingEmitter = false
	self.editingState   = false

	-- startUpdateTimer( 60 )

end

function ParticlePreview:onMouseDown( btn, x, y )
	if btn == 'left' and  self.testEmitter then
		self.testEmitter:setLoc( self:wndToWorld( x, y ) )		
	end
end

function ParticlePreview:onMouseMove( x, y )
	if self.testEmitter then
		if scn.inputDevice:isMouseDown('left') then
			self.testEmitter:setLoc( self:wndToWorld( x, y ) )
		end
	end
end

function ParticlePreview:rebuildSystem()
	if self.testSystem then
		self:detach( self.testSystem )		
	end
	self.testSystem =  self:attach( mock.ParticleSystem( self.editingConfig ) )
	self.testSystem:start()
	self:updateEmitter( true )	
end

function ParticlePreview:updateState( )
	local state = self.editingState
	self:rebuildSystem()
end

function ParticlePreview:updateEmitter( rebuild )
	local item = self.editingEmitter
	if not item then return end
	if rebuild then
		if self.testEmitter then self.testEmitter:stop() end
		self.testEmitter = self.testSystem:addEmitter( item.name )		
	else
		item:updateEmitter( self.testEmitter )
	end
end

function ParticlePreview:activateEmitter( item )
	if not self.testSystem then return end
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

function ParticlePreview:update( obj, field )
	if isInstanceOf( obj, mock.ParticleEmitterConfig ) then
		self:updateEmitter( field=='type' )
	elseif isInstanceOf( obj, mock.ParticleStateConfig ) then
		self:updateState()
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
	self.editingConfig = mock.ParticleSystemConfig()
	self.editingConfig.allowPool = false
	self.editingConfig.deck = mock.loadAsset( 'decks/icons.deck2d/simley_coin' )

	self.editingConfig:addEmitterConfig().name = 'timed'
	local config2 = self.editingConfig:addEmitterConfig()
	config2.name = 'distance'
	config2.type = 'distance'

	
	local state = self.editingConfig:addStateConfig()
	state.renderScript = 'sprite()'

	self:rebuildSystem()
	
	return self.editingConfig
end

preview = scn:addEntity( ParticlePreview() )

