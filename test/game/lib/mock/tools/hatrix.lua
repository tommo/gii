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
	'news.get'
}

CLASS: NewsCenter ()


local defaultNewsData={
	
}

--[[
	news format
	1. image url
	2. title
	3. text
	4. target url
]]

function NewsCenter:fetchNews()

	if self.task then
		self.task:stop()
	end
	self.task=MOAIHttpTask.new()
	self.task:setCallback(function(...)
		return self:onNewsCallback(...)
	end)

	local lastId=0
	for i, r in ipairs(self.data) do
		if r.id>lastId then lastId=r.id end
	end

	self.task:httpGet(self.url..'?last='..lastId)

end

function NewsCenter:onNewsCallback(task,code)
	local str=task:getString()
	local result=MOAIJsonParser.decode(str)
	if result and #result >0 then
		for i,r in ipairs(result) do
			r.read=false			
			table.insert(self.data,r)
		end
		self.hasUnread=true
		emitSignal('news.get')
		self:saveData()
	end
end

function NewsCenter:saveData()
	game:saveData('news',self.data)
end

function NewsCenter:updateUnread()
	local unread=false
	for i,n in ipairs(self.data) do
		if not n.read then unread=true break end
	end
	self.hasUnread=unread
end

function NewsCenter:init()
	self.url='www.hatrixgames.com:5000/news'
	-- self.url='192.168.1.99:5000/news'
	self.fetchingImage={}
	self.data=game:loadData('news') or defaultNewsData
	self:updateUnread()
end

function NewsCenter:getNews(id)
	for i,r in pairs(self.data) do
		if r.id==id then return r end
	end
end

function NewsCenter:minNews()
	local v=-1
	for i,r in pairs(self.data) do
		if v==-1 or r.id<v then v=r.id end
	end
	return v
end

function NewsCenter:maxNews()
	local v=0
	for i,r in pairs(self.data) do
		if r.id>v then v=r.id end
	end
	return v
end

function NewsCenter:getLastUnreadId()
	for i,n in ipairs(self.data) do
		if not n.read then return n.id end
	end
	return self:maxNews()
end

function NewsCenter:setRead(id)
	local r=self:getNews(id)
	r.read=true
	self:saveData()
	self:updateUnread()
end

function NewsCenter:fetchNewsImage(id)
		local r=self:getNews(id)
		

		if r.imageDeck then return end
		if self.fetchingImage[r] then return end

		if r.imageData then
			local data=MOAIDataBuffer.base64Decode(r.imageData)
			r.imageDeck=loadRes{
				type='quad',
				texture=data
			}
			
		else
			if r.img then
				self.fetchingImage[r]=true
				RemoteData.fetch(r.img,
				{
						onReady=function(data)
							local quad=data:toGfxQuad()
							r.imageDeck=quad
							self.fetchingImage[r]=nil
						end,
						onFail=function(code)
							self.fetchingImage[r]=nil
						end
					})
			end

		end
		return false
end

function timeSpanName(time,min,max,interval)	
	if time<min then return '<'..min end
	if time>max then return '>'..max end
	local d=time-min
	local i=math.floor(time/interval)
	return string.format('%d-%d',i*interval,(i+1)*interval)
end
