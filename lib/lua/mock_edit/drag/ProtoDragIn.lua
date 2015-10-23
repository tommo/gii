module 'mock_edit'

--------------------------------------------------------------------
CLASS: ProtoDragIn ( SceneViewDrag )
	:MODEL{}

function ProtoDragIn:__init( path, x, y  )
	local cmd = gii.doCommand( 
		'scene_editor/create_proto_instance', 
		{ 
			proto = path,
			create_sibling = true
		}
	)
	local instance = cmd and cmd.getResult()
	self.protoInstance = instance or false
end

function ProtoDragIn:onStart( view, x, y )
	self:updateInstanceLoc( view, x, y )
end

function ProtoDragIn:onMove( view, x, y )
	self:updateInstanceLoc( view, x, y )
end

function ProtoDragIn:onStop( view )
	self.protoInstance:destroyWithChildrenNow()--FIXME: use undo
	-- gii.undoCommand()
	view:updateCanvas()
end

function ProtoDragIn:updateInstanceLoc( view, x, y )
	if not self.protoInstance then return end
	x, y = view:wndToWorld( x, y )
	self.protoInstance:setWorldLoc( x, y )
	view:updateCanvas()
end

--------------------------------------------------------------------
CLASS: ProtoDragInFactory ( SceneViewDragFactory )
	:MODEL{}

function ProtoDragInFactory:create( view, mimeType, data, x, y )
	if mimeType ~= 'application/gii.asset-list' then return false end
	local result = {}
	for i, path in ipairs( data ) do
		local node = mock.getAssetNode( path )
		local assetType = node:getType()
		if assetType == 'proto' then
			return ProtoDragIn( path, x, y )
		end
	end
	return result
end
