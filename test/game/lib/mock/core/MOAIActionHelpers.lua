----TODO: move related host code from MDD into libmoai
local yield=coroutine.yield
local tmpNode=MOAIColor.new()

local setAttr=tmpNode.setAttr
local seekAttr=tmpNode.seekAttr
local moveAttr=tmpNode.moveAttr


local tmpaction=MOAITimer.new()
local EVENT_STOP=MOAIAction.EVENT_STOP
local setListener=tmpaction.setListener
function funcAfter(action,func)
	return setListener(action,EVENT_STOP,func)
end

if MDDHelper then
	local blockAction=MDDHelper.blockAction
	function actionAfter(action,actionLater)
		blockAction(actionLater,action)
		return actionLater
	end
end

-- function laterCall(t,f,...)
-- 	local thread=MOAICoroutine.new()

-- 	thread:run(function(...)
-- 		local t0=game:getTime()
-- 		while game:getTime()-t0<t do
-- 			yield()
-- 		end
-- 		return f(...)
-- 	end,...)

-- 	return thread
-- end


function laterCall(t, f, ... )
	local args = {...}
	local timer = MOAITimer.new()
	timer:setListener( MOAITimer.EVENT_TIMER_END_SPAN,  
		function() return f(unpack(args)) end
	)
	timer:setSpan( t )
	timer:start()
	return timer
end

function actionChain(list)
	local thread=MOAICoroutine.new()
	thread:run(function()
		for i , action in ipairs(list) do
			if type(action)=='userdata' then
				action:pause()
			end
		end

		for i , action in ipairs(list) do
			local tt=type(action)
			if tt=='number' then --wait time
				local t0=game:getTime()
				while game:getTime()-t0<action do
					yield()
				end
			elseif tt=='function' then --function block
				action()
			else --MOAIAction
				action:start()
				while not action:isDone() do 
					yield() 
				end
			end
		end
	end)
	return thread
end

function actionGroup(list)
	local thread=MOAICoroutine.new()
	thread:run(function()
		
		while true do
			local busy=false
			for i , action in ipairs(list) do
				if action:isBusy() then
					busy=true
					break
				end
			end
			if not busy then return end
		end

	end)
	return thread
end

function delayedFunc(func,time,parentAction)
	local timer=MOAITimer.new()
	timer:setSpan(time)
	funcAfter(timer,func)
	if parentAction then
		timer:start(parentAction)
	else
		timer:start()
	end
	return timer
end

function threadAction(func,parentAction)
	local thread=MOAICoroutine.new()
	thread:run(func)
	if parentAction then
		thread:attach(parentAction)
	end
	return thread
end

function timedAction(func,time)
	if not time or time <=0 then return end
	local thread=MOAICoroutine.new()
	thread:run(function()
			local baseTime=game:getTime()
			while true do
				-- print('timed action',time,basetime)
				local ntime=game:getTime()
				local diff=ntime-baseTime
				local k=diff/time
				func(k>1 and 1 or k)
				if diff>=time then return end
				coroutine.yield()
			end
		end
	)
	return thread
end

-------Anim curve helper

function createAnimCurve( data, easeType )
	local curve=MOAIAnimCurve.new()
	for i, node in ipairs( data ) do
		curve:setKey(i,
			node[1],
			node[2],
			node.ease or easeType,
			node.weight
		)
	end
	return curve
end

function createLinearAnimCurve( from, to, step, fps, startTime, easeType )
	fps       = fps  or 60
	step      = step or 1
	easeType  = easeType or MOAIEaseType.FLAT
	startTime = startTime or 0

	local curve = MOAIAnimCurve.new()

	if from > to then	step = -step end

	local count = math.floor( ( to - from ) / step ) + 1
	curve:reserveKeys( count )

	for frame = 1, count do
		local ftime = startTime + ( frame - 1 ) / fps
		local value = from + ( frame -1 )
		curve:setKey( frame, ftime, value, easeType )
	end

	return curve
end

