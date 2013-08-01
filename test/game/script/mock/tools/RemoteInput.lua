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
require 'input'


local function getExIP(target)
	local socket=require 'socket'
	target=target or "74.125.115.104"
	local s = socket.udp()
	s:setpeername(target,80)
	local publicip=s:getsockname()
	s:close()
	return publicip
end

--sender
local defaultPort=3333
local encodeJSON=MOAIJsonParser.encode
local decodeJSON=MOAIJsonParser.decode

function initSender(port)
	local socket=require 'socket'

	port=port or defaultPort
	local evqueue={}

	local function inputCallback(ev,id,x,y,fake)
		if not fake then 
			return table.insert(evqueue,{ev,id,x,y})
		end
	end
	local function timeout(t)
		local tt=os.clock()+t
		while os.clock() < tt do
			coroutine.yield()
		end
	end

	local master=socket.tcp()
	local ip=getExIP('192.168.1.1')
	local server=socket.bind(ip,port)
	assert(server)	
	print('Listening:', ip, port)
	server:settimeout(0)
	addTouchListener('remoteInputSender',inputCallback)
	local state
	local thread=MOAICoroutine.new()
	thread:run(function()

		local client
				
		while true do --start of FSM
			state='wait'

			while state=='wait' do --wait for connection
				client=server:accept()
				if client then 
					state='run'
					-- client:send('ok')
					client:settimeout(0)
					print('Client connected!',client:getsockname())
				end
				timeout(0.1)
				coroutine.yield()
			end

			--flush queue
			evqueue={}

			while state=='run' do -- main loop
				coroutine.yield()
				--flush queue into client
				local line,err=client:receive()
				if line then print(line) end
				if evqueue[1] then
					for i,e in ipairs(evqueue) do
						local t=encodeJSON(e)
						-- print('sending',t)
						client:send(t..'\n')
					end
					evqueue={}
				end
			end			

			client:shutdown()

		end
	end)

	return {
		reset=function()
			state='wait'
		end
	}
end



--receiver

function	initReceiver(ip,port)
	local socket=require 'socket'
	local tcp=socket.tcp()
	port=port or defaultPort
	assert(ip)
	print(socket._VERSION)
	tcp:settimeout(1)
	local thread=MOAICoroutine.new()
	local function timeout(t)
		local tt=os.clock()+t
		while os.clock() < tt do
			coroutine.yield()
		end
	end
	thread:run(function()
		local client
		
		local state='connect'
		print('connecting',ip,port)
		while state=='connect' do
			
			local succ,err=tcp:connect(ip,port)
			if succ then 
				state='run'
				client=tcp
				print('Server connected',client:getsockname())
				break
			end
			print("failed, retry in 1sec",err)
			timeout(1)	
		end
		tcp:settimeout(0)
		while state=='run' do
			coroutine.yield()
			local data=client:receive()
			if data then
				local t=decodeJSON(data)
				local ev,id,x,y=unpack(t)
				_sendTouchEvent(ev,id,x,y,true)
			end
		end
	end
	)
end


