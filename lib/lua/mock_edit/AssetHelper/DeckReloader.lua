module 'mock_edit'

local function onTextureRebuilt( node )
	if node:getType() ~= 'texture' then return end
	local path = node:getNodePath()
	local mockNode = mock.getAssetNode( path )
	if mockNode then mock.updateAssetNode( mockNode, _pyAssetNodeToData( node ) ) end

	for deckPath, node in pairs( mock.getAssetLibrary() ) do
		if node.type:startWith( 'deck2d.' ) then
			local item = node.cached.deckItem
			if item then
				if item:getTexture() == path then
					print( 'update deck!!', deckPath )
					item:setTexture( path )
				end
			end
		end
	end
	gii.emitPythonSignal( 'scene.update' )
end

-- connectSignalFunc( 'asset.modified', onAssetModified )
gii.connectPythonSignal( 'texture.rebuild',   onTextureRebuilt )

