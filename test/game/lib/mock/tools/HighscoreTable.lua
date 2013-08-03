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

CLASS: HighscoreTable ()

function HighscoreTable:__init(settings)
	self.records={}
	self.settings=self.settings or {}
end

function HighscoreTable:report(score,userdata,sync)
	if score<=0 then return 0,0 end
	
	local rank=0
	local lv=userdata and userdata.level
	local records=self.records
	local ctime=os.time()
	local nv={
			score=score,
			userdata=userdata,
			time=ctime,
			isnew=true
		}

	local todayRank=0

	local inserted
	for i, v in ipairs(records) do 
		v.isnew=false
		local diff=ctime-v.time
		-- print(diff,24*3600)
		if diff<=24*3600 then --today?
			todayRank=todayRank+1
		end

		if not inserted and  score > v.score or 
			lv and score ==v.score and lv > v.userdata.level then
			rank=i
			inserted=true
			table.insert(records,i,nv)
			break
		end
	end


	if not inserted then		
		table.insert(records,nv)
		rank=#records
		todayRank=todayRank+1
	end

	--trim
	self.records=table.sub(records,1,self.settings.recordSlotCount or 1000)

	if todayRank==1 or not self.settings.onlySyncHighest then
		self:doSync(score)
	end
	
	return rank,todayRank
end



function HighscoreTable:doSync(score)
	if checkOS('iOS') then
		if self.settings.leaderboardID then
			gameCenterHelper:reportScore(score,self.settings.leaderboardID)
		end

	else --use other game stat service?

	end
end

function HighscoreTable:fetchScore(from, count, timespan)
	from=from or 1
	count=count or 1
	timespan=timespan or 'all'
	local result={}

	if timespan=='all' then
		for i=from ,from+count-1 do 
			local v=self.records[i]
			if not v then break end
			result[i-from+1]=v
		end
	elseif timespan=='today' then --todo
	end

	return result
end

function HighscoreTable:fetchTopScore(timespan)
	local list=self:fetchScore(1,1,timespan)
	return list[1]
end