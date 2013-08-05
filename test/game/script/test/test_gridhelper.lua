CLASS: TestGridHelper ( Entity )

function TestGridHelper:onLoad()
	assert(MDDHelper)
	assert(MDDHelper.canSeeCell)
	assert(MDDHelper.getSeeableCells)

	local grid=MOAIGrid.new()

	grid:setSize(5,5,1,1)
	grid:fill(0)

	grid:setTile(2,2,1) --center

	-- grid:setTile(2,1,1) --bottom
	-- grid:setTile(2,3,1) --top
	-- grid:setTile(1,2,1) --left
	-- grid:setTile(3,2,1) --right

	for i=1,4 do
		grid:setTile(i,i,1)
	end


	table.foreach(
		{MDDHelper.getSeeableCells(grid, 2,2, 1)},
		function(i,idx) print(grid:cellAddrToCoord(idx)) end
		)

end

sceneGlobal:add(TestGridHelper())
