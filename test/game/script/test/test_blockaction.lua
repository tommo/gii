CLASS: TestBlockAction ( Entity )
-- function TestBlockAction:onLoad()
-- 	local act0=delayedFunc(function() print('good') end,.1)
-- 	local act11=delayedFunc(function() print('bad') end,.1)

-- 	actionAfter(act0,act11)
-- end

-- function TestBlockAction:onLoad()	
-- 		local act0,act2
-- 		act0=delayedFunc(function() print('good') end,.15)
-- 		-- act2=delayedFunc(function() print('bad') end,.1)
-- 		act2=MOAICoroutine.new()
		
-- 		act0:start()
-- 		-- act0:pause()
-- 		-- act0:pause(false)
		
-- 		actionAfter(act0,act2)
-- 		print('blocked:',MDDHelper.isBlocked(act2))

-- 		delayedFunc(function()
-- 			print('0.1')

-- 			act2:run(function()  coroutine.yield() print('in thread') end)
-- 		-- MDDHelper.setActionPass(act2,0)

-- 			-- act2:pause()
-- 				-- act2:pause()
-- 				-- act2:attach(game.root)
-- 			-- act2:start()
-- 				-- print('*act2',MDDHelper.isBlocked(act2))
-- 			end,
-- 			.1):start()

-- 		delayedFunc(function()
-- 				print('0.5')
-- 				-- act2:start()
-- 				print('blocked:',MDDHelper.isBlocked(act2))
-- 				print(MDDHelper.getActionStat(act2))
-- 				-- print(act2:isActive(),act2:isBusy())
-- 				-- print('*act2',MDDHelper.isBlocked(act2))
-- 			end,
-- 			.5):start()


-- 		-- delayedFunc(function()
-- 		-- 	print('act2',MDDHelper.isBlocked(act2))
-- 		-- end,.5)
-- end

-- local shit=0
-- function TestBlockAction:onUpdate2()
-- 	shit=shit+1
-- 	if shit~=3 then return end
-- 	print('first')

-- 	local act0=delayedFunc(function() print('good') end,.1)
-- 	local act11=delayedFunc(function() print('bad') end,.1)

-- 	actionAfter(act0,act11)
-- end

-- function TestBlockAction:onLoad1()
-- 	local thread=MOAICoroutine.new()
-- 	local a1,a2

-- 	thread:run(function()
-- 		a2=delayedFunc(function() print('1 secs passed::B') end,.1)
-- 		a1=delayedFunc(function() 
-- 				print('1 secs passed::A') 				
-- 				print(a2:isActive(),a2:isBusy(),MDDHelper.isBlocked(a2))
-- 				-- a2:detach()
-- 				a2:start()
-- 			end,.1)

-- 		-- actionAfter(a1,a2)
-- 		-- 	print(MDDHelper.isBlocked(a2))
-- 		-- delayedFunc(function()
-- 		-- 	print(MDDHelper.isBlocked(a2))
-- 		-- end,2)
-- 		a2:pause()
-- 		while true do
-- 			coroutine.yield()
-- 		end

-- 	end)
-- end

function TestBlockAction:onThread()
	print('delayed action start')
	local t1=MOAIProp.new()	

	local timer1=delayedFunc(function() print('1 secs passed::A') end,1)
	local timer2=delayedFunc(function() print('1 secs passed::B') end,1)

	
	actionAfter(timer1,timer2)

	local act0=delayedFunc(function() print('good') end,1)
	local act11=delayedFunc(function() print('bad') end,1)

	actionAfter(act0,act11)

end



sceneGlobal:add(TestBlockAction())

