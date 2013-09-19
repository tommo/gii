require 'mock_edit'

--------------------------------------------------------------------
--Asset Sync
--------------------------------------------------------------------
local function onAssetModified( node ) --node: <py>AssetNode	
	local nodepath = node:getPath()
	mock.releaseAsset( nodepath )
end

local function onAssetRegister( node )
	local nodePath = node:getPath()
	mock.registerAssetNode( nodePath, {
			deploy      = node.deployState == true,
			filePath    = node.filePath,
			type        = node.assetType,
			objectFiles = gii.dictToTable( node.objectFiles ),
		})
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

