module 'mock'
--------------------------------------------------------------------
CLASS:  ThreadDataTask ( ThreadTask )
	:MODEL{}

function ThreadDataTask:__init( filename )
	self.filename = filename
end

function ThreadDataTask:onExec( queue )
	if not self.filename then return false end
	local buffer = MOAIDataBuffer.new()
	buffer:loadAsync(
		self.filename,
		queue:getThread(),
		function( result )
			return self:complete( result )
		end
	)
	return true
end

