CLASS: TestActor ( Entity )

TestActor:applyFSMTrait(FSMDATA['test'])

function TestActor:onLoad()	
	self.text=self:addTextBox{
		string='this is a state'
	}
	self:setState'wander'
	self:initFSM()
end

function TestActor:onUpdate()
	self:updateFSM()
	self.text:setString(self.state)
end

function TestActor.fsm.system.common.wander:step()
	self:setColor(rand(0,1),rand(0,1),rand(0,1),1)
end

function TestActor.fsm.system.common.wander:exit(full_to, to)
	if to=='rest' then
		self:seekScl(2,2,1,1)
	end
end

function TestActor.fsm.system.common.wander:enter(full_from, from)
	if from=='rest' then
		self:seekScl(1,1,1,0.5)
	end
end

function TestActor.fsm.destroy:enter()
	self:destroy()
end

-- function TestActor:state_fight_exit(to)
-- 	if to=='wander' then
-- 		self:seekScl(1,1,1,1)
-- 	end
-- end


function TestActor:onKey(key,down)
	if not down then return end
	if key=='t' then self:tell('tired') end
	if key=='r' then self:tell('recovered') end
	if key=='m' then self:tell('rest_too_much') end

	if key=='f' then self:tell('enemy.found') end
	if key=='k' then self:tell('enemy.killed') end
	if key=='s' then self:tell('stop') end
end

function OnTestStart(logic)
	local a=logic:addSibling(TestActor())
end