--------------------------------------------------------------------
scn = mock_edit.createEditorCanvasScene()
--------------------------------------------------------------------

CLASS: TileMapEditor( mock_edit.EditorEntity )

function TileMapEditor:onLoad()
	self:addSibling( mock_edit.CanvasGrid() )
	self:addSibling( mock_edit.CanvasNavigate() )
end

function TileMapEditor:findTargetMap()
	local selection = gii.getSelection( 'scene' )
	--find a parent animator
	if #selection ~= 1 then --only single selection allowed( for now )
		return nil
	end

	local ent = selection[1]
	if not isInstance( ent, mock.Entity ) then
		return nil
	end

	while ent do
		local map = ent:getComponent( mock.TileMap )
		if map then return map end
		ent = ent.parent
	end

	return nil
end
editor = scn:addEntity( TileMapEditor() )
