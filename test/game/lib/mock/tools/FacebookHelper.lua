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

--TODO
CLASS: FacebookHelper ()

local function facebookCallbackLoginOK()

end

local function facebookCallbackLoginFail()

end

function FacebookHelper:init(settings)
	local appID=settings.appID
	print('initFacebook',appID)

	self.settings=settings

	MOAIFacebook.init(appID)
	print(MOAIFacebook.SESSION_DID_LOGIN)
	MOAIFacebook.setListener(MOAIFacebook.SESSION_DID_LOGIN,
		function()
			return self:onLogin(true)
		end)

	MOAIFacebook.setListener(MOAIFacebook.SESSION_DID_NOT_LOGIN,
		function()
			return self:onLogin(false)
		end)

	MOAIFacebook.setListener(MOAIFacebook.DIALOG_DID_COMPLETE,
		function()
			return self:onDialogComlete(true)
		end)

	MOAIFacebook.setListener(MOAIFacebook.DIALOG_DID_NOT_COMPLETE,
		function()
			return self:onDialogComlete(false)
		end)
end

function FacebookHelper:checkLogin()

	self.token=self.token or MOAIFacebook.getToken()
	if self.token or self.logging then return end
	self.logging=true
	MOAIFacebook.login()
end

function FacebookHelper:onLogin(loggedIn)
	print('loggedin:',loggedIn)	
	self.logging=false
	if loggedIn then
		self.token=MOAIFacebook.getToken()
		print('token got:',self.token)
	end
end

function FacebookHelper:onDialogComlete(complete)
	print('dialogComplete',complete)
end

function FacebookHelper:post(data)
	self:checkLogin()
	-- print('publishToFeed')
	threadAction(function()
		while not self.token do
			coroutine.yield()
		end

		MOAIFacebook.publishToFeed(
			data.link,
			data.picture,
			data.name,
			data.caption,
			data.description,
			data.message)
	end)
end
