print(TMPathGrid)
function quickFill(grid,w,h,fillX,fillY,code)
	local queueD={}
	local tailD,headD=0,0
	local function pushD(x,x1,y,d)
		tailD=tailD+1
		queueD[tailD]={x,x1,y,d}
		-- print('push',x,x1,y,d)
	end

	local function popD()
		if headD>=tailD then return nil end
		headD=headD+1
		local d=queueD[headD]
		queueD[headD]=nil
		-- print('pop ', d[1],d[2],d[3],headD)

		return d[1],d[2],d[3],d[4]
	end
	-----
	local function get(x,y) return grid:getTile(x,y) end
	local function set(x,y,v) 
		coroutine.yield()
		return grid:setTile(x,y,v)
	end
	
	local old=get(fillX,fillY)
	if old==0 then return end
	local new=code
	if old==new then return end
	pushD(fillX,fillX,fillY,-1)
	pushD(fillX,fillX,fillY+1,1)


	while true do
		--fill downward
		local x0,x1,y,d=popD()
		if not x0 then break end
		
		local nx0=-1
		local ny=y+d
		--span -x
		if get(x0,y)==old then
			for x=x0-1,1,-1 do
				if get(x,y)==old then					
					set(x,y,new)
					nx0=x
				else
					break
				end
			end
			if nx0>0 then 
				local ny1=y-d
				local nx1=-1

				for x=nx0,x0-1 do
					if get(x,ny1)==old then
						-- set(x,ny1,new)
						if nx1<0 then nx1=x end
					elseif nx1>0 then
						pushD(nx1,x-1,ny1,-d)
						nx1=-1
					end
				end
				if nx1>0 then
					pushD(nx1,x0-1,ny1,-d)
				end
			end
		end
		--span inside
		local nextNew=true
		for x=x0,x1 do
			if get(x,y)==old then
				set(x,y,new)
				if nx0==-1 then	nx0=x	end
			elseif nx0>0 then
				pushD(nx0,x-1,ny,d)
				nx0=-1
			end
		end
		--span +x
		if nx0>0 then			
			local broke=false
			local nx1=-1
			local ny1=y-d

			for x=x1+1,w do
				if get(x,y)==old then
					set(x,y,new)
					if get(x,ny1)==old then
						-- set(x,ny1,new)
						if nx1<0 then	nx1=x	end
					elseif nx1>0 then
						pushD(nx1,x-1,ny1,-d)
						nx1=-1
					end					
				else
					x2=x-1
					pushD(nx0,x-1,ny,d)
					broke=true
					break
				end
			end

			if not broke then	x2=w pushD(nx0,w,ny,d)	end
			if nx1>0 then
				pushD(nx1,x2,ny1,-d)
			end
			--check opposite

		end

		--fill upward
		-- coroutine.yield()
	end

	-- print("finished")
end


viewport = MOAIViewport.new ()
viewport:setSize ( 512, 384 )
viewport:setScale ( 512, 384 )

layer = MOAILayer2D.new ()
layer:setViewport ( viewport )
MOAISim.pushRenderPass ( layer )
local w,h=60,60
local t=5

grid = MOAIGrid.new ()
grid:setSize ( w,h , t,t, 0,0, t-1,t-1)
local fillcode=4
function initGrid()
	grid:fill(2)

	for i=1,w do
		for j=1,h do
			if prob(40) then grid:setTile(i,j,0) end
		end
	end
end

initGrid()
prop = MOAIProp2D.new ()
prop:setDeck ( res.tex['help_grid'] )
prop:setGrid ( grid )
layer:insertProp ( prop )
prop:setLoc(-w/2*t,-h/2*t)

local currentCoro=false
addMouseListener('m',function(ev,x,y,z,btn)
		if ev~='press' then return end
		x,y=layer:wndToWorld(x,y)
		x,y=prop:worldToModel(x,y)
		local tx,ty=grid:locToCoord(x,y)
			if btn=='left' and tx>0 and tx<=w and ty>0 and ty<=h then	
				local ot=grid:getTile(tx,ty)
				if ot==2 then
					grid:setTile(tx,ty,0)
				else
					grid:setTile(tx,ty,2)
				end
			end
		if grid:getTile(tx,ty)>0 then 
			if btn=='right' then
				MOAICoroutine.new():run(function()
					quickFill(grid,w,h,tx,ty,fillcode)
					end
				)
					print()
					print('>>>>>>>>>>>Start!!!-------')
				-- if currentCoro then

				-- else
				-- 	print()
				-- 	print('>>>>>>>>>>>Start!!!-------')
				-- 	-- MDDHelper.floodFillGrid(grid,tx,ty,4)
				-- 	currentCoro=coroutine.create(quickFill)
				-- 	local f,k=coroutine.resume(currentCoro,grid,w,h,tx,ty,4)
				-- 	if not f then error(k) end

				-- end
			end
		end
	end)

addKeyboardListener('k',function(key,down)
	if key=='c' and down then 
		if currentCoro then
			local f,k=coroutine.resume(currentCoro)
			if not f then error(k) end
			if coroutine.status(currentCoro)=='dead' then 
				print('DONE!!!',os.clock())
				currentCoro=nil
			end
		end
	end
	if key=='r' and down then 
		initGrid()
	end

	if key=='v' and down then
		if fillcode==4 then fillcode=3 else fillcode=4 end
	end

end
)