module 'mock'
local function hasItem(t, v)
	for _, i in ipairs(t) do
		if i==v then return true end
	end
	return false
end

CLASS: InputEventRecorder ()
function InputEventRecorder:__init(option)
	self.thread=false
	self.recording=false
	option=option or {}
	self.filter=option.filter or {'mouse','keyboard','touch','compass','level','joystick'}
	self.interval=option.interval
	self.events={}
	self.eventCount=0	
	self.lasttime=0
	self.filename=option.filename or 'input_record.json'
end

local clock=MOAISim.getElapsedTime
function InputEventRecorder:pushEvent(tag, ...)
	local time=math.floor(clock()*1000-self.entryTime)
	self.eventCount=self.eventCount+1
	self.events[self.eventCount]={tag,time,...}
end

function InputEventRecorder:start(recordtime, autosave)
	assert( not self.recording, 'already recording')
	self.recording=true
	print("recording start")
	
	local function _record(tag)
		return function(...) return self:pushEvent(tag,...) end
	end

	if recordtime then
		laterCall(recordtime, 
			function() 
				self:stop()
				if autosave then self:save() end
			end
		)
	end
	self.entryTime=clock()*1000
	
	local filter=self.filter
	if hasItem(filter, 'mouse') then
		addMouseListener(self, _record('m'))
	end
	if hasItem(filter, 'keyboard') then
		addKeyboardListener(self, _record('k'))
	end
	if hasItem(filter, 'touch') then
		addTouchListener(self, _record('t'))
	end
	if hasItem(filter, 'compass') then
		--TODO
		-- addCompassListener(self, _record('c'))
	end
	if hasItem(filter, 'level') then
		addMotionListener(self, _record('l'))
	end
	if hasItem(filter, 'joystick') then
		--TODO
		-- addJoystickListener(self, _record('j'))
	end

end

function InputEventRecorder:stop()
	print("recording stopped")
	self.recording=false
	removeKeyboardListener(self)
	removeMouseListener(self)
	removeTouchListener(self)
	-- removeCompassListener(self)
	removeMotionListener(self)
	-- removeJoystickListener(self)
end

function InputEventRecorder:save(filename)
	-- 	save
	filename=filename or self.filename
	local f=io.open(filename,'w')
	if not f then error('cannot open file for save:'..filename) end
	f:write(MOAIJsonParser.encode(self.events))
	f:close()
	print('input events written:'..filename)
end


CLASS: InputEventPlayer ()
function InputEventPlayer:load(file)
	local f=io.open(file,'r')
	if not f then return false end
	local data=MOAIJsonParser.decode(f:read())
	self.filename=file
	f:close()
	if data then
		self.data=data
		self.playPos=1
		self.dataSize=#data
	else
		self.data=false
		return false
	end
	return true
end

function InputEventPlayer:play(speed)
	if not self.data then return false end
	speed=speed or 1
	self.playPos=1
	local thread=MOAICoroutine.new()
	self.thread=thread
	self.entryTime=clock()*1000

	thread:run(function()
		print('start play input record:',self.filename)

		while true do
			if not self:playOneFrame(speed) then break end
			coroutine.yield()
		end
		print('play done!')
		self.thread=false
	end)

end

function InputEventPlayer:playOneFrame(speed)
	if self.playPos>self.dataSize then return false end
	local t=clock()*1000-self.entryTime
	t=t * speed
	local data=self.data
	while true do
		local frame=data[self.playPos]
		if not frame then return false end
		local tag,time,a,b,c,d,e,f,g=unpack(frame)
		if t>=time then
			if tag=='m' then
				_sendMouseEvent(a,b,c,d,e,f,g)
			elseif tag=='k' then
				_sendKeyEvent(a,b,c,d,e,f,g)
			elseif tag=='t' then
				_sendTouchEvent(a,b,c,d,e,f,g)
			elseif tag=='l' then
				_sendMotionEvent(a,b,c,d,e,f,g)
			elseif tag=='c' then
				-- _sendCompassEvent(a,b,c,d,e,f,g) TODO
			elseif tag=='j' then
				-- _sendJoystickEvent(a,b,c,d,e,f,g) TODO
			end
			self.playPos=self.playPos+1
		else
			break
		end
	end	
	return true
end

function InputEventPlayer:stop()
	if self.thread then self.thread:stop() self.thread=false end
end

function playOrRecordInputEvent(filename, length, option)
	option= option or {}
	local f=io.open(filename)
	if f then
		f:close()
		local player=InputEventPlayer()
		player:load(filename)
		player:play(option.speed)
	else
		length=length or 5
		local r=InputEventRecorder{
			filename=filename,
			filter=option.filter,
		}
		r:start(length, true)
	end
end

