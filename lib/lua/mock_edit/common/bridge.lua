module 'mock_edit'

--------------------------------------------------------------------
--Asset Sync
--------------------------------------------------------------------
function _pyAssetNodeToData( node )
	return {
			deploy      = node.deployState == true,
			filePath    = node.filePath,
			type        = node.assetType,
			objectFiles = gii.dictToTable( node.objectFiles ),
			properties  = gii.dictToTable( node.properties ),
			dependency  = gii.dictToTable( node.dependency ),
			fileTime    = node.fileTime
		}
end

local function onAssetModified( node ) --node: <py>AssetNode	
	local nodepath = node:getPath()
	mock.releaseAsset( nodepath )
	local mockNode = mock.getAssetNode( nodepath )
	if mockNode then
		local data = _pyAssetNodeToData( node )
		mock.updateAssetNode( mockNode, data )
	end
	emitSignal( 'asset.modified', nodepath )
end

local function onAssetRegister( node )
	local nodePath = node:getPath()
	mock.registerAssetNode( nodePath, _pyAssetNodeToData( node ) )
end

local function onAssetUnregister( node )
	local nodePath = node:getPath()
	mock.unregisterAssetNode( nodePath )
end

gii.connectPythonSignal( 'asset.modified',   onAssetModified )
gii.connectPythonSignal( 'asset.register',   onAssetRegister )
gii.connectPythonSignal( 'asset.unregister', onAssetUnregister )

--------------------------------------------------------------------
local function onContextChange( ctx, oldCtx )
	mock.game:setCurrentRenderContext( ctx )
end

gii.addContextChangeListeners( onContextChange )

