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

module 'mock'


registerSignals{
	'achievement.finish',	
	'achievement.report',
}

AchievementClasses={}

CLASS: Achievement ( Entity )
	:MEMBER{
		name   = 'achievement',
		icon   = 'empty',
		level  = 'bronze',
		desc   = '...',
		hidden = false,
		title  = 'Achievement',
	}

function Achievement:__init()
	local text=achievementTexts[self.name]
	assert(text,'no text found:'..self.name)
	self.title=text[1]
	self.desc=text[2]
end


function Achievement:checkAchievement()
end

function Achievement:setProgress(p)
	self.progress=p
	if p<100 and not self.actionChecking then
		self:startCheck()
	elseif p>=100 and self.actionChecking then
		self:stopCheck()
	end
end

function Achievement:startCheck()
	self.actionChecking=self:addCoroutine('threadCheck')
end

function Achievement:stopCheck()
	if self.actionChecking then
		self.actionChecking:stop()
		self.actionChecking=nil
	end
end

function Achievement:threadCheck()
	error'implement threadCheck please'
end

function Achievement:report(progress)

	progress=progress==true and 100 or progress
	progress=math.clamp(progress,0,100)

	if progress<=self.progress then return end

	self:setProgress(progress)
	self.center:reportProgress(self,progress)
end

	

--------------------------------------------------------------------
--------------------------------------------------------------------
CLASS: AchievementCenter ()
--------------------------------------------------------------------

function AchievementCenter:__init(settings)
	self.achievements={}
	self.progresses={}	
	self.settings=settings
end


function AchievementCenter:get(name)
	for i,a in ipairs(self.achievements) do
		if a.name==name then return a end
	end
	return nil
end

function AchievementCenter:getByGameCenterID(id)
	for i,a in ipairs(self.achievements) do
		if a.gameCenterID==id then return a end
	end
	return nil
end

function AchievementCenter:register(a)
	local name=a.name
	local progresses=self.progresses

	table.insert(self.achievements,a)
	progresses[name]=0
	
	self:addChild(a)
	a.center=self
	a.gameCenterID=self.settings.gameCenterPrefix..a.name
	a:setProgress(0)
end

function AchievementCenter:getProgressData()	
	local t={}
	for i,a in ipairs(self.achievements) do
		t[a.name]=a.progress
	end
	return t
end

function AchievementCenter:reportProgress(a,progress)
	if progress>=100 then
		self:emit('achievement.finish',a)
		a.isnew=true
	end
	
	self:emit('achievement.report',a)

	if checkOS('iOS') then
		local id=a.gameCenterID
		if id then			
			gameCenterHelper:reportAchievement(id,progress)
		end
	end
end

function AchievementCenter:clearNewFlag()
	for i, a in pairs(self.achievements) do
		a.isnew=false
	end
end

function AchievementCenter:syncFromGameCenter()	
	-- print('sync achievement from game center')
	local t=gameCenterHelper:getAchievements()
	
	for k,p in pairs(t) do
		local a=self:getByGameCenterID(k)
		-- print(k,p,a)
		if a then
			a:setProgress(p)
		else
			print("WARN: GC achievement not found",k)
		end
	end
end

function AchievementCenter:syncFromData(progresses)
	if not progresses then return end

	self.progresses=progresses
	for k,p in pairs(progresses) do
		local a=self:get(k)
		if a then
			a:setProgress(p)
		else
			print("WARN: achievement not found",k)
		end
	end
end

