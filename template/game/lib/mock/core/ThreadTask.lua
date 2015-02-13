module 'mock'

--------------------------------------------------------------------
CLASS: ThreadTaskManager ()
	:MODEL{}

local _mgr = false
function getThreadTaskManager()
	if _mgr then return _mgr end
	_mgr = ThreadTaskManager()
	return _mgr
end

function isThreadTaskBusy( queueName )
	return getThreadTaskManager():isBusy( queueName )
end

function getThreadTaskQueue( queueName )
	queueName = queueName or getThreadTaskManager().defaultQueue
	return getThreadTaskManager():getQueue( queueName )
end

function getThreadTaskProgress( queueName )
	queueName = queueName or getThreadTaskManager().defaultQueue
	local q = getThreadTaskManager():getQueue( queueName, false )
	if not q then return 1 end
	return q:getProgress()
end

function ThreadTaskManager:__init()
	self.queues = {}
	self.defaultQueue = 'main'
end

function ThreadTaskManager:getQueue( name, createIfNotExist )
	local q = self.queues[ name ]
	if not q and ( createIfNotExist ~= false ) then
		q = ThreadTaskQueue()
		self.queues[ name ] = q
		q.manager = self
	end
	return q
end

function ThreadTaskManager:getDefaultQueue( createIfNotExist )
	return self:getQueue( self.defaultQueue, createIfNotExist )
end

function ThreadTaskManager:setDefaultQueue( name )
	self.defaultQueue = name or 'main'
end

function ThreadTaskManager:pushTask( queue, t )
	queue = queue or self.defaultQueue
	local q = self:getQueue( queue )
	q:pushTask( t )
	return t
end

function ThreadTaskManager:isBusy( queueName )
	local q = self:getQueue( queueName or self.defaultQueue, false )
	if not q then return false end
	return q:isBusy()
end

function ThreadTaskManager:isAnyBusy()
	return self.busy
end

--------------------------------------------------------------------
CLASS: ThreadTaskQueue ()
	:MODEL{}
function ThreadTaskQueue:__init()
	
	self.pending = {}
	self.activeTask = false
	self.taskSize  = 0
	self.taskCount = 0
	self.totalTaskSize  = 0
	self.totalTaskCount = 0
	self.thread = false
	self.coro = MOAICoroutine.new()

end

function ThreadTaskQueue:getThread()
	if not self.thread then
		self.thread = MOAITaskThread.new()
	end
	return self.thread
end

function ThreadTaskQueue:resetProgress()
	self.totalTaskSize  = self.taskSize
	self.totalTaskCount = self.taskCount
end

function ThreadTaskQueue:getProgress()
	if self.totalTaskSize <= 0 then return 1 end
	return 1 - ( self.taskSize / self.totalTaskSize )
end

function ThreadTaskQueue:pushTask( task )
	table.insert( self.pending, task )
	self.taskSize  = self.taskSize + task:getTaskSize()
	self.taskCount = self.taskCount + 1
	self.totalTaskSize  = self.totalTaskSize + task:getTaskSize()
	self.totalTaskCount = self.totalTaskCount + 1
	task.queue = self
	if not self.activeTask then
		return self:processNext()
	end
end

function ThreadTaskQueue:processNext()
	local t = table.remove( self.pending, 1 )
	if t then
		_stat( 'Processing task', t:toString() )
		self.activeTask = t
		t.execTime0 = os.clock()
		t:onExec( self )
		_stat( 'task in execution now' )
		return t
	else
		--no more task, stop the thread
		_stat( 'Thread empty, now stopping....' )
		self.thread:stop()
		self.thread = nil
	end
end

function ThreadTaskQueue:isBusy()
	return ( self.activeTask and true ) or ( next( self.pending ) ~= nil )
end

function ThreadTaskQueue:notifyCompletion( task )
	assert( self.activeTask == task )
	_stat( 'Task completed', task:toString() )
	self.activeTask = false
	self.taskSize = self.taskSize - task:getTaskSize()
	self.taskCount = self.taskCount - 1
	task.execTime1 = os.clock()
	self:processNext()
end

function ThreadTaskQueue:notifyFail( task ) --TODO: allow interrupt on error?
	assert( self.activeTask == task )
	_stat( 'Task failed', task:toString() )
	self.activeTask = false
	self.taskSize = self.taskSize - task:getTaskSize()
	self.taskCount = self.taskCount - 1
	task.execTime1 = os.clock()
	self:processNext()
end

--------------------------------------------------------------------
CLASS: ThreadTask ()
	:MODEL{}

function ThreadTask:getDefaultQueue()
	return nil
end

function ThreadTask:start( queueName )
	getThreadTaskManager():pushTask( queueName or self:getDefaultQueue(), self )
end

function ThreadTask:toString()
	return '<unknown>'
end

function ThreadTask:complete( ... )
	if self.queue then 
		self.queue:notifyCompletion( self )		
	end
	return self:onComplete( ... )
end

function ThreadTask:fail( ... )
	if self.queue then 
		self.queue:notifyFail( self )		
	end
	return self:onFail( ... )
end

function ThreadTask:onExec( queue )
end

function ThreadTask:onComplete( ... )
end

function ThreadTask:onFail( ... )
end

function ThreadTask:getTaskSize() --for progress calculation
	return 1
end

function ThreadTask:getTimeElapsed()	
	local t0 = self.execTime0 or 0
	local t1 = self.execTime1 or os.clock()
	return t1 - t0
end



