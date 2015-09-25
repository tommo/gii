module 'mock_edit'

--------------------------------------------------------------------
CLASS: TextureDragIn ( SceneViewDrag )
	:MODEL{}

function TextureDragIn:__init( path, x, y  )
	local entity = mock.Entity()
	local texturePlane = entity:attach( mock.TexturePlane() )
	texturePlane:setTexture( path )
	texturePlane:resetSize()
	entity:setName( stripdir(stripext(path)) )
	local cmd = gii.doCommand( 
		'scene_editor/add_entity', 
		{ 
			entity = entity
		}
	)
	self.createdEntity = entity
end

function TextureDragIn:onStart( view, x, y )
	self:updateInstanceLoc( view, x, y )
end

function TextureDragIn:onMove( view, x, y )
	self:updateInstanceLoc( view, x, y )
end

function TextureDragIn:onStop( view )
end

function TextureDragIn:updateInstanceLoc( view, x, y )
	if not self.createdEntity then return end
	x, y = view:wndToWorld( x, y )
	self.createdEntity:setWorldLoc( x, y )
	view:updateCanvas()
end

--------------------------------------------------------------------
CLASS: TextureDragInFactory ( SceneViewDragFactory )
	:MODEL{}

function TextureDragInFactory:create( view, mimeType, data, x, y )
	if mimeType ~= 'application/gii.asset-list' then return false end
	local result = {}
	for i, path in ipairs( data ) do
		local node = mock.getAssetNode( path )
		local assetType = node:getType()
		if assetType == 'texture' then
			return TextureDragIn( path, x, y )
		end
	end
	return result
end
