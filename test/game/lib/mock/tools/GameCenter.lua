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


registerSignals{
	'gamecenter.login',
	'gamecenter.achievement.ready',
	'gamecenter.report.complete',
}

CLASS: GameCenterHelper ()

local function gameCenterReportCompletionHandler(job,errorcode)
	return gameCenterHelper:onReportCompletion(job,errorcode)
end

local function gameCenerGetScoreHandler(a)
	-- table.print(a)
end


function GameCenterHelper:init()
	if not checkOS("iOS") then return end

	self.reportScoreQueue={}
	self.reportAchievementQueue={}

	self.reportingScore=false
	self.reportingAchievement=false
	
	MOAIGameCenterIOS.setReportCompletionCallback(gameCenterReportCompletionHandler)
	MOAIGameCenterIOS.setGetScoresCallback(gameCenerGetScoreHandler)

	-- self.lastReportScoreTime=false
	-- self.lastReportAchievementTime=false

end

function GameCenterHelper:getAchievements()
	return self.achievements
end

function GameCenterHelper:reportScore(score,boardID)
	--todo: only keep highest score?
	table.insert(self.reportScoreQueue,
		{
			score=score,
			boardID=boardID
		}
	)
	self:syncNow()
end

function GameCenterHelper:reportAchievement(name,progress)
	table.insert(self.reportAchievementQueue,
		{
			name=name,
			progress=progress or 100
		}
	)
	self:syncNow()
end

function GameCenterHelper:onReportCompletion(job,errorcode)
	
	emitSignal('gamecenter.report.complete',job,errorcode)

	if errorcode then  --fail to sync, push back...
		print('reporting failed:',job,errorcode)
		if job=='achievement' then
			table.insert(self.reportAchievementQueue,self.reportingAchievement)
			self.reportingAchievement=false
		else
			table.insert(self.reportScoreQueue,self.reportingScore)
			self.reportingScore=false
		end
	else
		print('reporting done:',job)
		if job=='achievement' then			
			self.reportingAchievement=false
		else
			self.reportingScore=false
		end
	end

	game:updateSetting('gamecenter_cache',{
			reportScoreQueue=self.reportScoreQueue,
			reportAchievementQueue=self.reportAchievementQueue,
		}
	)
end


function GameCenterHelper:login()
	local function onAuthenticate(errorcode)		
		local data=game:getSetting('gamecenter_cache')
		if data then
			self.reportScoreQueue=data.reportScoreQueue or {}
			self.reportAchievementQueue=data.reportAchievementQueue or {}
			if self:hasInQueue() then
				self:syncNow()
			end
		end
		return emitSignal('gamecenter.login',not errorcode, errorcode)
	end


	local function onAchievementReady(errorcode)
		if not errorcode then 
			self.achievements=MOAIGameCenterIOS.getAchievements()
			-- print('achievements ready')
			-- table.print(self.achievements)
			return emitSignal('gamecenter.achievement.ready')
		end
	end
	-- print('Login Gamecenter')

	MOAIGameCenterIOS.setAchievementReadyCallback(onAchievementReady)
	MOAIGameCenterIOS.authenticatePlayer(onAuthenticate)
	
end

function GameCenterHelper:isSupported()
	return MOAIGameCenterIOS.isSupported()
end

function GameCenterHelper:syncNow()
	--sync queued reports
	if not self:isSupported() then return end
	if self.actionSync then return end

	self.actionSync=threadAction(function()
			self:threadSync()
			self.actionSync=nil
		end)

end

function GameCenterHelper:threadSync()
	while true do
		if not self.reportingAchievement then
			local a=table.remove(self.reportAchievementQueue,1) or false
			if a then
				self.reportingAchievement=a
				print('reporting:',a.name,a.progress)
				MOAIGameCenterIOS.reportAchievementProgress(a.name,a.progress)
			end
		end

		if not self.reportingScore then
			local r=table.remove(self.reportScoreQueue,1) or false
			if r then 
				self.reportingScore=r
				print('reporting:',r.boardID,r.score)
				MOAIGameCenterIOS.reportScore(r.score,r.boardID)
			end
		end

		if not self:hasInQueue() then return end
		coroutine.yield()
	end

end

function GameCenterHelper:hasInQueue()
	return next(self.reportScoreQueue) or next(self.reportAchievementQueue)
end

function GameCenterHelper:showLearderboardList()
	_codemark('Show Leaderboard List')
	return MOAIGameCenterIOS.showDefaultLeaderboard()
end

function GameCenterHelper:showLeaderboard(boardID)
	_codemark('Show Leaderboard: %s',boardID)
	return MOAIGameCenterIOS.showLeaderboard(boardID)
end

function GameCenterHelper:showAchivements()
	_codemark('Show Achievements')
	return MOAIGameCenterIOS:showDefaultAchievements()
end

gameCenterHelper=GameCenterHelper()
gameCenterHelper:init()