local function isEntityPickable( ent )
	if ent.FLAG_EDITOR_OBJECT then return false end
	if not ent:isVisible() then return false end
	local layerSrc = ent.layer.source
	if not layerSrc:isVisible() then return false end
	if not layerSrc:isEditorVisible() then return false end
	if layerSrc.editorSolo == 'hidden' then return false end
	if layerSrc:isLocked() then return false end
	return true
end

local function _pick( ent, x, y ) --depth first search
	if not isEntityPickable( ent ) then return nil end
	-- local children = ent.children
	-- if children then
	-- 	for child in pairs( children ) do
	-- 		local pickedEnt = _pick( child, x, y )
	-- 		if pickedEnt then return pickedEnt end
	-- 	end
	-- end
	local picked = ent:pick( x, y )
	if picked then return ent end
	return nil
end

function SceneViewBase:pick( x, y )
	--TODO: use layer order?
	local candidates = {}
	for ent in pairs( self:getScene().entities ) do
		-- if isEntityPickable( ent ) and ent:inside( x, y ) then
		-- 	table.insert( candidates, ent )
		-- end
		if not ent.parent then
			local p = _pick( ent, x, y )
			if p then
				table.insert( candidates, p )
			end
		end
	end

	--TODO:sort and find
	return candidates[1]
end