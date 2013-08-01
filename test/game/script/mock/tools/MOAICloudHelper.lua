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

--BIG TODO
local hmac=require'crypto.hmac'


local gsub,format,byte=string.gsub,string.format,string.byte
local function escape_gsubfunc(c)
	return format( "%%%02X", byte ( c ))    
end
local function urlencode(str)
	return  gsub ( str, "([^%w ._])", escape_gsubfunc)
end

local function escape ( str )
	if str==true then return 'true' end
	if str==false then return 'false' end
    
    str = gsub ( str, " ", "+" )
    return str
end

----------------------------------------------------------------
local function encodeParam ( t )

	local s = ""
	
	for k,v in pairs ( t ) do
		s = s .. "&" .. escape ( k ) .. "=" .. escape ( v )
	end
	
	return string.sub ( s, 2 ) -- remove first '&'
end

local function encodeParamSignature ( t )

	local s = ""
	local parts={}
	local m=1
	for k,v in pairs ( t ) do
		parts[m]=escape ( k ) 
		m=m+1
	end
	table.sort(parts)

	for i,k in ipairs(parts) do
		s=s..'&'..urlencode(escape(k))..'='..urlencode(escape(t[k]))
	end
	return string.sub ( s, 2 ) -- remove first '&'
end

---test moaicloud
CLASS: httpTaskResultHandler ()
function httpTaskResultHandler:wait()
	while not self.done do coroutine.yield() end
	return self.responseCode
end

local function httpTaskCallback(task,responseCode)
	local str=task:getString()
	local result=MOAIJsonParser.decode(str)
	local handler=task.handler
	
	handler.done=true
	handler.responseCode=responseCode
	handler.result=result
	handler.text=str

	if task.caller.onResponse then
		return task.caller:onResponse(responseCode,result,str)
	end
end

--------------------------------------------------------------------
CLASS: MOAICloudCaller()

function MOAICloudCaller:__init( data )
	self.urlbase    = data.urlbase or 'http://services.moaicloud.com/'..data.path
	self.method     = data.method or 'get'
	self.defaultArg = data.defaultArg
	self.header     = data.header
	self.async      = data.async or true
	self.clientKey  = data.clientKey
	self.needSign   = data.needSign
	self.onResponse = data.onResponse
	self.secret     = data.secret
end

function MOAICloudCaller:call(data,forceMethod,forceSync)
	local url=self.urlbase

	local task=MOAIHttpTask.new()
	task.caller=self
	task.handler=httpTaskResultHandler()

	task:setCallback(httpTaskCallback)
	task:setUserAgent('Moai')
	local method=forceMethod or self.method or 'get'

	if method=='post' then
		if data then
			task:setBody(MOAIJsonParser.encode ( data ) )
		end
		task:setUrl(url)	
	else
		if data and next(data) then
			url=url..'?'..encodeParam(data)
		end
		print(url)
		task:setUrl(url)
	end

	if self.header then
		for k,v in pairs(self.header) do
			task:setHeader(k,v)
		end		
	end

	if self.clientKey then
		task:setHeader('x-clientkey',self.clientKey)
	end

	if self.needSign then
		local src=method:upper()..'&'
			..urlencode(self.urlbase:lower())..'&'
			..urlencode(encodeParamSignature(data))
		local sig=hmac.digest('sha256',src,self.secret,true)
		sig=MOAIDataBuffer.base64Encode(sig)
		task:setHeader('signature',sig)
		print('sig-->')
		print(src)
		print(sig)
	end

	if not forceSync and self.async then 
		task:performAsync()
	else
		task:performSync()
	end

	return task.handler
end

