scn = mock_edit.createEditorCanvasScene()

CLASS: EffectEditor ( mock_edit.EditorEntity )

function EffectEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )
	self.previewing = false
	self.previewEmitter = false
end

function EffectEditor:open( path )
	local config = mock.loadAsset( path )
	self.effectConfig = config	
	self.effectRoot   = config:getRootNode()
	return self.effectConfig
end

function EffectEditor:save( path )
	mock.serializeToFile( self.effectConfig, path )
end

function EffectEditor:close()
	-- self:stopPreview()
end

function EffectEditor:markDirty( node )
	local p = node
	while p do
		p._built = false
		p = p.parent
	end
end

function EffectEditor:refreshPreview()
	if not self.previewing then return end
	local loc = { self.previewEmitterEnt:getLoc() }
	self:stopPreview()
	self:startPreview()
	self.previewEmitterEnt:setLoc( unpack( loc ) )
end

function EffectEditor:startPreview()
	if self.previewing then return end
	local ent = mock.Entity()	
	emitter = ent:attach( mock.EffectEmitter() )
	self.previewEmitter    = emitter
	self.previewEmitterEnt = ent
	emitter:setEffect( self.effectConfig )
	self:addChild( ent )
	emitter:start()
	self.previewing = true
	startUpdateTimer( 60 )
end

function EffectEditor:stopPreview()
	if not self.previewing then return end
	self.previewEmitterEnt:destroy()
	self.previewEmitter = false
	self.previewEmitterEnt = false
	self.previewing = false
	updateCanvas()
	stopUpdateTimer()
end


function EffectEditor:onMouseDown( btn, x, y )
	if btn == 'left' and  self.previewEmitterEnt then
		self.previewEmitterEnt:setLoc( self:wndToWorld( x, y ) )		
	end
end

function EffectEditor:onMouseMove( x, y )
	if self.previewEmitterEnt then
		if scn.inputDevice:isMouseDown('left') then
			self.previewEmitterEnt:setLoc( self:wndToWorld( x, y ) )
		end
	end
end

function EffectEditor:removeNode( node )
	node.parent:removeChild( node )
end

function EffectEditor:addMove()
	local mv = mock.EffectMove()
	self.effectRoot:addChild( mv )	
	return mv
end

function EffectEditor:addSystem()
	local sys = mock.EffectNodeParticleSystem()
	self.effectRoot:addChild( sys )
	sys:addChild( mock.EffectNodeParticleState() )
	sys:addChild( mock.EffectNodeParticleTimedEmitter() )
	return sys
end

function _cloneEffectNode( n )
	local n1 = mock.clone( n )
	n1.children = {}
	n1.parent = false
	for i, child in ipairs( n.children ) do
		n1:addChild( _cloneEffectNode( child ) )
	end
	return n1
end

function EffectEditor:cloneNode( node )
	local n1 = _cloneEffectNode( node )
	node.parent:addChild( n1 )
	return n1
end

local nameToNodeClass = {
	[ 'state'            ] = mock.EffectNodeParticleState ;
	[ 'emitter-timed'    ] = mock.EffectNodeParticleTimedEmitter ;
	[ 'emitter-distance' ] = mock.EffectNodeParticleDistanceEmitter ;
	[ 'force-attractor'  ] = mock.EffectNodeForceAttractor ;
	[ 'force-basin'      ] = mock.EffectNodeForceBasin ;
	[ 'force-linear'     ] = mock.EffectNodeForceLinear ;
	[ 'force-radial'     ] = mock.EffectNodeForceRadial ;
}
function EffectEditor:addChildNode( parent, childType )
	local clas = nameToNodeClass[ childType ]
	local node = clas()
	if not parent:isInstance( mock.EffectNodeParticleSystem ) then
		parent = parent.parent
		assert( parent:isInstance( mock.EffectNodeParticleSystem ) )
	end
	parent:addChild( node )
	return node
end

--------------------------------------------------------------------
editor = scn:addEntity( EffectEditor() )
