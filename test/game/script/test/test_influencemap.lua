CLASS: InfluenceMapTest ( Entity )

local W,H = 40, 30
local TS = 3*100/W
function InfluenceMapTest:onLoad()
	self.cam = self:attach( mock.Camera() )
	self.input = self:attach( mock.InputScript() )
	self:attach( mock.DrawScript() )
	-- self.prop = self:attach( mock.Prop() )
	self.map  = TMInfluenceMap.new()

	local function fromDiffusionRate( targetRate, diffusionRate )
		local decayRate = targetRate / ((4/1.4+4) * diffusionRate/ 8 )
		return decayRate
	end

	local function fromDecayRate( targetRate, decayRate )
		local diffusionRate = ( targetRate / decayRate ) / ( 4/1.4 + 4 ) * 8
		return diffusionRate
	end


	local targetRate = 0.99
	local diffusionRate = 1/2
	local decayRate = 0.90

	-- diffusionRate = fromDecayRate( targetRate, decayRate )
	-- decayRate = fromDiffusionRate( targetRate, diffusionRate )

	print (  decayRate, diffusionRate, targetRate )
	self.map:init( W, H, 0, decayRate, diffusionRate )
	self.cam:setLoc( W * TS/2, H*TS/2 )

	self.walker = TMInfluenceMapWalker.new()
	self.walker:reserve( 1 )
	self.walker:setMap( 1, self.map,  0.5, 0, .5)
	local wallSource = -100

	-- for x = 3, W-2 do
	-- 	self.map:addSource( x, 2, wallSource )
	-- 	self.map:addSource( x, H-1, wallSource )	
	-- end

	-- for x = 3, W-3 do
	-- 	self.map:addSource( x, 4, wallSource )
	-- end

	-- for y = 1, H do
	-- 	self.map:addSource( 2,   y, wallSource )
	-- 	self.map:addSource( W-1, y, wallSource )
	-- end
	self.walker:setLoc( 3, 3 )

end


drawRect = MOAIDraw.drawRect
fillRect = MOAIDraw.fillRect
setPenColor = MOAIGfxDevice.setPenColor
function InfluenceMapTest:onDraw()
	local map = self.map
	local walker = self.walker
	for y = 1, H do
		for x = 1, W do
			local v = walker:calcScore( x, y ) / 400 

			if v >0 then 
				setPenColor( math.min(v+0.1,1), 0, 0, 1 )
			elseif v < 0 then
				setPenColor( 0, 0, math.min( -v+0.1,1), 1 )
			else
				setPenColor( 0, 0, 0 ,1 )

			end
			local x , y = (x-1) * TS, (y-1) * TS
			fillRect( x, y, x+TS-1, y+TS-1 )
		end
	end
	local x , y = walker:getLoc()
	x, y = (x-1) * TS, (y-1) * TS
	setPenColor( 0, 1, 0, 1 )
	drawRect( x, y, x+TS-1, y+TS-1 )
end

function InfluenceMapTest:onMouseEvent( ev, x, y, btn )
	x, y = self:wndToWorld(x, y)
	local c, r = math.floor(x/TS) , math.floor(y/TS)
	if ev == 'move' then
		-- if c>0 and c<W and r>0 and r<H then
		-- 	self.map:setCell( c, r, -10000 )
		-- end		
	end

	if ev == 'down' then
		if btn == 'middle' then
			self.walker:setLoc( c, r )
			return
		end

		local value = btn == 'left' and 1000 or btn=='right' and -1000 or 0
		
		if mock.isKeyDown('s') then
			self.map:addSource( c, r, value )
		else
			self.map:setCell( c, r, value )
		end

	end
end

function InfluenceMapTest:updateWalker()
	local x, y = self.walker:getLoc()
	local dx, dy = self.walker:getVector( x, y )
	self.walker:setLoc( x + dx, y + dy )
end

function InfluenceMapTest:onKeyDown( key )
	if key == 'space' then
		local x,y= mock.getMouseLoc()
		x, y = self:wndToWorld(x, y)
		local c, r = math.floor(x/TS) , math.floor(y/TS)
		print( self.map:getCell(c,r) )

		-- self.map:update()
	elseif key == 'r' then
		self.map:clearMap()
	elseif key == 't' then
		self.map:clearSource()
	end
end

local x=0
local y=0
function InfluenceMapTest:onUpdate( dt )
	if y == 1 then 
		y=0
		self.walker:updateStep()
	else
		y = y+1
	end
	
	if x == 20 then x=0 else x = x+1 return end
	self.map:update()
end

function OnTestStart(logic)
	logic:addChild(InfluenceMapTest())
	MOAIGfxDevice.getFrameBuffer():setClearColor(.5,.5,.5,1)
end


