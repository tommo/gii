module 'mock'

CLASS: TexturePlane ( RenderComponent )
	:MODEL{
		Field 'texture' :asset('texture;framebuffer') :getset( 'Texture' );
		Field 'size'    :type('vec2') :getset('Size');
		'----';
		Field 'resetSize' :action( 'resetSize' );
	}

registerComponent( 'TexturePlane', TexturePlane )
mock.registerEntityWithComponent( 'TexturePlane', TexturePlane )

function TexturePlane:__init()
	self.texture = false
	self.w = 100
	self.h = 100
	self.deck = Quad2D()
	self.deck:setSize( 100, 100 )
	self.prop = MOAIProp.new()
	self.prop:setDeck( self.deck:getMoaiDeck() )
end

function TexturePlane:onAttach( ent )
	ent:_attachProp( self.prop )
end

function TexturePlane:onDetach( ent )
	ent:_detachProp( self.prop )
end

function TexturePlane:setLayer( layer )
	layer:insertProp( self.prop )
end


function TexturePlane:getTexture()
	return self.texture
end

function TexturePlane:setTexture( t )
	self.texture = t
	self.deck:setTexture( t, false ) --dont resize
	self.deck:update()
	self.prop:forceUpdate()
end

function TexturePlane:getSize()
	return self.w, self.h
end

function TexturePlane:setSize( w, h )
	self.w = w
	self.h = h
	self.deck:setSize( w, h )
	self.deck:update()
	self.prop:forceUpdate()
end

function TexturePlane:setBlend( b )
	self.blend = b
	setPropBlend( self.prop, b )
end

function TexturePlane:setScissorRect( s )
	self.prop:setScissorRect( s )
end

function TexturePlane:resetSize()
	if self.texture then
		local tex = loadAsset( self.texture )
		self:setSize( tex:getSize() )
	end
end


--------------------------------------------------------------------
local defaultShader = MOAIShaderMgr.getShader( MOAIShaderMgr.DECK2D_SHADER )

function TexturePlane:setShader( shaderPath )
	self.shader = shaderPath	
	if shaderPath then
		local shader = mock.loadAsset( shaderPath )
		if shader then
			local moaiShader = shader:getMoaiShader()
			return self.prop:setShader( moaiShader )
		end
	end
	self.prop:setShader( defaultShader )
end

