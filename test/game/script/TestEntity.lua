require 'mock'

--
CLASS: TestEntity ( mock.Entity )

function TestEntity:onLoad()
	self:attach( mock.DrawScript() )
	-- local sprite = self:attach(
	-- 	mock.AuroraSprite{
	-- 		sprite    =  mock.loadAsset('anim/output.sprite'),
	-- 		fps       =  10,
	-- 	})
	-- sprite:play( 'walk', MOAITimer.LOOP )
	-- sprite:setScl( 10, 10 )
end

function TestEntity:onDraw()
	MOAIDraw.drawRect( -10, -10, 10, 10 )
end

mock.registerEntityType( 'Test', TestEntity )
--------------------------------------------------------------------

