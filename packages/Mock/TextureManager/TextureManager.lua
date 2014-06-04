local function getTextureUV( tex )
	local ttype = tex.type
	local t, uv
	if ttype == 'sub_texture' then
		t = tex.atlas
		uv = tex.uv
	else
		t = tex
		uv = { 0,1,1,0 }
	end
	return t, uv
end

--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

CLASS: TextureManagerPreview( mock_edit.EditorEntity )

function TextureManagerPreview:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )
	self.previewProps = {}
end

function TextureManagerPreview:setLibrary( lib )
	self.lib = lib
end

function TextureManagerPreview:getLibrary()
	return self.lib
end

function TextureManagerPreview:addGroup()
	return self.lib:addGroup()
end

function TextureManagerPreview:setGroup()
end

function TextureManagerPreview:removeGroup( group )
	self.lib:removeGroup( group, true )
end

function TextureManagerPreview:moveTextureToDefaultGroup( texture )
	return self:regroup( texture, self.lib.defaultGroup )
end

function TextureManagerPreview:regroup( texture, group )
	group:addTexture( texture )
end

function TextureManagerPreview:changeSelection( selection )
	selection = gii.listToTable( selection )
	self:clearPreview()
	for i, node in ipairs( selection ) do
		self:addPreview( node )
	end
	self:layoutPreview()
	updateCanvas()
end

function TextureManagerPreview:addPreview( node )
	local prop = MOAIProp.new()
	local deck = MOAIGfxQuad2D.new()
	prop:setDeck( deck )

	if node:getClassName() == 'TextureGroup' then
		--draw atlas
		if node:isAtlas() then
			node:loadAtlas()
			local t = node.atlasTextures[ 1 ]
			deck:setTexture( t )
			deck:setRect( 0,0, t:getSize() )
			deck:setUVRect( 0,1,1,0 )
		end
	else
		--draw texture
		local path = node.path
		mock.loadAsset( path )
		local tex = mock.loadAsset( path )
		local t, uv = tex:getMoaiTextureUV()
		deck:setTexture( t )
		deck:setRect( 0,0, tex:getSize() )
		deck:setUVRect( unpack( uv ) )
	end
	self:_insertPropToLayer( prop )
	self.previewProps[ prop ] = true
end

function TextureManagerPreview:layoutPreview()
	--TODO
end

function TextureManagerPreview:clearPreview()
	for n in pairs( self.previewProps ) do
		self:_detachProp( n )
	end
	self.previewProps = {}
end

preview = scn:addEntity( TextureManagerPreview() )


