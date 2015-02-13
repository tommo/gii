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

CLASS: RemoteData ()
	

registerSignals{
	'remotedata.ready',
	'remotedata.fail',
}

local remoteDataCallback=function(task,code)

	if code~=200 then
		return task.owner:_onFail(code)
	else		
		return task.owner:_onReady(task:getString())
	end

end

function RemoteData.fetch(url,option)
	local data=RemoteData{
		url=url,
		option=option or {}
	}
	return data:doFetch()
end

function RemoteData:doFetch()
	local url,option=self.url,self.option

	local task=MOAIHttpTask.new()
	local method=option and option.method
	
	task.owner=self
	task:setCallback(remoteDataCallback)

	if method=='post' then
		local data=option and option.data
		task:httpPost(url,data)
	else
		task:httpGet(url)
	end
	return self
end

function RemoteData:isDone()
	return self.done
end

function RemoteData:refetch()
	self.done=false
	self.data=nil
	self.errorCode=nil
	self:doFetch()
end

function RemoteData:toString()
	return self.data
end

function RemoteData:toImage()
	local buf=MOAIDataBuffer.new()
	buf:setString(self.data)
	local img=MOAIImage.new()
	img:load(buf)
	return img
end

function RemoteData:toGfxQuad()
	local buf=MOAIDataBuffer.new()
	buf:setString(self.data)
	
	return loadRes{
		type='quad',
		texture=buf
	}

end

function RemoteData:toTexture()
	local buf=MOAIDataBuffer.new()
	buf:setString(self.data)
	local tex=MOAITexture.new()
	tex:load(buf)
	return tex
end


function RemoteData:_onReady(data)
	self.data=data
	self.done=true
	local option=self.option
	if option.onReady then return option.onReady(self) end
	emitSignal('remotedata.ready',self,data)
end

function RemoteData:_onFail(code)
	local option=self.option
	self.errorCode=code
	self.done=true
	if option.onFail then return option.onFail(self) end
	emitSignal('remotedata.fail',self,code)
end


