CLASS: TestManualGrid ( Entity )

function TestManualGrid:onLoad()
	print('create blocker')
	self.blocker=TMManualBlocker.new()	
	
	self:addCoroutine('threadBlocked')
	self:addCoroutine('threadBlocking')

end

function TestManualGrid:threadBlocked()
	print('start')
	self.blocker:blockCurrentAction()
	-- self:wait(self.blocker)
	-- MOAICoroutine.blockOnAction(self.blocker)
	print('end')
end

function TestManualGrid:threadBlocking()
	print('wait 1 sec',self.blocker:isBlocked())
	self:wait(2)
	self.blocker:unblock()
	print('unblock!',self.blocker:isBlocked())
end


sceneGlobal:add(TestManualGrid())
