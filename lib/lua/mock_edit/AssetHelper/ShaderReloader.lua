module 'mock_edit'
local function onAssetModified( node )
	local atype = node:getType()
	local toUpdate = {}
	if atype == 'fsh' or atype == 'vsh' then
		local path = node:getNodePath()
		local programs = mock.getShaderPrograms()
		for key, prog in pairs( programs ) do
			if prog.vsh == path or prog.fsh == path then
				prog:build( true )
			end
		end
	elseif atype == 'shader' then
		local config = node.cached and node.cached.config
		if config then
			config:build( true )
		end
	else
		return
	end
	gii.emitPythonSignal( 'scene.update' )

end

connectSignalFunc( 'asset.modified', onAssetModified )

