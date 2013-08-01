--[[
* MOCK framework for Moai

* Copyright (C) 2012 Tommo Zhou(tommo.zhou@gmail.com).  All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
]]

CLASS: MOAIDirectLeaderboard()

function MOAIDirectLeaderboard:__init( data )
	local obj=self
	local board,clientKey=data.board,data.clientKey
	if not (board and clientKey) then
		error('board and clientKey must be defined',2)
	end

	obj.caller=MOAICloudCaller{
		path='moai/leaderboard/'..board,		
		clientKey=clientKey,
		needSign=data.needSign,	
		secret=data.secret,				
	}
	obj.unique=data.unique		
end


function MOAIDirectLeaderboard:postScore(userid,username,score)
	return self.caller:call({
		userid=userid,
		username=username,
		score=score,
		unique=self.unique
	},'post')
end

function MOAIDirectLeaderboard:getScore(userid,pagesize)
	return self.caller:call({
			userid=userid,
			pagesize=pagesize,
			sort='desc'
		})
end

function MOAIDirectLeaderboard:getNeighborScore(userid,before,after)
	return self.caller:call{
		userid=userid,
		before=before,
		after=after,
		neighborhood=true	
	}
end


--example

-- local board1=MOAIDirectLeaderboard{
-- 	board='test',
-- 	clientKey='hGkjQuPotBGbLOwYEMmkEgAYwPAZNvQk',
-- 	unique=true,
-- 	secret='Vws8mM7MAtPcU86JG8yBgnsKD8irQT8qrbUof07rvagSgQ0wXw',
-- 	needSign=false
-- }

-- -- print'posting random scores'
-- -- for i=1,100 do
-- -- 	local j=i%10
-- -- 	board1:postScore('user_'..j,'player'..j,rand(1000,30000))
-- -- end
-- -- print'try query'

-- local task=board1:getNeighborScore('user_3',3,3)
-- local th1=MOAICoroutine.new()

-- th1:run(function()
-- 	local code=task:wait()
-- 	print'request done:'
-- 	if code==200 then
-- 		for i,r in pairs(task.result) do
-- 			print('name:',r.username,
-- 				'score:',r.score,'rank:',r.rank)
-- 		end
-- 	else
-- 		print('failed,code:',code)
-- 	end
-- end
-- )



