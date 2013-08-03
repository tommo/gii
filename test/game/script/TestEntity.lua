require 'mock'

--
CLASS: TestEntity ( mock.Entity )

function TestEntity:onLoad()
	local sprite = self:attach(
		mock.AuroraSprite{
			sprite    =  mock.loadAsset('anim/output.sprite'),
			fps       =  10,
		})
	sprite:play( 'walk', MOAITimer.LOOP )
	sprite:setScl( 10, 10 )
end


