module 'mock'

-- MOAIFlurry = rawget( _G, 'MOAIFlurry' ) or false
-- local MOAIFlurryReady = false
-- local AnalyticEnabled = false

-- Analytic = {}

-- function Analytic:enable( e )
-- 	AnalyticEnabled = e
-- end

-- function Analytic:start( id )
-- 	if not AnalyticEnabled then return end
-- 	if MOAIFlurry then
-- 		MOAIFlurry.startSession( id )
-- 		MOAIFlurry.logEvent("Startup")
-- 		MOAIFlurryReady = true
-- 	end
-- end

-- function Analytic:log( event, data )
-- 	if not AnalyticEnabled then return end
-- 	if MOAIFlurry then
-- 		return MOAIFlurry.logEvent( event, data )
-- 	end
-- end

CLASS: AnalyticHelper ()
	:MODEL{}


function AnalyticHelper:init( option )
	self.initOptions = option or {}
	self:onInit( option )
end

function AnalyticHelper:sync()
end

function AnalyticHelper:initCache()
end

function AnalyticHelper:log( event, data )
end
