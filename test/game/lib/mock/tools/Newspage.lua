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
CLASS: Newspage ( Object )

function Newspage:onLoad()
	self.frame=self:addProp{
		deck=res.title['news_frame'],
		transform={
			loc={0,10},
			scl={1,5}
		}
	}

	self.title=self:addTextBox{
		rect={rectCenter(0,20,190,50)},
		style=res.styles['news_title'],
		align='center',
		text='THIS IS A NEWS'
	}

	self.text=self:addTextBox{
		rect={rectCenterTop(0,10,210,-180)},
		style=res.styles['news_body'],
		align='left',

		text=[[news text]]
	}

	self.buttonImage=self:addChild(TouchButton{
		deck=res.title['newsimg'],
		transform={
			scl={1.2,1.2},
			loc={0,110}
		},
		sound='button.enter'
	})

	local y=-188
	self.buttonPrev=self:addChild(TouchButton{
		deckPress=res.title['news_prev'],
		deckTransform={
			scl={.5,.5},
			loc={-73,y}
		}
	})

	self.buttonExit=self:addChild(TouchButton{
		deckPress=res.title['news_close'],
		deckTransform={
			scl={.5,.5},
			loc={-2,y}
		}
	})
	self.buttonNext=self:addChild(TouchButton{
		deckPress=res.title['news_next'],
		deckTransform={
			scl={.5,.5},
			loc={71,y}
		}
	})


	self.readingId=false

end

function Newspage:updateView()
	local news=player.newsCenter:getNews(self.readingId)
	if not news then return end
	self.title:setString(news.title)
	self.text:setString(news.text)
	self.targetUrl=news.url
	
	self.buttonImage.prop:setDeck(res.title['newsimg'])
	self.buttonImage.prop:setScl(1.2,1.2)
	self.buttonImage.prop:forceUpdate()

	player.newsCenter:setRead(self.readingId)
	
	self.imgThread=self:addCoroutine('threadImg')

end

function Newspage:threadImg()
	local news=player.newsCenter:getNews(self.readingId)
	player.newsCenter:fetchNewsImage(self.readingId)
	while true do
		local imageDeck=news.imageDeck 
		if imageDeck==false then 
			return 
		elseif imageDeck then
			self.buttonImage.prop:setDeck(imageDeck)
			self.buttonImage.prop:setScl(.5,.5)
			self.buttonImage.prop:forceUpdate()
			return
		end
		coroutine.yield()
	end
end

function Newspage:showNext()
	if not self.readingId then
		self.readingId=player.newsCenter:getLastUnreadId()
	else
		self.readingId=math.min(self.readingId+1,player.newsCenter:maxNews())
	end
	self:updateView()
end

function Newspage:showPrev()
	self.readingId=math.min(self.readingId-1,player.newsCenter:minNews())
	self:updateView()
end

function Newspage:onThread()
	self:showNext()
	while true do
		local b=self:waitSignal('button.click')

		if b==self.buttonImage then
			-- print('opening url',self.targetUrl)
			openURLInBrowser(self.targetUrl)
		elseif b==self.buttonPrev then
			self:showPrev()
		elseif b==self.buttonNext then
			self:showNext()
		elseif b==self.buttonExit then
			self:setState'done'
			break
		end

	end
	-- self:wait(self:seekColor(1,1,1,0,0.5))
	self:destroy()
end
