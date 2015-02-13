module 'mock'

registerSignals{
	'async_queue.start',
	'async_queue.stop',
	'async_task.start',
	'async_task.stop',
}

--------------------------------------------------------------------
local _dataCache = {}
local _loadingTasks = {}
local _loadingTaskCount = 0
local _loadedTask = {}

--------------------------------------------------------------------
local _IOThread = MOAITaskThread.new ()
local _IOCoroutine

function getIOThread()
	return _IOThread
end

function startIOCoroutine()
	if _IOCoroutine then return end
	_IOCoroutine = MOAICoroutine.new()
	_IOCoroutine:run( 
	function()
		while true do
			local budget = 0.001
			while budget > 0  do
				local currentPostLoad = table.remove( _loadedTask, 1 )
				if not currentPostLoad then break end
				local t0 = MOAISim.getDeviceTime()
				local buffer, filePath, onLoad, context, result = unpack( currentPostLoad )
				_loadingTaskCount = _loadingTaskCount - 1
				_loadingTasks[ filePath ] = nil
				emitSignal( 'async_task.stop', buffer )
				if _loadingTaskCount == 0 then
					emitSignal( 'async_queue.stop' )
				end
				if result then
					_dataCache[ filePath ] = buffer				
					onLoad( buffer, context )
				end
				local t1 = MOAISim.getDeviceTime()
				local delta = t1 - t0
				budget = budget - delta
			end --end of poll loop			
			coroutine.yield()
		end --end of coroutine loop

	end --end of function
	)

	return _IOCoroutine
end


function loadAsyncData( filePath, onLoad, context )
	if _loadingTasks[ filePath ] then return end
	local buffer = _dataCache[ filePath ]
	if buffer then return onLoad( buffer, context )	end
	_loadingTaskCount = _loadingTaskCount + 1
	if _loadingTaskCount == 1 then
		emitSignal( 'async_queue.start' )
	end
	buffer = MOAIDataBuffer.new()
	emitSignal( 'async_task.start', buffer )
	buffer:loadAsync( filePath, _IOThread, 
		function( result )
			table.insert( _loadedTask, { buffer, filePath, onLoad, context, result } )
		end 
	)
	startIOCoroutine()
	return true
end

function isAsyncBusy()
	return _loadingTaskCount > 0
end
