scn = mock_edit.createEditorCanvasScene()

CLASS: EffectEditor ( mock_edit.EditorEntity )

function EffectEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )
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
end

function EffectEditor:removeNode( node )
	node.parent:removeChild( node )
end

function EffectEditor:addSystem()
	local sys = mock.EffectNodeParticleSystem()
	print( self.effectRoot:getClassName() )
	self.effectRoot:addChild( sys )
	return sys
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
function EffectEditor:addChild( parent, childType )
	local clas = nameToNodeClass[ childType ]
	local node = clas()
	if not parent:isInstance( mock.EffectNodeParticleSystem ) then
		parent = parent.parent
		assert( parent:isInstance( mock.EffectNodeParticleSystem ) )
	end
	parent:addChild( node )
	return node
end

function EffectEditor:addState( parent )
	assert( parent:isInstance( mock.EffectNodeParticleSystem ) )
	local state = mock.EffectNodeParticleState()
	parent:addChild( state )
	return state
end

--------------------------------------------------------------------
editor = scn:addEntity( EffectEditor() )
