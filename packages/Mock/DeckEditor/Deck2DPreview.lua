--------------------------------------------------------------------
scn = gii.createMockEditorScene()
--------------------------------------------------------------------

CLASS: Preview ( mock.Entity )
function Preview:onLoad()
	self:addSibling( CanvasGrid() )
	self:addSibling( CanvasNavigate() )
	self.prop = self:addProp{
		blend = 'alpha'
	}
	self.zoom = 1

end

function Preview:show( path )
	self:detach( self.prop )
	self.prop = self:addProp{
		blend = 'alpha'
	}
	local deck = mock.loadAsset(path)
	if not deck then return false end 
	if deck:getClass() == MOAITileDeck2D then
		local grid = MOAIGrid.new()
		local col, row = deck:getSize()
		local tw , th  = deck.tw , deck.th
		local sp = deck.spacing
		grid:setSize( col, row, tw + sp, th + sp, 0, 0, tw, th)
		local t = 1
		for j = row, 1, -1 do
			for i = 1, col do
				grid:setTile( i, j, t )
				t=t+1
			end
		end
		self.prop:setGrid( grid )
	end
	self.prop:setDeck( deck )
	self.prop:forceUpdate()
	updateCanvas()
end


preview = scn:addEntity( Preview() )

function show( path )
	preview:show( path )
end
