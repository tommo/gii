scn = mock_edit.createEditorCanvasScene()

CLASS: EffectEditor ( mock_edit.EditorEntity )

function EffectEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )

	self.handleLayer = self:addSibling( mock_edit.CanvasHandleLayer{
			inputDevice = inputDevice
		} )
	self.handleLayer:setLoc( 0,0,1000 )
	self.handleLayer:setUpdateCallback(
		function()
			scheduleUpdate()
		end
	)

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

function EffectEditor:selectEditTarget( node )
	self:clearGizmos()
	if node then
		local onBuildGizmo = node.onBuildGizmo
		if onBuildGizmo then
			local giz = onBuildGizmo( node )
			if giz then self.handleLayer:addHandle( giz ) end
		end
	end
	updateCanvas()
end

function EffectEditor:clearGizmos()
	self.handleLayer:clearHandles()
end

function EffectEditor:addChildNode( parent, childType )
	if not parent then
		parent = self.effectRoot
	end
	
	local clas = mock.getEffectNodeType( childType )
	if not clas then
		_error( 'no effect class found:', childType )
	end
	local node = clas()
	parent:addChild( node )
	
	return node
end

function EffectEditor:requestAvailSubNodeTypes( parent )
	if not parent then --root
		parent = 'root'
	end
	local ename = parent.__effectName
	local t = mock.getAvailSubEffectNodeTypes( ename )
	-- table.foreach( t, print )
	return t
end

--------------------------------------------------------------------
editor = scn:addEntity( EffectEditor() )
