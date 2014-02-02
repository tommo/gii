module 'mock_edit'

local function onTextureRebuilt( node )
	if node:getType() ~= 'texture' then return end

	local path = node:getNodePath()
	local mockNode = mock.getAssetNode( path )
	if mockNode then mock.updateAssetNode( mockNode, _pyAssetNodeToData( node ) ) end

	for item in pairs( mock.getLoadedDecks() ) do
		if item:getTexture() == path then
			item:setTexture( path, false )
		end
	end
	gii.emitPythonSignal( 'scene.update' )
end

gii.connectPythonSignal( 'texture.rebuild',   onTextureRebuilt )

