CLASS: PathGridTest ( Entity )

local w,h=200,150
local tw,th=5,5

local rx0,ry0,rx1,ry1=1,1,3,1

function PathGridTest:onLoad()
	local cam = self:attach( mock.Camera() )
	self:attach( mock.InputScript() )
	self:attach( mock.DrawScript() )

	local grid=TMPathGrid.new()
	self.w=w
	self.h=h

	grid:init(w,h,3,3)
	grid:registerTileType(1, 0x1)
	grid:registerTileType(2, 0x1)

	for i = 2, w-1 do
		for j = 2, h-1 do
			grid:setTile( i, j, 1 )
		end
	end

	for k = 10, h-1, 20 do
		for i = 2, w-1 do
			grid:setTile( i, k, 0 )
		end
	end


	for k = 10, w-1, 20 do
		for i = 2, h-1 do
			grid:setTile( k, i, 0 )
		end
	end



	print(grid:setTile(1,1,2))
	print(grid:setTile(2,1,1))
	print(grid:setTile(4,1,2))
	-- print(grid:setTile(3,1,1))
	-- print(grid:setTile(4,1,1))
	-- print(grid:setTile(2,1,2))

	print(grid:isReachable(1,1,3,1,0x1,true))
	-- printGrid(grid,w,h)	
	
	-- print(grid:setTile(2,1,1))	
	-- printGrid(grid,w,h)	
	
	-- print(grid:setTile(2,2,1)) --connect
	-- printGrid(grid,w,h)	

	self.grid=grid

	-- self:setLoc(-w/2*tw,-h/2*th)

	cam:setLoc(w/2*tw,h/2*th)
end

local colors={[0]={.1,.1,.1,1}}
local function getColor(id)
	local c=colors[id]
	if not c then c={rand(0.2,1),rand(0.2,1),rand(0.2,1),1} colors[id]=c end
	return unpack(c) 
end

local drawRect=MOAIDraw.fillRect
local drawRect2=MOAIDraw.drawRect
local drawCircle=MOAIDraw.drawCircle

local setPenColor=MOAIGfxDevice.setPenColor
function PathGridTest:onDraw()
	local grid=self.grid
	local w,h=self.w,self.h
	for yy=h,1,-1 do
		for xx=1,w do
			local t=grid:getSectionId(xx,yy)
			local code=grid:getTile(xx,yy)
			local x,y=xx*tw,yy*th
			setPenColor(getColor(t))
			if code==2 then
				drawRect(x,y,x+tw-1,y+th-1)
			else
				drawRect(x+1,y+1,x+tw-2,y+th-2)
			end
			if xx==rx0 and yy==ry0 then
				setPenColor(1,1,1,1)
				drawRect2(x-1,y-1,x+tw+1,y+th+1)
			elseif xx==rx1 and yy==ry1 then
				setPenColor(1,1,1,1)
				drawRect2(x-1,y-1,x+tw+1,y+th+1)
				
			end

		end
	end
	

end

function PathGridTest:onMouseEvent(ev,x,y,btn)
	if ev~='down' then return end
	x,y=self:wndToModel(x,y)
	local tx,ty=floors(x/tw,y/th)
	if tx>0 and tx<=self.w and ty>0 and ty<=self.h then
		
		if btn=='left' then
			local t = os.clock()
			self.grid:setTile(tx,ty,1)
			printf("%.2f",(os.clock()-t) * 1000 )
		elseif btn=='middle' then
			local t = os.clock()
			self.grid:setTile(tx,ty,0)
			printf("%.2f",(os.clock()-t) * 1000 )
		else
			self.grid:setTile(tx,ty,2)
		end

		if self.grid:isReachable(rx0,ry0,rx1,ry1,nil,true) then
			game:setClearColor(0,.1,0,1)
		else
			game:setClearColor(.1,0,0,1)
		end

	end
end

function printGrid(g,w,h)
	for x=1,w do
		io.write('---')
	end
	print()
	for y=h,1,-1 do
		for x=1,w do
			io.write(string.format('%2d ',g:getSectionId(x,y)))
		end
		io.write('\n')
	end
	for x=1,w do
		io.write('---')
	end
	print()

end

function OnTestStart(logic)
	logic:addChild(PathGridTest())
	
end

-- NO_WINDOW=true