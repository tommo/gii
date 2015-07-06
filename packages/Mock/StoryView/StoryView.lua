scn = mock_edit.createEditorCanvasScene()

CLASS: StoryView ( mock_edit.EditorEntity )

function StoryView:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
end

view = scn:addEntity( StoryView() )
