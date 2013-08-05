CLASS: TexturePreview ( EditorEntity )

function TexturePreview:onLoad()
	self.prop = self:attach ( Prop() )
	self:attach( InputScript() )
end

function TexturePreview:openAsset( node )
	local tex = loadAsset( node:getPath() )
	if not tex then return end
	
	local deck = MOAIGfxQuad2D.new()
	local w, h = tex:getSize()

	deck:setRect( -w/2, -h/2, w/2, h/2 )
	if tex.type == 'sub_texture' then
		deck:setTexture( tex.atlas )
		deck:setUVRect( unpack(tex.uv) )
	else
		deck:setTexture( tex )
		deck:setUVRect(0,1,1,0)
	end
	self.prop:setDeck( deck )

	_owner:updateCanvas()	
end




function onLoad()
end