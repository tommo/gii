module 'mock_edit'

function requestAvailSQNodeTypes()
	local reg = mock.getSQNodeRegistry()
	local result = {}
	for name, entry in pairs( reg ) do
		table.insert( result, name )
	end
	return result
end

function createSQNode( name, contextNode, contextRoutine )
	local entry = mock.findInSQNodeRegistry( name )
	if not entry then
		_warn( 'sq node registry not found', name )
		return nil
	end
	local clas = entry.clas
	local node = clas()
	if not contextNode then --root node
		contextRoutine:addNode( node )
	else
		if contextNode:isGroup() then
			contextNode:addChild( node )
		else
			local parentNode = contextNode:getParent()
			local index = parentNode:indexOfChild( contextNode )
			parentNode:addChild( node, index+1 )
		end
	end
	return node
end

