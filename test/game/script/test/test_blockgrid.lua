CLASS: Camera ( Entity )

function Camera:onLoad()
	local cam = self:attach( Camera() )
	
	self.vx,self.vy=0,0
	self.tx,self.ty=0,0

	self.damping=0.8
	self.holded=false
	self.floating=false
	cam:setPiv(0,0,5000)
	cam:setRot(-(90-MapObjectViewRotation),0,0)
	-- cam:setRot(MapObjectViewRotation,0,0)
	self._cam=cam
end

function Camera:followObject(o)
	self.followingObject=o
	-- if o then
	-- 	local trans=self.trans
	-- 	trans:setAttrLink(MOAITransform.ATTR_X_LOC,o.trans,MOAITransform.ATTR_X_LOC)
	-- 	trans:setAttrLink(MOAITransform.ATTR_Y_LOC,o.trans,MOAITransform.ATTR_Y_LOC)
	-- else
	-- 	local trans=self.trans
	-- 	trans:setAttrLink(MOAITransform.ATTR_X_LOC,nil)
	-- 	trans:setAttrLink(MOAITransform.ATTR_Y_LOC,nil)
	-- end
end

function Camera:pointObject(o,t)
	o:forceUpdate()
	local x,y=o:getWorldLoc()
	self:setTarget(x,y,t)

end


function Camera:setTarget(x,y)
	self.tx,self.ty=x,y
	self.floating=false
end

function Camera:setDamping(damping)
	self.damping=damping or 0.5
end

function Camera:hold(holder)	
	if self.holder then return false end
	self.vx,self.vy=0,0
	local x,y=self:getLoc()
	self:setTarget(x,y)	
	self.holder=holder
	return true
end

function Camera:unhold(holder,nofloating)
	if self.holder~=holder then return false end
	self.holder=false
	self.floating= not nofloating
	return true
end

function Camera:drag(vx,vy)
	-- self.vx,self.vy=vx,vy
	self:addTargetLoc(vx,vy)
end

function Camera:addTargetLoc(dx,dy)
	return self:setTarget(self.tx+dx,self.ty+dy)
end

local floor=math.floor
function Camera:addLoc(x,y)
	return self.trans:addLoc(floor(x),floor(y))
end
function Camera:setLoc(x,y)
	return self.trans:setLoc(floor(x),floor(y))
end

function Camera:onUpdate()

	if self.followingObject then
		local o=self.followingObject
		local x,y=o:getWorldLoc()
		self:setTarget(x,y)
	end

	if self.floating then
		local vx,vy=self.vx,self.vy
		if (vx~=0 or vy~=0) then
			local d=self.damping
			vx=vx*d
			vy=vy*d
			if vx*vx+vy*vy<1 then 
				vx=0 vy=0
			end
			self:addLoc(vx,vy)
			self.vx=vx
			self.vy=vy
		else
			self.tx,self.ty=self:getLoc()
			self.floating=false
		end
	else
		local x,y=self:getLoc()
		local tx,ty=self.tx,self.ty
		if (x~=tx or y~=ty) then
			local x1=lerp(x,tx,0.6)
			local y1=lerp(y,ty,0.6)
			self.vx,self.vy=x1-x,y1-y
			self:setLoc(x1,y1)
		end
	end
	
end



CLASS: TestBlockGrid ( Entity )

function TestBlockGrid:onLoad()
	self.cam=self:addSibling(Camera())

	local grid=MOAIGrid.new()
	local w,h=50,50
	grid:setSize(w,h,30,30)
	grid:fill(1)

	local wgrid=MOAIGrid.new()
	wgrid:setSize(w,h,30,30)

	local prop=self:attach( TMBlockProp.new() ) : setupProp{
			depthMask=true,
			depthTest=true,
		}

	local function registerBrush(option)
		return prop:registerBrush(option.id, 
			option.height, option.face, option.wall1, option.wall2, option.wallEdge)
	end

	registerBrush{
		id=1,
		height=4,
		face=17,
	}

	registerBrush{
		id=2,
		height=2,
		face=18,
		wall1=25,
		wall2=26,
		wallEdge=28
	}

	registerBrush{
		id=3,
		height=0,
		face=18,
		wall1=25,
		wall2=26,
		wallEdge=0
	}

	prop:setDeck(res.tex['tile_test'])
	prop:setGrid(grid)

	self.prop=prop

	self.wprop=self:addProp{
		deck=res.tex['tile_test'],
		depthMask=false,
		depthTest=true,
		transform={loc={0,0,48}}
	}

	self.wprop:setGrid(wgrid)
	self:setLoc(-w*32/2,-h*32/2,0)
	self:setScl(1.5,1.5)

	grid:fill(2)
	for x=1, w do
	for y=1,h do
		if prob(50) then 
			grid:setTile(x,y,1)
		elseif prob(50) then
			grid:setTile(x,y,2)
		else
			grid:setTile(x,y,3)
			wgrid:setTile(x,y,2)
		end
	end
	end
end

function TestBlockGrid:onUpdate()
	self.wprop:setPiv(0,0,wave(0.2,-1,1))
end


local xx,yy
function TestBlockGrid:onMouse(ev, x,y)
	-- if ev=='press' then
	-- 	xx=x
	-- 	yy=y
	-- end
	x,y=self:wndToWorld(x,y)
	if ev=='move' then
		self:setRot(y/2,0,x/5)
		-- self.prop:setRot(y/2,0)
		-- self:setColor(gradColor({{1,1,1,1},{1,.5,.5,1},{.5,.5,1,1}}, (x+500)/1000))
	end

end

function TestBlockGrid:onKey(key,down)
	local prop=self.prop
	if not down then return end
	if key=='w' then
		self:addLoc(0,-5)
	elseif key=='s' then
		self:addLoc(0,5)
	elseif key=='a' then
		self:addLoc(5)
elseif key=='d' then
		self:addLoc(-5)
	end

end

function TestBlockGrid:unitTestGrid()
	local grid=self.grid
	grid:setHeight(2,2, 1)
	grid:setPage(2,2, 5)
	grid:setWallEdge(2,2,3)
	grid:setWall(2,2,1,2)
	grid:setFace(2,2,7)

	print(grid:getHeight(2,2))
	print(grid:getPage(2,2))
	print(grid:getWallEdge(2,2))
	print(grid:getWall(2,2))
	print(grid:getFace(2,2))

	print(grid:getBlock(2,2))

	grid:setBlock(2,2,
		2, --height
		4, --page
		7, --walledge
		3,3, --walls
		9)
	print(grid:getBlock(2,2))
end

function OnTestStart(logic)
	MOAIGfxDevice.getFrameBuffer():setClearDepth(true)
	local a=logic:addSibling(TestBlockGrid())
end

