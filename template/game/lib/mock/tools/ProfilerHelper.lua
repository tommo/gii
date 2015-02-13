module 'mock'

local ProFi
function startProfiler()
	if not ProFi then
		ProFi = require 'mock.tools.ProFi'
	end
	ProFi:reset()
	ProFi:start()	
end

function stopProfiler( outputFile )
	if ProFi then
		ProFi:stop()
		if outputFile then
			ProFi:writeReport( outputFile )
		end
	end
end

function runProfiler( duration, outputPath )
	duration = duration or 10
	printf('start profiling for %d secs', duration)
	startProfiler()
	laterCall(
		duration,
		function()
			print('stop profiling')
			mock.stopProfiler( outputPath or 'profiler.log' )
		end
	)
end