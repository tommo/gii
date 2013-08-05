local material = {
	name        = 'test',
	restitution = 1,
	friction    = 0,
	density     = 1,
	sensor      = false,
	coltype     = 1,
}

local LEAVE      = MOAIBox2DArbiter.END
local ENTER      = MOAIBox2DArbiter.BEGIN
local POST_SOLVE = MOAIBox2DArbiter.POST_SOLVE
local PRE_SOLVE  = MOAIBox2DArbiter.PRE_SOLVE

local bodySettings = {
	shapes = {
		{
			name = 'goo',
			type = 'circle',
			data = { 0,0, 10 }, --x,y,radius
			collision = true,
			collisionPhaseMask = LEAVE + ENTER
		}
	}
}


CLASS: BlockStatic ( Entity )
function BlockStatic:onLoad()
	local w,h= 500, 20
	local data={rectCenter(0,0,w-2,h-2)}
	local body=self:attach( mock.Box2DBody{
		type='static',
		fixedRotation=true,
		shapes={
				{type='rect', data=data, name='block'}
		}
	}	 )
end


CLASS: TestEntity ( Entity )
function TestEntity:onLoad()
	self.body = self:attach( mock.Box2DBody( bodySettings ) )
	-- self:attach( mock.DrawScript() )
end

function TestEntity:onCollision( phase, fixa, fixb, arb )
	self:destroy()
end

function TestEntity:onDestroy()
	self:addSibling( TestEntity() )
end

function TestEntity:onDraw()
	MOAIDraw.drawRect( 0,0, 10, 10 )
end

CLASS: CameraEntity ( Entity )
function CameraEntity:onLoad()
	self:attach( mock.Camera() )
end

function OnTestStart( logic )
	game:setupBox2DWorld{
		unitsToMeters = 1/ ( 60 ) ,
		gravity = { 0,-9.8 * 60 }
	}
	logic:addSibling( CameraEntity() )
	logic:addSibling( TestEntity() )
	logic:addSibling( BlockStatic{ transform={loc={0,-100}} } )

end

