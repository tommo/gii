
CLASS: TestDungeonMap ( Entity )

function TestDungeonMap:onLoad()
	local map = MDDMap.new()
	self.map = map
	map:init( 50, 50, 32, 10 )
	self.pathGrid  = map:getPathGrid()
	self.partition = map:getPartition()
	print(self.pathGrid, self.partition)
end

function TestDungeonMap:addMapObject( obj )
	self.map:insertObject( obj._prop )
end

CLASS: Creature ( Entity )
function Creature:_createEntityProp()
	return MDDMapObject.new()
end

function Creature:onLoad()
	self:attach( mock.DrawScript() )
end

function Creature:onDraw()
	MOAIDraw.drawRect(0,0,10,10)
end


CLASS: MDDMapTest ( Entity )
function MDDMapTest:onLoad()
	self.map = self:addSibling( TestDungeonMap() )
	local creature = Creature()
	self.map:addMapObject( creature )
end

function OnTestStart(logic)
	logic:addChild( MDDMapTest() )
end

