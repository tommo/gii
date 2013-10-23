--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

CLASS: TextureManagerPreview( mock_edit.EditorEntity )

function TextureManagerPreview:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )
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
	self.lib:removeGroup( group )
end

function TextureManagerPreview:regroup( texture, group )
	group:addTexture( texture )
end


preview = scn:addEntity( TextureManagerPreview() )
