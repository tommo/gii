scn = mock_edit.createEditorCanvasScene()

CLASS: EffectEditor ( mock_edit.EditorEntity )

function EffectEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
	self:attach( mock.InputScript{ device = scn.inputDevice } )
	self:attach( mock.DrawScript{ priority = 1000 } )
end

function EffectEditor:open()
end

function EffectEditor:save()
end

function EffectEditor:close()
end


--------------------------------------------------------------------
editor = scn:addEntity( EffectEditor() )
