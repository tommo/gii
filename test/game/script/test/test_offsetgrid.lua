
CLASS: GlobalLogic ( Entity )
function GlobalLogic:onThread()
	local gridDeck=TMOffsetGridDeck.new()
	
	local prop=self:addProp{
		deck=res.tex['tile']
	}

	local prop1=self:addProp{
		deck=res.tex['walledge']
	}

	local w,h=100,100

	local grid=MOAIGrid.new()
	grid:setSize(w,h,32,20)
	grid:fill(4)
	
	prop:setGrid(grid)
	-- prop:setRot(45,45,0)
	-- prop:moveRot(0,180,180,10,MOAIEaseType.LINEAR)

	
	-- local grid1=MOAIGrid.new()
	-- grid1:setSize(w*2,h*2,32/2,20/2)
	-- grid1:fill(0)
	
	-- prop1:setGrid(grid1)
	self.scene.camera:setLoc(200,100)
end


sceneGlobal=Scene{
	
}

function sceneGlobal:onEnter()
	
	
	globalLogic=self:add(GlobalLogic())

	MOAIGfxDevice.setClearDepth(false)
	game:setClearColor(0,0,0,1)

end

game:addScene('global',sceneGlobal)
